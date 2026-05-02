import csv
import io
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from ..schemas.fake_data import (
    FakeDataExportRequest,
    FakeDataPreviewRequest,
    FakeDataPreviewResponse,
)
from ..services.fake_data import SUPPORTED_TYPES, generate_fake_data

router = APIRouter(prefix="/api/fake-data", tags=["fake_data"])


def _validate(payload: FakeDataPreviewRequest) -> None:
    if len(payload.field_names) != len(payload.field_types):
        raise HTTPException(
            status_code=400, detail="field_names and field_types must have equal length."
        )
    bad = [t for t in payload.field_types if t not in SUPPORTED_TYPES]
    if bad:
        raise HTTPException(status_code=400, detail=f"Unsupported field types: {bad}")


@router.get("/types")
def supported_types() -> dict:
    return {"types": SUPPORTED_TYPES}


@router.post("/preview", response_model=FakeDataPreviewResponse)
def preview(payload: FakeDataPreviewRequest) -> FakeDataPreviewResponse:
    _validate(payload)
    records = generate_fake_data(payload.field_names, payload.field_types, payload.num_records)
    return FakeDataPreviewResponse(records=records)


@router.post("/export")
def export(payload: FakeDataExportRequest) -> StreamingResponse:
    _validate(payload)
    records = generate_fake_data(payload.field_names, payload.field_types, payload.num_records)

    if payload.format == "json":
        body = json.dumps(records, indent=2, default=str)
        return StreamingResponse(
            iter([body]),
            media_type="application/json",
            headers={"Content-Disposition": 'attachment; filename="fake_data.json"'},
        )

    si = io.StringIO()
    writer = csv.DictWriter(si, fieldnames=payload.field_names)
    writer.writeheader()
    writer.writerows(records)
    return StreamingResponse(
        iter([si.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="fake_data.csv"'},
    )
