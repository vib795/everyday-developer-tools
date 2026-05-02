from typing import Literal

from pydantic import BaseModel, Field


class HttpStatus(BaseModel):
    code: int
    name: str
    description: str


class HttpStatusListResponse(BaseModel):
    statuses: list[HttpStatus]


class MimeType(BaseModel):
    type: str
    extensions: list[str]
    description: str


class MimeTypeListResponse(BaseModel):
    mime_types: list[MimeType]


class LoremRequest(BaseModel):
    units: Literal["paragraphs", "sentences", "words"] = "paragraphs"
    count: int = Field(3, ge=1, le=50)
    start_with_lorem: bool = True


class LoremResponse(BaseModel):
    text: str


class QrCodeRequest(BaseModel):
    text: str
    error_correction: Literal["L", "M", "Q", "H"] = "M"
    box_size: int = Field(8, ge=1, le=40)
    border: int = Field(4, ge=0, le=20)


class QrCodeResponse(BaseModel):
    svg: str = ""
    error: str | None = None
