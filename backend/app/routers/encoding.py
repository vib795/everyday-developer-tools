import base64

import jwt
from fastapi import APIRouter

from ..schemas.encoding import Base64Request, Base64Response, JwtRequest, JwtResponse

router = APIRouter(prefix="/api/encoding", tags=["encoding"])


@router.post("/base64", response_model=Base64Response)
def base64_endpoint(payload: Base64Request) -> Base64Response:
    try:
        if payload.operation == "encode":
            return Base64Response(output=base64.b64encode(payload.input_text.encode()).decode())
        return Base64Response(output=base64.b64decode(payload.input_text.encode()).decode())
    except Exception as e:  # noqa: BLE001
        return Base64Response(output=f"Error: {e}")


@router.post("/jwt", response_model=JwtResponse)
def jwt_endpoint(payload: JwtRequest) -> JwtResponse:
    # secret_key is optional (it defaults to "") and the JWT Viewer page does not
    # require it, so decoding a token you hold no secret for is a normal request.
    # Passing an empty key to jwt.decode raises InvalidKeyError, which is NOT an
    # InvalidTokenError and so used to escape this handler as a 500. Inspect the
    # token unverified instead, and tell the caller the signature was not checked.
    if not payload.secret_key:
        try:
            decoded = jwt.decode(payload.jwt_token, options={"verify_signature": False})
            return JwtResponse(decoded=decoded, signature_verified=False)
        except jwt.InvalidTokenError:
            return JwtResponse(error="Invalid token")

    try:
        decoded = jwt.decode(payload.jwt_token, payload.secret_key, algorithms=["HS256"])
        return JwtResponse(decoded=decoded, signature_verified=True)
    except jwt.ExpiredSignatureError:
        return JwtResponse(error="Token has expired")
    except jwt.InvalidTokenError:
        return JwtResponse(error="Invalid token")
