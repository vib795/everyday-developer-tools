from typing import Literal

from pydantic import BaseModel, Field

# UUID

UuidVersion = Literal["v1", "v3", "v4", "v5", "v7"]


class UuidGenerateRequest(BaseModel):
    version: UuidVersion = "v4"
    count: int = Field(1, ge=1, le=100)
    namespace: str | None = None  # for v3/v5 — uuid in std-form, or "dns"/"url"/"oid"/"x500"
    name: str | None = None  # for v3/v5


class UuidGenerateResponse(BaseModel):
    values: list[str]


class UuidInspectRequest(BaseModel):
    value: str


class UuidInspectResponse(BaseModel):
    valid: bool
    version: int | None = None
    variant: str | None = None
    is_nil: bool | None = None
    hex: str | None = None
    urn: str | None = None
    timestamp_iso: str | None = None  # for v1, v6, v7
    error: str | None = None


# Hash

HashAlgo = Literal["md5", "sha1", "sha256", "sha384", "sha512"]


class HashRequest(BaseModel):
    text: str
    algorithms: list[HashAlgo] = Field(default_factory=lambda: ["sha256"])


class HashResponse(BaseModel):
    digests: dict[str, str]


class HmacRequest(BaseModel):
    text: str
    secret: str
    algorithm: HashAlgo = "sha256"


class HmacResponse(BaseModel):
    digest: str


# URL codec

class UrlCodecRequest(BaseModel):
    text: str
    operation: Literal["encode", "decode"] = "encode"
    component: bool = True  # encodeURIComponent vs encodeURI


class UrlCodecResponse(BaseModel):
    output: str


class QueryStringRequest(BaseModel):
    text: str  # full URL, or just "?a=1&b=2", or "a=1&b=2"


class QueryParamPair(BaseModel):
    key: str
    value: str


class QueryStringResponse(BaseModel):
    params: list[QueryParamPair]
    base: str | None = None  # the URL portion before ?, if present


# Case converter

CaseStyle = Literal[
    "camel",
    "pascal",
    "snake",
    "kebab",
    "constant",
    "title",
    "sentence",
    "lower",
    "upper",
    "dot",
    "path",
]


class CaseConvertRequest(BaseModel):
    text: str
    style: CaseStyle


class CaseConvertResponse(BaseModel):
    output: str


# JWT signer

JwtAlgo = Literal["HS256", "HS384", "HS512"]


class JwtSignRequest(BaseModel):
    payload: dict | str  # dict or JSON string
    secret: str
    algorithm: JwtAlgo = "HS256"


class JwtSignResponse(BaseModel):
    token: str | None = None
    error: str | None = None
