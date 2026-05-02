import logging

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import Response

from ..services.markdown_pdf import markdown_to_pdf, pdf_to_markdown

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/document", tags=["document"])


@router.post("/md-to-pdf")
async def md_to_pdf(payload: dict) -> Response:
    text = payload.get("markdown_text", "")
    if not isinstance(text, str):
        raise HTTPException(status_code=400, detail="markdown_text must be a string")
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
