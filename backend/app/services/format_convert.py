"""Convert between JSON / YAML / TOML / XML / CSV.

Conversions go through Python objects: source.parse() → target.dump().
CSV is constrained: round-trips a list-of-dicts shape.
"""
from __future__ import annotations

import csv
import io
import json
import sys
from typing import Any

import xmltodict
import yaml

if sys.version_info >= (3, 11):
    import tomllib
else:  # pragma: no cover
    import tomli as tomllib

import tomli_w


def _from_csv(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]


def _to_csv(data: Any) -> str:
    if not isinstance(data, list) or not data or not isinstance(data[0], dict):
        raise ValueError("CSV target requires a JSON array of objects")
    fieldnames: list[str] = []
    for row in data:
        for k in row.keys():
            if k not in fieldnames:
                fieldnames.append(k)
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=fieldnames)
    writer.writeheader()
    for row in data:
        writer.writerow({k: ("" if row.get(k) is None else row.get(k)) for k in fieldnames})
    return out.getvalue()


def _from_xml(text: str) -> Any:
    return xmltodict.parse(text)


def _to_xml(data: Any) -> str:
    if not isinstance(data, dict) or len(data) != 1:
        # xmltodict requires a single root element.
        return xmltodict.unparse({"root": data}, pretty=True)
    return xmltodict.unparse(data, pretty=True)


def parse(text: str, fmt: str) -> Any:
    if fmt == "json":
        return json.loads(text)
    if fmt == "yaml":
        return yaml.safe_load(text)
    if fmt == "toml":
        return tomllib.loads(text)
    if fmt == "xml":
        return _from_xml(text)
    if fmt == "csv":
        return _from_csv(text)
    raise ValueError(f"unknown source format: {fmt}")


def dump(data: Any, fmt: str) -> str:
    if fmt == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    if fmt == "yaml":
        return yaml.safe_dump(data, sort_keys=False, allow_unicode=True)
    if fmt == "toml":
        if not isinstance(data, dict):
            raise ValueError("TOML target requires a top-level object")
        return tomli_w.dumps(data)
    if fmt == "xml":
        return _to_xml(data)
    if fmt == "csv":
        return _to_csv(data)
    raise ValueError(f"unknown target format: {fmt}")
