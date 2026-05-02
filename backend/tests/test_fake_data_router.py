def test_supported_types(client):
    r = client.get("/api/fake-data/types")
    assert r.status_code == 200
    types = r.json()["types"]
    assert "name" in types
    assert "car_make" in types
    assert "car_model" in types


def test_preview(client):
    payload = {
        "field_names": ["name", "make", "model"],
        "field_types": ["name", "car_make", "car_model"],
        "num_records": 3,
    }
    r = client.post("/api/fake-data/preview", json=payload)
    assert r.status_code == 200
    records = r.json()["records"]
    assert len(records) == 3
    for rec in records:
        assert rec["name"]
        assert rec["make"]
        assert rec["model"]


def test_preview_unsupported_type(client):
    r = client.post(
        "/api/fake-data/preview",
        json={"field_names": ["x"], "field_types": ["nope"], "num_records": 1},
    )
    assert r.status_code == 400


def test_preview_mismatched_lengths(client):
    r = client.post(
        "/api/fake-data/preview",
        json={"field_names": ["x", "y"], "field_types": ["name"], "num_records": 1},
    )
    assert r.status_code == 400


def test_export_json(client):
    r = client.post(
        "/api/fake-data/export",
        json={
            "field_names": ["name"],
            "field_types": ["name"],
            "num_records": 2,
            "format": "json",
        },
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/json")
    assert "fake_data.json" in r.headers["content-disposition"]


def test_export_csv(client):
    r = client.post(
        "/api/fake-data/export",
        json={
            "field_names": ["name", "email"],
            "field_types": ["name", "email"],
            "num_records": 2,
            "format": "csv",
        },
    )
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/csv")
    text = r.content.decode()
    lines = [line for line in text.splitlines() if line.strip()]
    assert lines[0] == "name,email"
    assert len(lines) == 3
