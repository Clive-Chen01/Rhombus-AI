import regex as re
import pandas as pd
import numpy as np

from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services.file_io import load_to_df
from .services.llm_client import compile_regex_plan
from .serializers import UploadResponse

TMP_DIR = Path(__file__).resolve().parent / "storage"

_state = {"df": None, "filename": None}


@csrf_exempt
@api_view(["POST"])
def upload_file(request):
    f = request.FILES.get("file")
    if not f:
        return Response({"error": "Missing file"}, status=status.HTTP_400_BAD_REQUEST)
    tmp = TMP_DIR / f.name
    with tmp.open("wb+") as dst:
        for chunk in f.chunks():
            dst.write(chunk)
    loaded = load_to_df(tmp)
    _state["df"] = loaded.df
    _state["filename"] = loaded.name


    payload = {
        "columns": list(loaded.df.columns),
        "data": loaded.df.head(100).fillna("").values.tolist(),
        "filename": loaded.name
    }
    return Response(UploadResponse(payload).data)


FLAG_MAP = {
    "IGNORECASE": re.IGNORECASE,
    "MULTILINE": re.MULTILINE,
    "DOTALL": re.DOTALL,
    "UNICODE": re.UNICODE,
}

def _compile_regex_safe(pattern: str, flags_list: list[str]):
    flags = 0
    for k in flags_list or []:
        flags |= FLAG_MAP.get(k.upper(), 0)
    return re.compile(pattern, flags)

def _to_py_backrefs(template: str) -> str:
    return re.sub(r"\$(\d+)", r"\\g<\1>", template)

def _apply_regex_once(df: pd.DataFrame, pat_obj, intent: str, candidate, columns: list[str] | None):
    new_df = df.copy()
    target_cols = columns or list(new_df.columns)
    target_cols = [c for c in target_cols if c in new_df.columns]
    if not target_cols:
        return new_df, {"updated_rows": 0, "updated_cells": 0, "target_cols": []}

    if intent in ("replace","mask"):
        repl_template = _to_py_backrefs(candidate.replacement or "")
        def do_sub(x: str):
            try: return pat_obj.sub(repl_template, x, concurrent=True)
            except re.TimeoutError: return x
    elif intent == "normalize":
        fmt = _to_py_backrefs(candidate.format or "")
        def do_sub(x: str):
            try: return pat_obj.sub(fmt, x, concurrent=True)
            except re.TimeoutError: return x
    else:
        def do_sub(x: str): return x

    updated_cells = 0
    for col in target_cols:
        before = new_df[col].astype(str).fillna("")
        after = before.map(do_sub)
        changed = (before != after)
        updated_cells += int(changed.sum())
        new_df[col] = after

    changed_row_mask = np.zeros(len(new_df), dtype=bool)
    for col in target_cols:
        changed_row_mask |= (df[col].astype(str).fillna("") != new_df[col].astype(str).fillna("")).to_numpy()
    updated_rows = int(changed_row_mask.sum())
    return new_df, {"updated_rows": updated_rows, "updated_cells": updated_cells, "target_cols": target_cols}

def _score_candidate(stats: dict, total_cells: int) -> float:
    u = stats.get("updated_cells", 0)
    if u <= 0: return -1.0
    coverage = u / max(1, total_cells)
    penalty = 0.0
    if coverage > 0.8: penalty = (coverage - 0.8) * 0.5 * u
    return u - penalty

@csrf_exempt
@api_view(["POST"])
def transform_data(request):
    data = request.data or {}
    prompt = data.get("prompt", "")
    if not isinstance(prompt, str) or not prompt.strip():
        return Response({"error": "prompt is required"}, status=400)

    df = _state.get("df")
    if df is None:
        return Response({"error": "Upload a file first."}, status=400)

    print(f"[/api/transform] received prompt: {prompt}")

    try:
        plan = compile_regex_plan(nl=prompt, columns=[], k=3)
    except Exception as e:
        print(f"[/api/transform] LLM call failed: {e}")
        return Response({"error": f"compile failed: {str(e)}"}, status=502)

    print(f"[/api/transform] LLM plan -> is_table_op={plan.is_table_op}, intent={plan.intent}, candidates={len(plan.candidates)}")
    if not plan.is_table_op:
        print(f"[/api/transform] invalid input: {plan.reason}")
        return Response({"error": "invalid_input", "reason": plan.reason or "输入与表格文本处理无关"}, status=422)

    if not plan.candidates:
        print("[/api/transform] no regex candidates from LLM")
        return Response({"error": "no valid regex candidate produced"}, status=422)

    candidates_evals = []
    cols_to_use = plan.columns or list(df.columns)
    total_cells = len(df) * max(1, len(cols_to_use))

    for idx, cand in enumerate(plan.candidates, start=1):
        try:
            pat_obj = _compile_regex_safe(cand.pattern, cand.flags)
        except Exception as ce:
            print(f"[/api/transform] candidate#{idx} compile failed: {cand.pattern} | {ce}")
            continue

        if plan.intent in ("replace","mask") and not cand.replacement:
            print(f"[/api/transform] candidate#{idx} skipped: missing replacement for intent={plan.intent}")
            continue
        if plan.intent == "normalize" and not cand.format:
            print(f"[/api/transform] candidate#{idx} skipped: missing format for normalize")
            continue

        df_try, stats = _apply_regex_once(df, pat_obj, plan.intent, cand, cols_to_use)
        score = _score_candidate(stats, total_cells)

        candidates_evals.append({
            "idx": idx,
            "pattern": cand.pattern,
            "flags": cand.flags,
            "explanation": cand.explanation,
            "risk_notes": cand.risk_notes,
            "replacement": cand.replacement,
            "format": cand.format,
            "score": score,
            "stats": stats,
            "df": df_try
        })
        print(f"[/api/transform] candidate#{idx} score={score} stats={stats} pattern={cand.pattern}")

    if not candidates_evals:
        print("[/api/transform] all candidates invalid after compile/validation")
        return Response({"error": "no valid regex candidate produced"}, status=422)

    candidates_evals.sort(key=lambda x: x["score"], reverse=True)
    chosen = candidates_evals[0]
    df2 = chosen["df"]
    _state["df"] = df2

    payload = {
        "prompt": prompt,
        "intent": plan.intent,
        "pattern": chosen["pattern"],
        "flags": chosen["flags"],
        "columns": cols_to_use,
        "replacement": chosen.get("replacement"),
        "format": chosen.get("format"),
        "assumptions": plan.assumptions,
        "stats": {
            "updated_rows": chosen["stats"]["updated_rows"],
            "updated_cells": chosen["stats"]["updated_cells"]
        },
        "headers": list(df2.columns),
        "data": df2.head(100).fillna("").values.tolist(),
        "candidates_debug": [
            {
                "pattern": c["pattern"],
                "flags": c["flags"],
                "replacement": c["replacement"],
                "format": c["format"],
                "score": c["score"],
                "stats": c["stats"]
            } for c in candidates_evals
        ]
    }

    pp = dict(payload); pp.pop("data", None)
    print(f"[/api/transform] 200 response (preview): {pp}")

    return Response(payload, status=200)