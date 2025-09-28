# services/llm_client.py
from __future__ import annotations
import json
import os
from typing import List, Optional
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from ollama import Client

# === Set Up ===
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "https://ollama.com")
OLLAMA_API_KEY = os.getenv(
    "OLLAMA_API_KEY",
    "d9d2d8108eca4c4a86224dee96852708.OKPxaPg_1hsPepxTgiWDVGQr"
)
MODEL_NAME = os.getenv("OLLAMA_MODEL", "gpt-oss:120b")
TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))

# === Initialize Client ===
client = Client(
    host=OLLAMA_HOST,
    headers={'Authorization': f'Bearer {OLLAMA_API_KEY}'}
)

SYSTEM = """You are a planner that converts natural-language spreadsheet/text-column instructions
into an executable plan for Python 'regex' library.

Output STRICT JSON with this schema:
{
    "is_table_op": boolean,
    "intent": "replace" | "extract" | "mask" | "normalize" | "split" | "none",
    "reason": string,
    "columns": string[] | [],
    "candidates": [
        {
        "engine": "regex",
        "pattern": string,
        "flags": string[],                 // e.g. ["UNICODE","IGNORECASE"]
        "replacement": string | null,      // REQUIRED when intent in ["replace","mask"]
        "format": string | null,           // REQUIRED when intent == "normalize" (may use $1,$2... groups)
        "explanation": string,
        "risk_notes": string[]
        }
    ],
    "assumptions": string[]
}

Rules:
- JSON ONLY (no markdown or comments).
- Decide intent yourself. If not a table/text-column task, set is_table_op=false, intent="none", reason, candidates=[].
- Avoid catastrophic backtracking ((.+)+, (.*)+, nested star/plus).
- Prefer Unicode-aware classes; Python 'regex' supports \\p{...}.
- If user didn't specify columns, set columns=[] (caller may decide).
- Replacement/format policy:
  * For replace/mask: provide a literal "replacement". It may contain backreferences like $1, $2...
  * For normalize: provide a "format" string that uses captured groups (e.g., "+61 $1 $2 $3").
- Provide 1–3 candidates that meaningfully differ.
"""

USER_TEMPLATE = """Natural language intent:
{nl}

Known column names:
{columns}

Constraints:
- Return 1 to {k} candidates.
- Ensure "replacement" is present for replace/mask, or "format" is present for normalize.
- Backreferences must use $1, $2, ... (the caller will convert to Python syntax).
"""

class RegexCandidate(BaseModel):
    engine: str = Field(pattern="^regex$")
    pattern: str
    flags: List[str] = []
    replacement: Optional[str] = None
    format: Optional[str] = None
    explanation: str
    risk_notes: List[str] = []

class CompilePlan(BaseModel):
    is_table_op: bool
    intent: str = Field(pattern="^(replace|extract|mask|normalize|split|none)$")
    reason: str
    columns: List[str] = []
    candidates: List[RegexCandidate] = []
    assumptions: List[str] = []

class LLMBadJSON(Exception): ...
class LLMCallError(Exception): ...

def _chat_once(prompt: str) -> str:
    try:
        res = client.chat(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": prompt}
            ],
            stream=False,
            options={"temperature": TEMPERATURE}
        )
    except Exception as e:
        raise LLMCallError(str(e))
    text = (res.get("message") or {}).get("content", "")
    if not text:
        raise LLMCallError("empty response from model")
    return text

@retry(
    retry=retry_if_exception_type((LLMBadJSON, ValidationError, LLMCallError)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=6)
)
def compile_regex_plan(nl: str, columns: Optional[list[str]] = None, k: int = 3) -> CompilePlan:
    prompt = USER_TEMPLATE.format(
        nl=nl.strip(),
        columns=json.dumps(columns or [], ensure_ascii=False),
        k=max(1, min(int(k or 1), 3))
    )
    raw = _chat_once(prompt).strip()
    try:
        obj = json.loads(raw)
    except json.JSONDecodeError:
        try:
            s = raw.index("{"); e = raw.rindex("}") + 1
            obj = json.loads(raw[s:e])
        except Exception as ex:
            raise LLMBadJSON(f"Cannot parse JSON: {raw[:300]}...") from ex

    plan = CompilePlan.model_validate(obj)

    if plan.is_table_op:
        for c in plan.candidates:
            if c.engine != "regex":
                raise LLMBadJSON("Only 'regex' engine is supported")
            if plan.intent in ("replace","mask") and not c.replacement:
                raise LLMBadJSON("replacement is required for replace/mask")
            if plan.intent == "normalize" and not c.format:
                raise LLMBadJSON("format is required for normalize")
    return plan
