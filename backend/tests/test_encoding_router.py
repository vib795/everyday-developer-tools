import base64

import jwt


def test_base64_round_trip(client):
    enc = client.post("/api/encoding/base64", json={"input_text": "hello", "operation": "encode"})
    assert enc.status_code == 200
    encoded = enc.json()["output"]
    assert base64.b64decode(encoded).decode() == "hello"

    dec = client.post("/api/encoding/base64", json={"input_text": encoded, "operation": "decode"})
    assert dec.json()["output"] == "hello"


def test_base64_decode_error(client):
    # Decoding non-UTF-8 bytes produces an error string (the legacy app's contract).
    encoded = base64.b64encode(bytes([200, 201, 202])).decode()
    r = client.post("/api/encoding/base64", json={"input_text": encoded, "operation": "decode"})
    assert "Error" in r.json()["output"]


def test_jwt_decode(client):
    token = jwt.encode({"user": "x"}, "secret", algorithm="HS256")
    r = client.post("/api/encoding/jwt", json={"jwt_token": token, "secret_key": "secret"})
    body = r.json()
    assert body["decoded"] == {"user": "x"}


def test_jwt_invalid(client):
    r = client.post("/api/encoding/jwt", json={"jwt_token": "not-a-token", "secret_key": "secret"})
    assert r.json()["error"] == "Invalid token"


def test_jwt_without_secret_decodes_unverified(client):
    # The page is a "JWT Viewer" and its Secret Key input is not required, so
    # submitting a token with no secret is the normal flow. It used to 500:
    # pyjwt raises InvalidKeyError for an empty key, which is not an
    # InvalidTokenError and so escaped the handler.
    token = jwt.encode({"user": "x"}, "secret", algorithm="HS256")
    r = client.post("/api/encoding/jwt", json={"jwt_token": token})
    assert r.status_code == 200
    body = r.json()
    assert body["decoded"] == {"user": "x"}
    assert body["signature_verified"] is False


def test_jwt_empty_secret_decodes_unverified(client):
    token = jwt.encode({"user": "x"}, "secret", algorithm="HS256")
    r = client.post("/api/encoding/jwt", json={"jwt_token": token, "secret_key": ""})
    assert r.status_code == 200
    assert r.json()["signature_verified"] is False


def test_jwt_with_secret_reports_verified(client):
    token = jwt.encode({"user": "x"}, "secret", algorithm="HS256")
    r = client.post("/api/encoding/jwt", json={"jwt_token": token, "secret_key": "secret"})
    body = r.json()
    assert body["decoded"] == {"user": "x"}
    assert body["signature_verified"] is True


def test_jwt_wrong_secret_still_rejected(client):
    # Verification must still fail loudly when a secret IS supplied.
    token = jwt.encode({"user": "x"}, "secret", algorithm="HS256")
    r = client.post("/api/encoding/jwt", json={"jwt_token": token, "secret_key": "wrong"})
    body = r.json()
    assert body["decoded"] is None
    assert body["error"] == "Invalid token"


def test_jwt_malformed_without_secret(client):
    r = client.post("/api/encoding/jwt", json={"jwt_token": "not-a-token"})
    assert r.status_code == 200
    assert r.json()["error"] == "Invalid token"
