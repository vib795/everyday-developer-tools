import hashlib
import hmac
import json
import urllib.parse
import uuid
from datetime import datetime, timezone

import jwt
from fastapi import APIRouter

from ..schemas.codec import (
    CaseConvertRequest,
    CaseConvertResponse,
    HashRequest,
    HashResponse,
    HmacRequest,
    HmacResponse,
    JwtSignRequest,
    JwtSignResponse,
    QueryParamPair,
    QueryStringRequest,
    QueryStringResponse,
    UrlCodecRequest,
    UrlCodecResponse,
    UuidGenerateRequest,
    UuidGenerateResponse,
    UuidInspectRequest,
    UuidInspectResponse,
)
from ..services.case_convert import to_case

router = APIRouter(prefix="/api/codec", tags=["codec"])


_NAMESPACES = {
    "dns": uuid.NAMESPACE_DNS,
    "url": uuid.NAMESPACE_URL,
    "oid": uuid.NAMESPACE_OID,
    "x500": uuid.NAMESPACE_X500,
}


def _uuid7() -> uuid.UUID:
    """RFC 9562 UUIDv7: 48-bit unix-ms timestamp + 74 random bits + version/variant."""
    import os

    ts_ms = int(datetime.now(tz=timezone.utc).timestamp() * 1000)
    rand_a = int.from_bytes(os.urandom(2), "big") & 0x0FFF  # 12 bits
    rand_b = int.from_bytes(os.urandom(8), "big") & 0x3FFFFFFFFFFFFFFF  # 62 bits
    val = (ts_ms & 0xFFFFFFFFFFFF) << 80
    val |= 0x7 << 76
    val |= rand_a << 64
    val |= 0x2 << 62  # variant 10
    val |= rand_b
    return uuid.UUID(int=val)


@router.post("/uuid/generate", response_model=UuidGenerateResponse)
def uuid_generate(payload: UuidGenerateRequest) -> UuidGenerateResponse:
    out: list[str] = []
    for _ in range(payload.count):
        if payload.version == "v1":
            out.append(str(uuid.uuid1()))
        elif payload.version == "v4":
            out.append(str(uuid.uuid4()))
        elif payload.version == "v7":
            out.append(str(_uuid7()))
        elif payload.version in ("v3", "v5"):
            ns = payload.namespace or "dns"
            ns_uuid = _NAMESPACES.get(ns.lower())
            if ns_uuid is None:
                try:
                    ns_uuid = uuid.UUID(ns)
                except (ValueError, AttributeError):
                    ns_uuid = uuid.NAMESPACE_DNS
            name = payload.name or ""
            fn = uuid.uuid3 if payload.version == "v3" else uuid.uuid5
            out.append(str(fn(ns_uuid, name)))
    return UuidGenerateResponse(values=out)


@router.post("/uuid/inspect", response_model=UuidInspectResponse)
def uuid_inspect(payload: UuidInspectRequest) -> UuidInspectResponse:
    try:
        u = uuid.UUID(payload.value.strip())
    except (ValueError, AttributeError) as e:
        return UuidInspectResponse(valid=False, error=str(e))

    variant_map = {
        uuid.RESERVED_NCS: "NCS (reserved)",
        uuid.RFC_4122: "RFC 4122",
        uuid.RESERVED_MICROSOFT: "Microsoft (reserved)",
        uuid.RESERVED_FUTURE: "Future (reserved)",
    }
    ts_iso: str | None = None
    if u.version == 1 and u.variant == uuid.RFC_4122:
        # uuid1 timestamp is 100-ns intervals since 1582-10-15
        secs = (u.time - 0x01B21DD213814000) / 1e7
        ts_iso = datetime.fromtimestamp(secs, tz=timezone.utc).isoformat()
    elif u.version == 7:
        ts_ms = (u.int >> 80) & 0xFFFFFFFFFFFF
        ts_iso = datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).isoformat()

    return UuidInspectResponse(
        valid=True,
        version=u.version,
        variant=variant_map.get(u.variant, str(u.variant)),
        is_nil=u.int == 0,
        hex=u.hex,
        urn=u.urn,
        timestamp_iso=ts_iso,
    )


@router.post("/hash", response_model=HashResponse)
def hash_text(payload: HashRequest) -> HashResponse:
    data = payload.text.encode("utf-8")
    digests: dict[str, str] = {}
    for algo in payload.algorithms:
        h = hashlib.new(algo)
        h.update(data)
        digests[algo] = h.hexdigest()
    return HashResponse(digests=digests)


@router.post("/hmac", response_model=HmacResponse)
def hmac_text(payload: HmacRequest) -> HmacResponse:
    digest = hmac.new(
        payload.secret.encode("utf-8"),
        payload.text.encode("utf-8"),
        getattr(hashlib, payload.algorithm),
    ).hexdigest()
    return HmacResponse(digest=digest)


@router.post("/url", response_model=UrlCodecResponse)
def url_codec(payload: UrlCodecRequest) -> UrlCodecResponse:
    if payload.operation == "encode":
        if payload.component:
            return UrlCodecResponse(output=urllib.parse.quote(payload.text, safe=""))
        return UrlCodecResponse(output=urllib.parse.quote(payload.text, safe=":/?#[]@!$&'()*+,;="))
    try:
        return UrlCodecResponse(output=urllib.parse.unquote(payload.text))
    except Exception as e:  # noqa: BLE001
        return UrlCodecResponse(output=f"Error: {e}")


@router.post("/url/parse", response_model=QueryStringResponse)
def query_string_parse(payload: QueryStringRequest) -> QueryStringResponse:
    text = payload.text.strip()
    base: str | None = None
    qs = text
    if "?" in text:
        base, qs = text.split("?", 1)
    elif text.startswith("?"):
        qs = text[1:]
    pairs = urllib.parse.parse_qsl(qs, keep_blank_values=True)
    return QueryStringResponse(
        params=[QueryParamPair(key=k, value=v) for k, v in pairs],
        base=base or None,
    )


@router.post("/case", response_model=CaseConvertResponse)
def case_convert(payload: CaseConvertRequest) -> CaseConvertResponse:
    return CaseConvertResponse(output=to_case(payload.text, payload.style))


@router.post("/jwt/sign", response_model=JwtSignResponse)
def jwt_sign(payload: JwtSignRequest) -> JwtSignResponse:
    try:
        body = payload.payload
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError as e:
                return JwtSignResponse(error=f"Invalid JSON payload: {e}")
        token = jwt.encode(body, payload.secret, algorithm=payload.algorithm)
        return JwtSignResponse(token=token)
    except Exception as e:  # noqa: BLE001
        return JwtSignResponse(error=f"Sign failed: {e}")
