def test_check_match(client):
    r = client.post("/api/regex/check", json={"regex": r"^a.*z$", "string": "abcz"})
    assert r.status_code == 200
    body = r.json()
    assert body["match"] is True
    assert "matches" in body["message"].lower()


def test_check_no_match(client):
    r = client.post("/api/regex/check", json={"regex": r"^a.*z$", "string": "nope"})
    assert r.status_code == 200
    body = r.json()
    assert body["match"] is False


def test_check_invalid_regex(client):
    r = client.post("/api/regex/check", json={"regex": "[", "string": "x"})
    assert r.status_code == 200
    assert "regex error" in r.json()["message"].lower()


def test_generate_email(client):
    r = client.post("/api/regex/generate", json={"text_input": "foo@bar.com"})
    assert r.status_code == 200
    assert "@" in r.json()["pattern"]


def test_generate_phone(client):
    r = client.post("/api/regex/generate", json={"text_input": "+15551234567"})
    assert r.status_code == 200
    assert r.json()["pattern"] == r"\+?1?\d{10,15}"


def test_generate_basic(client):
    r = client.post("/api/regex/generate", json={"text_input": "Ab1!"})
    assert r.status_code == 200
    p = r.json()["pattern"]
    assert p.startswith("[") and p.endswith("}")
