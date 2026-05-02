from pydantic import BaseModel


class RegexCheckRequest(BaseModel):
    regex: str
    string: str


class RegexCheckResponse(BaseModel):
    match: bool | None
    message: str


class RegexGenerateRequest(BaseModel):
    text_input: str


class RegexGenerateResponse(BaseModel):
    pattern: str
