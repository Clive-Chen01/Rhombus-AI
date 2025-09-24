from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .services.file_io import load_to_df
from .services.transformers import regex_replace, normalize_au_phone, normalize_dates
from .services.llm_regex import nl_to_regex
from .serializers import UploadResponse, TransformRequest, TransformResponse


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


@csrf_exempt
@api_view(["POST"])
def transform_data(request):
    if _state["df"] is None:
        return Response({"error": "Upload a file first."}, status=status.HTTP_400_BAD_REQUEST)


    s = TransformRequest(data=request.data)
    s.is_valid(raise_exception=True)
    nl = s.validated_data["natural_language"]
    replacement = s.validated_data["replacement"]
    columns = s.validated_data.get("columns")
    apply_phone = s.validated_data.get("apply_phone_normalization", False)
    apply_date = s.validated_data.get("apply_date_normalization", False)


    pattern, explanation = nl_to_regex(nl)


    df = _state["df"]
    df2 = regex_replace(df, pattern, replacement, columns)


    if apply_phone:
        df2 = normalize_au_phone(df2, columns)
    if apply_date:
        df2 = normalize_dates(df2, columns=columns)


    payload = {
        "pattern": pattern,
        "explanation": explanation,
        "columns": columns or [],
        "data": df2.head(100).fillna("").values.tolist()
    }
    return Response(TransformResponse(payload).data)


@csrf_exempt
@api_view(["POST"])
def llm_preview(request):
    body = request.data or {}
    nl = body.get("natural_language", "")
    pattern, explanation = nl_to_regex(nl)
    return Response({"pattern": pattern, "explanation": explanation})