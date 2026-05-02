import json


# Format converters

def test_json_to_yaml(client):
    r = client.post(
        "/api/convert/format",
        json={"text": '{"a": 1, "b": [2, 3]}', "source": "json", "target": "yaml"},
    )
    body = r.json()
    assert body["error"] is None
    assert "a: 1" in body["output"]
    assert "- 2" in body["output"]


def test_yaml_to_json_round_trip(client):
    yaml_text = "name: alice\nlangs:\n  - py\n  - js\n"
    r = client.post(
        "/api/convert/format",
        json={"text": yaml_text, "source": "yaml", "target": "json"},
    )
    obj = json.loads(r.json()["output"])
    assert obj == {"name": "alice", "langs": ["py", "js"]}


def test_json_to_toml(client):
    r = client.post(
        "/api/convert/format",
        json={"text": '{"server": {"host": "x", "port": 80}}', "source": "json", "target": "toml"},
    )
    out = r.json()["output"]
    assert "[server]" in out
    assert 'host = "x"' in out
    assert "port = 80" in out


def test_toml_to_json(client):
    toml_text = '[server]\nhost = "x"\nport = 80\n'
    r = client.post(
        "/api/convert/format",
        json={"text": toml_text, "source": "toml", "target": "json"},
    )
    obj = json.loads(r.json()["output"])
    assert obj == {"server": {"host": "x", "port": 80}}


def test_xml_to_json(client):
    xml_text = "<root><a>1</a><b>2</b></root>"
    r = client.post(
        "/api/convert/format",
        json={"text": xml_text, "source": "xml", "target": "json"},
    )
    obj = json.loads(r.json()["output"])
    assert obj == {"root": {"a": "1", "b": "2"}}


def test_json_to_xml(client):
    r = client.post(
        "/api/convert/format",
        json={"text": '{"root": {"a": "1"}}', "source": "json", "target": "xml"},
    )
    out = r.json()["output"]
    assert "<root>" in out and "<a>1</a>" in out


def test_csv_to_json(client):
    csv_text = "name,age\nalice,30\nbob,25\n"
    r = client.post(
        "/api/convert/format",
        json={"text": csv_text, "source": "csv", "target": "json"},
    )
    obj = json.loads(r.json()["output"])
    assert obj == [{"name": "alice", "age": "30"}, {"name": "bob", "age": "25"}]


def test_json_to_csv(client):
    r = client.post(
        "/api/convert/format",
        json={
            "text": '[{"name": "alice", "age": 30}, {"name": "bob", "age": 25}]',
            "source": "json",
            "target": "csv",
        },
    )
    out = r.json()["output"].strip().splitlines()
    assert out[0] == "name,age"
    assert "alice,30" in out
    assert "bob,25" in out


def test_format_invalid_source_returns_error(client):
    r = client.post(
        "/api/convert/format",
        json={"text": "{not json", "source": "json", "target": "yaml"},
    )
    assert r.json()["error"] is not None


# JSONPath

def test_jsonpath_basic(client):
    r = client.post(
        "/api/convert/jsonpath",
        json={"json_text": '{"users": [{"name": "a"}, {"name": "b"}]}', "expression": "$.users[*].name"},
    )
    body = r.json()
    assert body["error"] is None
    assert body["matches"] == ["a", "b"]


def test_jsonpath_filter(client):
    r = client.post(
        "/api/convert/jsonpath",
        json={
            "json_text": '{"items":[{"v":1},{"v":2},{"v":3}]}',
            "expression": "$.items[?(@.v > 1)].v",
        },
    )
    assert sorted(r.json()["matches"]) == [2, 3]


def test_jsonpath_invalid_json(client):
    r = client.post(
        "/api/convert/jsonpath",
        json={"json_text": "not json", "expression": "$"},
    )
    assert "Invalid JSON" in r.json()["error"]


def test_jsonpath_invalid_expr(client):
    r = client.post(
        "/api/convert/jsonpath",
        json={"json_text": "{}", "expression": "$[]["},
    )
    assert "Invalid JSONPath" in r.json()["error"]


# cURL converter

def test_curl_simple_get(client):
    r = client.post(
        "/api/convert/curl",
        json={"curl": 'curl https://api.example.com/u'},
    )
    outs = r.json()["outputs"]
    assert "fetch(" in outs["fetch"]
    assert "axios(" in outs["axios"]
    assert "requests.get" in outs["requests"]
    assert "https://api.example.com/u" in outs["requests"]


def test_curl_post_json_body(client):
    cmd = (
        'curl -X POST https://api.example.com/u '
        '-H "Content-Type: application/json" '
        "-d '{\"name\":\"alice\"}'"
    )
    r = client.post("/api/convert/curl", json={"curl": cmd})
    outs = r.json()["outputs"]
    assert "POST" in outs["fetch"]
    assert "alice" in outs["fetch"]
    # requests should detect JSON body and use json= kwarg
    assert "json=" in outs["requests"]
    assert "requests.post" in outs["requests"]


def test_curl_with_basic_auth(client):
    r = client.post(
        "/api/convert/curl",
        json={"curl": "curl -u alice:secret https://api.example.com/"},
    )
    outs = r.json()["outputs"]
    assert "alice" in outs["requests"] and "secret" in outs["requests"]


def test_curl_get_with_data_promoted_to_query(client):
    r = client.post(
        "/api/convert/curl",
        json={"curl": "curl -G -d 'q=hello' -d 'lang=py' https://api.example.com/search"},
    )
    outs = r.json()["outputs"]
    assert "?q=hello&lang=py" in outs["requests"]
    assert "requests.get" in outs["requests"]


def test_curl_invalid_returns_error(client):
    r = client.post("/api/convert/curl", json={"curl": "curl"})
    assert r.json()["error"] is not None
