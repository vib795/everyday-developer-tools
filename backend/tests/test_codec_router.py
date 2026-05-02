import hashlib
import hmac as _hmac
import json
import urllib.parse
import uuid

import jwt


# UUID

def test_uuid_v4_generate(client):
    r = client.post("/api/codec/uuid/generate", json={"version": "v4", "count": 3})
    assert r.status_code == 200
    values = r.json()["values"]
    assert len(values) == 3
    for v in values:
        u = uuid.UUID(v)
        assert u.version == 4


def test_uuid_v7_generate_is_time_ordered(client):
    r = client.post("/api/codec/uuid/generate", json={"version": "v7", "count": 5})
    values = r.json()["values"]
    assert len(values) == 5
    parsed = [uuid.UUID(v) for v in values]
    # v7 prefix is the unix-ms timestamp; consecutive ones should be non-decreasing.
    times = [(p.int >> 80) & 0xFFFFFFFFFFFF for p in parsed]
    assert times == sorted(times)


def test_uuid_v5_deterministic(client):
    body = {"version": "v5", "namespace": "dns", "name": "example.com"}
    a = client.post("/api/codec/uuid/generate", json=body).json()["values"][0]
    b = client.post("/api/codec/uuid/generate", json=body).json()["values"][0]
    assert a == b


def test_uuid_inspect_v4(client):
    val = "550e8400-e29b-41d4-a716-446655440000"
    r = client.post("/api/codec/uuid/inspect", json={"value": val})
    body = r.json()
    assert body["valid"] is True
    assert body["version"] == 4
    assert body["variant"] == "RFC 4122"


def test_uuid_inspect_invalid(client):
    r = client.post("/api/codec/uuid/inspect", json={"value": "not-a-uuid"})
    assert r.json()["valid"] is False


def test_uuid_inspect_v7_returns_timestamp(client):
    gen = client.post("/api/codec/uuid/generate", json={"version": "v7", "count": 1})
    val = gen.json()["values"][0]
    r = client.post("/api/codec/uuid/inspect", json={"value": val})
    body = r.json()
    assert body["version"] == 7
    assert body["timestamp_iso"] is not None


# Hash & HMAC

def test_hash_sha256(client):
    r = client.post("/api/codec/hash", json={"text": "hello", "algorithms": ["sha256"]})
    assert r.json()["digests"]["sha256"] == hashlib.sha256(b"hello").hexdigest()


def test_hash_multiple_algos(client):
    r = client.post(
        "/api/codec/hash",
        json={"text": "hello", "algorithms": ["md5", "sha1", "sha512"]},
    )
    digs = r.json()["digests"]
    assert digs["md5"] == hashlib.md5(b"hello").hexdigest()
    assert digs["sha1"] == hashlib.sha1(b"hello").hexdigest()
    assert digs["sha512"] == hashlib.sha512(b"hello").hexdigest()


def test_hmac_sha256(client):
    r = client.post(
        "/api/codec/hmac",
        json={"text": "hello", "secret": "key", "algorithm": "sha256"},
    )
    expected = _hmac.new(b"key", b"hello", hashlib.sha256).hexdigest()
    assert r.json()["digest"] == expected


# URL codec

def test_url_encode_component(client):
    r = client.post(
        "/api/codec/url",
        json={"text": "a b/c?d=1", "operation": "encode", "component": True},
    )
    assert r.json()["output"] == urllib.parse.quote("a b/c?d=1", safe="")


def test_url_decode(client):
    r = client.post(
        "/api/codec/url",
        json={"text": "a%20b%2Fc", "operation": "decode"},
    )
    assert r.json()["output"] == "a b/c"


def test_query_string_parse_full_url(client):
    r = client.post(
        "/api/codec/url/parse",
        json={"text": "https://example.com/path?a=1&b=hi%20there&c="},
    )
    body = r.json()
    assert body["base"] == "https://example.com/path"
    pairs = {(p["key"], p["value"]) for p in body["params"]}
    assert ("a", "1") in pairs
    assert ("b", "hi there") in pairs
    assert ("c", "") in pairs


def test_query_string_parse_bare(client):
    r = client.post("/api/codec/url/parse", json={"text": "a=1&b=2"})
    body = r.json()
    assert body["base"] is None
    assert {(p["key"], p["value"]) for p in body["params"]} == {("a", "1"), ("b", "2")}


# Case converter

def test_case_camel(client):
    r = client.post("/api/codec/case", json={"text": "hello world FOO_BAR", "style": "camel"})
    assert r.json()["output"] == "helloWorldFooBar"


def test_case_snake(client):
    r = client.post("/api/codec/case", json={"text": "HelloWorldHTTPServer", "style": "snake"})
    assert r.json()["output"] == "hello_world_http_server"


def test_case_kebab(client):
    r = client.post("/api/codec/case", json={"text": "Hello World", "style": "kebab"})
    assert r.json()["output"] == "hello-world"


def test_case_constant(client):
    r = client.post("/api/codec/case", json={"text": "myVar name", "style": "constant"})
    assert r.json()["output"] == "MY_VAR_NAME"


def test_case_pascal(client):
    r = client.post("/api/codec/case", json={"text": "user_id", "style": "pascal"})
    assert r.json()["output"] == "UserId"


# JWT signer

def test_jwt_sign_dict_payload(client):
    r = client.post(
        "/api/codec/jwt/sign",
        json={"payload": {"sub": "abc", "n": 1}, "secret": "supersecretkey", "algorithm": "HS256"},
    )
    token = r.json()["token"]
    assert token
    decoded = jwt.decode(token, "supersecretkey", algorithms=["HS256"])
    assert decoded == {"sub": "abc", "n": 1}


def test_jwt_sign_json_string_payload(client):
    payload = json.dumps({"x": 42})
    r = client.post(
        "/api/codec/jwt/sign",
        json={"payload": payload, "secret": "abcdefghijklmnopqrstuvwxyz123456", "algorithm": "HS512"},
    )
    token = r.json()["token"]
    assert token
    decoded = jwt.decode(token, "abcdefghijklmnopqrstuvwxyz123456", algorithms=["HS512"])
    assert decoded == {"x": 42}


def test_jwt_sign_bad_json_payload(client):
    r = client.post(
        "/api/codec/jwt/sign",
        json={"payload": "not json", "secret": "k", "algorithm": "HS256"},
    )
    assert "Invalid JSON" in r.json()["error"]
