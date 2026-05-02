import base64

import jwt


def test_base64_round_trip(client):
    enc = client.post(
        "/api/encoding/base64", json={"input_text": "hello", "operation": "encode"}
    )
    assert enc.status_code == 200
    encoded = enc.json()["output"]
    assert base64.b64decode(encoded).decode() == "hello"

    dec = client.post(
        "/api/encoding/base64", json={"input_text": encoded, "operation": "decode"}
    )
    assert dec.json()["output"] == "hello"


def test_base64_decode_error(client):
    # Decoding non-UTF-8 bytes produces an error string (the legacy app's contract).
    encoded = base64.b64encode(bytes([200, 201, 202])).decode()
    r = client.post(
        "/api/encoding/base64", json={"input_text": encoded, "operation": "decode"}
    )
    assert "Error" in r.json()["output"]


def test_jwt_decode(client):
    token = jwt.encode({"user": "x"}, "secret", algorithm="HS256")
    r = client.post(
        "/api/encoding/jwt", json={"jwt_token": token, "secret_key": "secret"}
    )
    body = r.json()
    assert body["decoded"] == {"user": "x"}


def test_jwt_invalid(client):
    r = client.post(
        "/api/encoding/jwt", json={"jwt_token": "not-a-token", "secret_key": "secret"}
    )
    assert r.json()["error"] == "Invalid token"
