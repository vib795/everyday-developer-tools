import json

from fastapi import APIRouter
from jsonpath_ng.ext import parse as jsonpath_parse

from ..schemas.convert import (
    CurlConvertRequest,
    CurlConvertResponse,
    FormatConvertRequest,
    FormatConvertResponse,
    JsonPathRequest,
    JsonPathResponse,
)
from ..services.curl_parse import convert_curl
from ..services.format_convert import dump, parse

router = APIRouter(prefix="/api/convert", tags=["convert"])


@router.post("/format", response_model=FormatConvertResponse)
def format_convert(payload: FormatConvertRequest) -> FormatConvertResponse:
    try:
        data = parse(payload.text, payload.source)
        out = dump(data, payload.target)
        return FormatConvertResponse(output=out)
    except Exception as e:  # noqa: BLE001
        return FormatConvertResponse(output="", error=f"{type(e).__name__}: {e}")


@router.post("/jsonpath", response_model=JsonPathResponse)
def jsonpath_eval(payload: JsonPathRequest) -> JsonPathResponse:
    try:
        data = json.loads(payload.json_text)
    except json.JSONDecodeError as e:
        return JsonPathResponse(matches=[], error=f"Invalid JSON: {e}")
    try:
        expr = jsonpath_parse(payload.expression)
    except Exception as e:  # noqa: BLE001
        return JsonPathResponse(matches=[], error=f"Invalid JSONPath: {e}")
    matches = [m.value for m in expr.find(data)]
    return JsonPathResponse(matches=matches)


@router.post("/curl", response_model=CurlConvertResponse)
def curl_convert(payload: CurlConvertRequest) -> CurlConvertResponse:
    try:
        return CurlConvertResponse(outputs=convert_curl(payload.curl))
    except Exception as e:  # noqa: BLE001
        return CurlConvertResponse(outputs={}, error=f"{type(e).__name__}: {e}")
