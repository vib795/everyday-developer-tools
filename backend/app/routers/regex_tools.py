import concurrent.futures
import re

from fastapi import APIRouter, Request

from ..config import settings
from ..rate_limit import limiter
from ..schemas.regex_tools import (
    RegexCheckRequest,
    RegexCheckResponse,
    RegexGenerateRequest,
    RegexGenerateResponse,
)
from ..services.regex_gen import detect_pattern

router = APIRouter(prefix="/api/regex", tags=["regex"])

_executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)


@router.post("/check", response_model=RegexCheckResponse)
@limiter.limit(settings.rate_limit_regex_check)
def regex_check(request: Request, payload: RegexCheckRequest) -> RegexCheckResponse:
    future = _executor.submit(re.fullmatch, payload.regex, payload.string)
    try:
        result = future.result(timeout=1)
    except concurrent.futures.TimeoutError:
        return RegexCheckResponse(
            match=None,
            message="Execution timed out due to complex/malicious pattern.",
        )
    except re.error as e:
        return RegexCheckResponse(match=None, message=f"Regex Error: {e}")
    matched = result is not None
    return RegexCheckResponse(
        match=matched,
        message="Pattern matches the string." if matched
        else "Pattern does not match the string.",
    )


@router.post("/generate", response_model=RegexGenerateResponse)
def regex_generate(payload: RegexGenerateRequest) -> RegexGenerateResponse:
    return RegexGenerateResponse(pattern=detect_pattern(payload.text_input))
