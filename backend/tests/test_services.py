import json

from app.services.diff import structured_diff
from app.services.fake_data import generate_fake_data
from app.services.json_schema import apply_conditions_to_schema, generate_json_schema
from app.services.markdown_pdf import _inline, markdown_to_pdf, pdf_to_markdown
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


def _side(hunks, key):
    lines = []
    for h in hunks:
        lines.extend(h[key])
    return lines


def test_structured_diff_reconstructs_both_sides():
    text1 = "the\nquick\nbrown\nfox"
    text2 = "the\nlazy\nbrown\ndog\nhere"
    hunks = structured_diff(text1, text2)
    a, b = text1.splitlines(), text2.splitlines()
    # Concatenating each side over the hunks rebuilds the original inputs,
    # and every hunk's start index points at the right offset.
    assert _side(hunks, "left") == a
    assert _side(hunks, "right") == b
    for h in hunks:
        assert h["left"] == a[h["left_start"] : h["left_start"] + len(h["left"])]
        assert h["right"] == b[h["right_start"] : h["right_start"] + len(h["right"])]


def test_structured_diff_is_minimum_edit_script():
    # Myers (1986) worked example: "ABCABBA" -> "CBABAC" has edit distance 5
    # and a longest common subsequence of length 4. A correct O(ND) diff must
    # reproduce those invariants regardless of the exact path chosen.
    hunks = structured_diff("\n".join("ABCABBA"), "\n".join("CBABAC"))
    kept = sum(len(h["left"]) for h in hunks if h["tag"] == "equal")
    changed = sum(len(h["left"]) + len(h["right"]) for h in hunks if h["tag"] != "equal")
    assert kept == 4
    assert changed == 5


def test_inline_markdown_converts_emphasis_and_code():
    assert _inline("**bold**") == "<b>bold</b>"
    assert _inline("*italic*") == "<i>italic</i>"
    assert _inline("`code`") == '<font face="Courier">code</font>'
    # emphasis markers inside a code span are left alone
    assert _inline("`a*b*c`") == '<font face="Courier">a*b*c</font>'
    # underscores inside words are not treated as italics
    assert _inline("snake_case_name") == "snake_case_name"
    # angle brackets and ampersands are escaped, not passed through as markup
    assert _inline("a < b & c") == "a &lt; b &amp; c"


def test_ordered_list_marker_digits_are_bounded():
    from app.services.markdown_pdf import _ORDERED

    assert _ORDERED.match("1. First").group(1) == "First"
    assert _ORDERED.match("42. Answer").group(1) == "Answer"
    # A long run of digits with no trailing "." must not send the engine
    # backtracking once per digit (CodeQL py/polynomial-redos).
    assert _ORDERED.match("9" * 50_000) is None


def test_markdown_to_pdf_does_not_leak_markers():
    md = (
        "# Developer Tools\n\n"
        "### Encoding\n"
        "- **Base64** — encode UTF-8 text.\n"
        "- **URL Codec** — encode text.\n\n"
        "1. First\n2. Second\n\n"
        "A `code` word and **bold** text.\n"
    )
    pdf = markdown_to_pdf(md)
    assert pdf.startswith(b"%PDF")
    text = pdf_to_markdown(pdf)
    # content survives, but raw bold markers and leading bullet dashes do not
    assert "Developer Tools" in text
    assert "Base64" in text
    assert "**" not in text
    assert "- Base64" not in text
