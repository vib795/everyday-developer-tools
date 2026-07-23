import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from ..services.markdown_pdf import markdown_to_pdf, pdf_to_markdown

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/document", tags=["document"])

# ReportLab's paragraph layout is superlinear in the length of a single
# unbreakable token, so an oversized document can occupy a worker for minutes.
MAX_MARKDOWN_CHARS = 100_000


# Deliberately sync: FastAPI runs `def` handlers in a threadpool, so the blocking
# conversion below cannot stall the event loop for every other request.
@router.post("/md-to-pdf")
def md_to_pdf(payload: dict) -> Response:
    text = payload.get("markdown_text", "")
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="markdown_text must be a string")
    if len(text) > MAX_MARKDOWN_CHARS:
        raise HTTPException(
            status_code=413,
            detail=f"markdown_text exceeds {MAX_MARKDOWN_CHARS} characters",
        )
    try:
        pdf_bytes = markdown_to_pdf(text)
    except Exception as e:  # noqa: BLE001
        logger.error("md->pdf failed: %s", e)
        raise HTTPException(status_code=400, detail=f"Conversion failed: {e}")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="output.pdf"'},
    )


@router.post("/pdf-to-md")
async def pdf_to_md(pdf_file: UploadFile = File(...)) -> dict:
    try:
        data = await pdf_file.read()
        text = pdf_to_markdown(data)
    except Exception as e:  # noqa: BLE001
        logger.error("pdf->md failed: %s", e)
        raise HTTPException(status_code=400, detail=f"Conversion failed: {e}")
    return {"text": text}
