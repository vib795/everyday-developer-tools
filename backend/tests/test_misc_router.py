def test_http_statuses_listed(client):
    r = client.get("/api/misc/http-statuses")
    body = r.json()
    codes = {s["code"] for s in body["statuses"]}
    # Spot-check the most common codes are there.
    for c in (200, 201, 301, 400, 401, 403, 404, 500, 503):
        assert c in codes


def test_http_statuses_have_name_and_desc(client):
    r = client.get("/api/misc/http-statuses")
    for s in r.json()["statuses"]:
        assert s["name"] and s["description"]


def test_mime_types_listed(client):
    r = client.get("/api/misc/mime-types")
    body = r.json()
    types = {m["type"] for m in body["mime_types"]}
    for t in ("application/json", "text/html", "image/png", "application/pdf"):
        assert t in types


def test_lorem_paragraphs(client):
    r = client.post("/api/misc/lorem", json={"units": "paragraphs", "count": 3})
    text = r.json()["text"]
    assert text.lower().startswith("lorem ipsum")
    assert text.count("\n\n") == 2  # 3 paragraphs separated by blank lines


def test_lorem_sentences(client):
    r = client.post("/api/misc/lorem", json={"units": "sentences", "count": 2, "start_with_lorem": False})
    text = r.json()["text"]
    assert len(text) > 0
    # Two sentences end with periods
    assert text.count(".") >= 2


def test_lorem_words(client):
    r = client.post("/api/misc/lorem", json={"units": "words", "count": 5, "start_with_lorem": False})
    text = r.json()["text"]
    assert len(text.split()) == 5


def test_qr_basic(client):
    r = client.post("/api/misc/qr", json={"text": "https://example.com"})
    body = r.json()
    assert body["error"] is None
    svg = body["svg"]
    assert svg.startswith("<?xml") or svg.startswith("<svg")
    assert "<svg" in svg


def test_qr_empty_returns_error(client):
    r = client.post("/api/misc/qr", json={"text": ""})
    assert r.json()["error"] == "Text is empty"
