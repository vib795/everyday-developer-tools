import json

from app.services.diff import structured_diff
from app.services.fake_data import generate_fake_data
from app.services.json_schema import apply_conditions_to_schema, generate_json_schema
from app.services.regex_gen import detect_pattern, generate_basic_pattern
from app.services.sample_data import generate_sample_data


def test_generate_json_schema_includes_dollar_schema():
    schema = generate_json_schema('{"a": 1}')
    assert schema["$schema"] == "http://json-schema.org/draft-04/schema#"


def test_generate_json_schema_invalid_input_raises():
    import pytest

    with pytest.raises(ValueError):
        generate_json_schema("nope")


def test_apply_conditions_root_level():
    schema: dict = {}
    apply_conditions_to_schema(schema, [{"path": "", "condition": {"required": ["x"]}}])
    assert schema["required"] == ["x"]


def test_apply_conditions_nested_path():
    schema: dict = {}
    apply_conditions_to_schema(
        schema,
        [{"path": "address.zip", "condition": {"type": "string"}}],
    )
    assert (
        schema["properties"]["address"]["properties"]["zip"]["type"] == "string"
    )


def test_generate_sample_data_full_shape():
    schema = json.loads(
        json.dumps(
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "age": {"type": "integer"},
                    "active": {"type": "boolean"},
                    "score": {"type": "number", "minimum": 0, "maximum": 10},
                    "id": {"type": "string", "format": "uuid"},
                    "email": {"type": "string", "format": "email"},
                    "tag": {"type": "string", "enum": ["a", "b"]},
                    "nothing": {"type": "null"},
                    "tags": {"type": "array", "items": {"type": "string"}},
                },
            }
        )
    )
    sample = generate_sample_data(schema)
    assert isinstance(sample["name"], str)
    assert isinstance(sample["age"], int)
    assert isinstance(sample["active"], bool)
    assert 0 <= sample["score"] <= 10
    assert sample["email"] == "example@example.com"
    assert sample["tag"] in ("a", "b")
    assert sample["nothing"] is None
    assert isinstance(sample["tags"], list)


def test_detect_pattern_email_phone_date_ssn():
    assert "@" in detect_pattern("foo@bar.com")
    assert detect_pattern("+15551234567") == r"\+?1?\d{10,15}"
    assert detect_pattern("2024-01-01") == r"\d{4}-\d{2}-\d{2}"
    assert detect_pattern("123-45-6789") == r"\d{3}-\d{2}-\d{4}"


def test_basic_pattern_includes_classes():
    pat = generate_basic_pattern("Aa1!")
    assert "a-z" in pat
    assert "A-Z" in pat
    assert "0-9" in pat


def test_generate_fake_data_make_model_pairing():
    from app.services.fake_data import CAR_MODELS

    records = generate_fake_data(
        ["make", "model"], ["car_make", "car_model"], 25
    )
    for rec in records:
        assert rec["model"] in CAR_MODELS[rec["make"]]


def test_generate_fake_data_zero_records():
    assert generate_fake_data(["name"], ["name"], 0) == []


def test_structured_diff_emits_change_tags():
    hunks = structured_diff("a\nb", "a\nc")
    tags = {h["tag"] for h in hunks}
    assert "equal" in tags
    assert tags & {"replace", "delete", "insert"}
