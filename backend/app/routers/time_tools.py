from fastapi import APIRouter, HTTPException

from ..schemas.time_tools import (
    CronRequest,
    CronResponse,
    TimeConvertRequest,
    TimeConvertResponse,
)
from ..services.time_convert import convert_time

router = APIRouter(prefix="/api/time", tags=["time"])


@router.post("/convert", response_model=TimeConvertResponse)
def time_convert(payload: TimeConvertRequest) -> TimeConvertResponse:
    try:
        return TimeConvertResponse(output=convert_time(payload.time_input))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/cron", response_model=CronResponse)
def cron(payload: CronRequest) -> CronResponse:
    expression = (
        f"{payload.minute} {payload.hour} {payload.day_of_month} "
        f"{payload.month} {payload.day_of_week}"
    )
    return CronResponse(expression=expression)
