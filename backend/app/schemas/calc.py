from pydantic import BaseModel, Field


class CronNextRunsRequest(BaseModel):
    expression: str
    count: int = Field(5, ge=1, le=50)
    timezone: str | None = None  # IANA tz; None → UTC


class CronNextRunsResponse(BaseModel):
    runs: list[str] = []
    error: str | None = None


class ColorConvertRequest(BaseModel):
    color: str  # accepts hex, rgb(...), hsl(...)


class ColorConvertResponse(BaseModel):
    hex: str = ""
    rgb: str = ""
    hsl: str = ""
    oklch: str | None = None
    error: str | None = None


class ContrastRequest(BaseModel):
    foreground: str
    background: str


class ContrastResponse(BaseModel):
    ratio: float = 0.0
    aa_normal: bool = False
    aa_large: bool = False
    aaa_normal: bool = False
    aaa_large: bool = False
    error: str | None = None


class ChmodRequest(BaseModel):
    value: str  # "755" or "rwxr-xr-x" or "u+rwx,go+rx"


class ChmodResponse(BaseModel):
    numeric: str = ""
    symbolic: str = ""
    error: str | None = None


class CidrRequest(BaseModel):
    cidr: str  # "10.0.0.0/24"


class CidrResponse(BaseModel):
    network: str = ""
    netmask: str = ""
    broadcast: str | None = None
    first_host: str | None = None
    last_host: str | None = None
    num_hosts: int = 0
    prefix: int = 0
    version: int = 4
    error: str | None = None


class MarkdownPreviewRequest(BaseModel):
    text: str


class MarkdownPreviewResponse(BaseModel):
    html: str
