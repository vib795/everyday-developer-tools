from typing import Any, Literal

from pydantic import BaseModel


class Base64Request(BaseModel):
    input_text: str
    operation: Literal["encode", "decode"] = "encode"


class Base64Response(BaseModel):
    output: str


class JwtRequest(BaseModel):
    jwt_token: str
    secret_key: str = ""


class JwtResponse(BaseModel):
    decoded: dict[str, Any] | None = None
    error: str | None = None
    # False when the token was decoded without checking its signature,
    # which happens when no secret is supplied. Callers must not treat an
    # unverified payload as trustworthy.
    signature_verified: bool = False
