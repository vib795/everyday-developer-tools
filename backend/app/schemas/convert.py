from typing import Literal

from pydantic import BaseModel

Format = Literal["json", "yaml", "toml", "xml", "csv"]


class FormatConvertRequest(BaseModel):
    text: str
    source: Format
    target: Format


class FormatConvertResponse(BaseModel):
    output: str
    error: str | None = None


class JsonPathRequest(BaseModel):
    json_text: str
    expression: str


class JsonPathResponse(BaseModel):
    matches: list = []
    error: str | None = None


class CurlConvertRequest(BaseModel):
    curl: str


class CurlConvertResponse(BaseModel):
    outputs: dict[str, str] = {}
    error: str | None = None
