from typing import Any

from pydantic import BaseModel


class TimeConvertRequest(BaseModel):
    time_input: str


class TimeConvertResponse(BaseModel):
    output: dict[str, Any]


class CronRequest(BaseModel):
    minute: str = "*"
    hour: str = "*"
    day_of_month: str = "*"
    month: str = "*"
    day_of_week: str = "*"


class CronResponse(BaseModel):
    expression: str
