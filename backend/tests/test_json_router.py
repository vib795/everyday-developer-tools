import json


def test_validate_valid(client):
    r = client.post("/api/json/validate", json={"json_input": '{"a": 1}'})
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert "valid" in body["message"].lower()
    assert json.loads(body["formatted_json"]) == {"a": 1}


def test_validate_invalid(client):
    r = client.post("/api/json/validate", json={"json_input": "{not-json}"})
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is False
    assert body["error_details"]


def test_validate_with_schema(client):
    payload = {
        "json_input": json.dumps({"name": "x"}),
        "schema_input": json.dumps({"type": "object", "required": ["name"]}),
    }
    r = client.post("/api/json/validate", json=payload)
    assert r.status_code == 200
    assert r.json()["valid"] is True


def test_validate_against_failing_schema(client):
    payload = {
        "json_input": json.dumps({"name": 1}),
        "schema_input": json.dumps(
            {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}
        ),
    }
    r = client.post("/api/json/validate", json=payload)
    body = r.json()
    assert body["valid"] is False
    assert "schema" in body["message"].lower()


def test_schema_generator(client):
    r = client.post("/api/json/schema", json={"json_input": '{"a": 1}'})
    assert r.status_code == 200
    schema = r.json()["schema"]
    assert schema["$schema"] == "http://json-schema.org/draft-04/schema#"
    assert schema["type"] == "object"
    assert "a" in schema["properties"]


def test_schema_generator_invalid(client):
    r = client.post("/api/json/schema", json={"json_input": "not-json"})
    assert r.status_code == 400


def test_sample_generator(client):
    schema = json.dumps(
        {"type": "object", "properties": {"name": {"type": "string"}, "age": {"type": "integer"}}}
    )
    r = client.post("/api/json/sample", json={"schema_input": schema})
    assert r.status_code == 200
    sample = r.json()["sample"]
    assert isinstance(sample, dict)
    assert "name" in sample and "age" in sample


def test_sample_generator_invalid_json(client):
    r = client.post("/api/json/sample", json={"schema_input": "{"})
    assert r.status_code == 400


def test_convert_to_string_and_back(client):
    r = client.post(
        "/api/json/convert",
        json={"input_data": '{"a":1}', "conversion_type": "to_string"},
    )
    assert r.status_code == 200
    out = r.json()["output"]
    assert out.startswith('"') and out.endswith('"')

    r2 = client.post(
        "/api/json/convert", json={"input_data": out, "conversion_type": "to_json"}
    )
    assert r2.status_code == 200
    assert json.loads(r2.json()["output"]) == {"a": 1}


def test_convert_invalid_type(client):
    r = client.post(
        "/api/json/convert", json={"input_data": "{}", "conversion_type": "blah"}
    )
    assert r.status_code in (400, 422)


def test_parse(client):
    r = client.post("/api/json/parse", json={"input_json": '{"a": 1}'})
    assert r.status_code == 200
    assert json.loads(r.json()["output"]) == {"a": 1}


def test_parse_invalid(client):
    r = client.post("/api/json/parse", json={"input_json": "not-json"})
    assert r.status_code == 400
