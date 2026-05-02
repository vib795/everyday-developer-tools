from typing import Any, Literal

from pydantic import BaseModel, Field


class FakeDataPreviewRequest(BaseModel):
    field_names: list[str]
    field_types: list[str]
    num_records: int = Field(10, ge=0, le=1000)


class FakeDataPreviewResponse(BaseModel):
    records: list[dict[str, Any]]


class FakeDataExportRequest(FakeDataPreviewRequest):
    format: Literal["json", "csv"] = "json"
