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
    try:
        decoded = jwt.decode(payload.jwt_token, payload.secret_key, algorithms=["HS256"])
        return JwtResponse(decoded=decoded)
    except jwt.ExpiredSignatureError:
        return JwtResponse(error="Token has expired")
    except jwt.InvalidTokenError:
        return JwtResponse(error="Invalid token")
