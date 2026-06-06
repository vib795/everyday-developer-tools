def test_diff(client):
    r = client.post("/api/string/diff", json={"text1": "hello\nworld", "text2": "hello\nworld!"})
    assert r.status_code == 200
    hunks = r.json()["hunks"]
    assert any(h["tag"] != "equal" for h in hunks)


def test_count_character(client):
    r = client.post(
        "/api/string/count",
        json={"text_input": "abc", "filter_option": "Character"},
    )
    assert r.status_code == 200
    assert r.json()["count"] == 3


def test_count_word(client):
    r = client.post(
        "/api/string/count", json={"text_input": "one two three", "filter_option": "Word"}
    )
    assert r.json()["count"] == 3


def test_count_line(client):
    r = client.post("/api/string/count", json={"text_input": "a\nb\nc", "filter_option": "Line"})
    assert r.json()["count"] == 3


def test_count_custom_delimiter(client):
    r = client.post(
        "/api/string/count",
        json={
            "text_input": "a|b|c",
            "filter_option": "Custom Delimiter",
            "custom_delimiter": "|",
        },
    )
    assert r.json()["count"] == 3


def test_columns(client):
    text = "a,b,c\nd,e,f"
    r = client.post(
        "/api/string/columns", json={"text": text, "column_number": 2, "delimiter": ","}
    )
    assert r.json()["columns"] == ["b", "e"]


def test_clean_preserves_case_and_internal_whitespace(client):
    r = client.post(
        "/api/string/clean",
        json={"text": "  Hello   WORLD\n\nfoo  bar  "},
    )
    assert r.json()["cleaned"] == "Hello   WORLD\n\nfoo  bar"


def test_clean_strips_invisible_and_control_chars(client):
    r = client.post(
        "/api/string/clean",
        json={"text": "﻿hi​there\x07\r\nnext"},
    )
    assert r.json()["cleaned"] == "hithere\nnext"


def test_clean_collapse_spaces_keeps_newlines(client):
    r = client.post(
        "/api/string/clean",
        json={"text": "a    b\n\n  c   d", "collapse_spaces": True},
    )
    assert r.json()["cleaned"] == "a b\n\n c d"


def test_stats(client):
    r = client.post("/api/string/stats", json={"text": "This is a test. This is only a test."})
    assert r.status_code == 200
    body = r.json()
    assert body["num_words"] == 9
    assert body["num_sentences"] == 2


def test_random_number(client):
    r = client.post("/api/string/random-number", json={"min_val": 1, "max_val": 1})
    assert r.json()["value"] == 1


def test_random_string(client):
    r = client.post("/api/string/random-string", json={"length": 8})
    assert len(r.json()["value"]) == 8


def test_shuffle_letters(client):
    r = client.post("/api/string/shuffle", json={"text": "abc"})
    assert sorted(r.json()["value"]) == ["a", "b", "c"]
