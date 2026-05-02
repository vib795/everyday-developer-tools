import io

import qrcode
import qrcode.image.svg
from faker import Faker
from fastapi import APIRouter

from ..schemas.misc import (
    HttpStatusListResponse,
    LoremRequest,
    LoremResponse,
    MimeTypeListResponse,
    QrCodeRequest,
    QrCodeResponse,
)
from ..services.reference_data import HTTP_STATUSES, MIME_TYPES

router = APIRouter(prefix="/api/misc", tags=["misc"])

_fake = Faker()


@router.get("/http-statuses", response_model=HttpStatusListResponse)
def http_statuses() -> HttpStatusListResponse:
    return HttpStatusListResponse(statuses=HTTP_STATUSES)


@router.get("/mime-types", response_model=MimeTypeListResponse)
def mime_types() -> MimeTypeListResponse:
    return MimeTypeListResponse(mime_types=MIME_TYPES)


@router.post("/lorem", response_model=LoremResponse)
def lorem(payload: LoremRequest) -> LoremResponse:
    if payload.units == "paragraphs":
        paragraphs = [_fake.paragraph(nb_sentences=4) for _ in range(payload.count)]
        text = "\n\n".join(paragraphs)
    elif payload.units == "sentences":
        text = " ".join(_fake.sentence() for _ in range(payload.count))
    else:
        text = " ".join(_fake.words(nb=payload.count))

    if payload.start_with_lorem and not text.lower().startswith("lorem ipsum"):
        suffix = text[0].lower() + text[1:] if text else ""
        text = "Lorem ipsum dolor sit amet, " + suffix
    return LoremResponse(text=text)


_EC_MAP = {
    "L": qrcode.constants.ERROR_CORRECT_L,
    "M": qrcode.constants.ERROR_CORRECT_M,
    "Q": qrcode.constants.ERROR_CORRECT_Q,
    "H": qrcode.constants.ERROR_CORRECT_H,
}


@router.post("/qr", response_model=QrCodeResponse)
def qr(payload: QrCodeRequest) -> QrCodeResponse:
    if not payload.text:
        return QrCodeResponse(error="Text is empty")
    try:
        q = qrcode.QRCode(
            error_correction=_EC_MAP[payload.error_correction],
            box_size=payload.box_size,
            border=payload.border,
        )
        q.add_data(payload.text)
        q.make(fit=True)
        img = q.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        buf = io.BytesIO()
        img.save(buf)
        return QrCodeResponse(svg=buf.getvalue().decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        return QrCodeResponse(error=f"{type(e).__name__}: {e}")
