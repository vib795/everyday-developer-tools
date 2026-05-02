"""Parse a single `curl ...` invocation into language-specific HTTP-client snippets.

Supports common flags: -X, -H/--header, -d/--data/--data-raw/--data-binary/--data-urlencode,
-u/--user, --form, --compressed, -G/--get. Newline continuations (\\) and shell quoting are honored.
"""
from __future__ import annotations

import json
import shlex
from typing import Any
from urllib.parse import parse_qsl, urlencode


def parse_curl(curl: str) -> dict[str, Any]:
    raw = curl.replace("\\\n", " ").strip()
    if raw.startswith("curl"):
        raw = raw[4:].strip()
    tokens = shlex.split(raw, posix=True)

    method = "GET"
    url: str | None = None
    headers: dict[str, str] = {}
    data: list[str] = []
    user: str | None = None
    is_form = False
    is_get_with_data = False

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("-X", "--request"):
            method = tokens[i + 1].upper()
            i += 2
            continue
        if tok in ("-H", "--header"):
            kv = tokens[i + 1]
            if ":" in kv:
                k, v = kv.split(":", 1)
                headers[k.strip()] = v.strip()
            i += 2
            continue
        if tok in ("-d", "--data", "--data-raw", "--data-binary", "--data-urlencode"):
            data.append(tokens[i + 1])
            if method == "GET":
                method = "POST"
            i += 2
            continue
        if tok in ("-u", "--user"):
            user = tokens[i + 1]
            i += 2
            continue
        if tok in ("-F", "--form"):
            is_form = True
            data.append(tokens[i + 1])
            if method == "GET":
                method = "POST"
            i += 2
            continue
        if tok in ("-G", "--get"):
            is_get_with_data = True
            i += 1
            continue
        if tok in ("--compressed", "-i", "-I", "-s", "-v", "-k", "--insecure", "-L"):
            i += 1
            continue
        if tok.startswith("-"):
            # Unknown flag — skip the next token if it doesn't start with -.
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("-"):
                i += 2
            else:
                i += 1
            continue
        if url is None:
            url = tok
        i += 1

    if url is None:
        raise ValueError("URL not found in curl command")

    body_text = "&".join(data) if data else None
    if is_get_with_data and body_text:
        sep = "&" if "?" in url else "?"
        url = f"{url}{sep}{body_text}"
        body_text = None
        method = "GET"

    return {
        "method": method,
        "url": url,
        "headers": headers,
        "body": body_text,
        "user": user,
        "is_form": is_form,
    }


def _pretty_json_body(body: str | None) -> Any | None:
    if not body:
        return None
    try:
        return json.loads(body)
    except (ValueError, TypeError):
        return None


def to_fetch(parsed: dict[str, Any]) -> str:
    init: dict[str, Any] = {"method": parsed["method"]}
    if parsed["headers"]:
        init["headers"] = parsed["headers"]
    if parsed["body"]:
        init["body"] = parsed["body"]
    body_str = json.dumps(init, indent=2)
    return f'fetch({json.dumps(parsed["url"])}, {body_str})\n  .then((r) => r.json())\n  .then(console.log);'


def to_axios(parsed: dict[str, Any]) -> str:
    cfg: dict[str, Any] = {
        "method": parsed["method"].lower(),
        "url": parsed["url"],
    }
    if parsed["headers"]:
        cfg["headers"] = parsed["headers"]
    body_obj = _pretty_json_body(parsed["body"])
    if body_obj is not None:
        cfg["data"] = body_obj
    elif parsed["body"]:
        cfg["data"] = parsed["body"]
    return f"axios({json.dumps(cfg, indent=2)});"


def to_requests(parsed: dict[str, Any]) -> str:
    method = parsed["method"].lower()
    args = [f'    "{parsed["url"]}"']
    if parsed["headers"]:
        args.append(f"    headers={json.dumps(parsed['headers'])}")
    if parsed["body"]:
        body_obj = _pretty_json_body(parsed["body"])
        if body_obj is not None:
            args.append(f"    json={json.dumps(body_obj)}")
        else:
            try:
                form = dict(parse_qsl(parsed["body"], keep_blank_values=True))
                if form:
                    args.append(f"    data={json.dumps(form)}")
                else:
                    args.append(f"    data={json.dumps(parsed['body'])}")
            except Exception:  # noqa: BLE001
                args.append(f"    data={json.dumps(parsed['body'])}")
    if parsed["user"]:
        u = parsed["user"]
        if ":" in u:
            user, pwd = u.split(":", 1)
            args.append(f'    auth=("{user}", "{pwd}")')
        else:
            args.append(f'    auth=("{u}", "")')
    body = ",\n".join(args)
    return f"import requests\n\nresp = requests.{method}(\n{body},\n)\nprint(resp.json())"


def convert_curl(curl: str) -> dict[str, str]:
    parsed = parse_curl(curl)
    # Sanity rebuild of body for fetch when JSON body parses cleanly.
    body_obj = _pretty_json_body(parsed["body"])
    if body_obj is not None:
        parsed["body"] = json.dumps(body_obj)
    elif parsed["body"]:
        # Normalize URL-encoded strings so they don't shell-quote oddly.
        try:
            kv = list(parse_qsl(parsed["body"], keep_blank_values=True))
            if kv:
                parsed["body"] = urlencode(kv)
        except Exception:  # noqa: BLE001
            pass
    return {
        "fetch": to_fetch(parsed),
        "axios": to_axios(parsed),
        "requests": to_requests(parsed),
    }
