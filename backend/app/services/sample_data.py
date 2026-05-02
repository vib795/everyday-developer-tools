import uuid
from datetime import datetime
from random import choice, randint
from typing import Any

import exrex


def generate_sample_data(schema: dict[str, Any]) -> Any:
    """Generate sample data matching the given JSON schema.

    Handles object/array/string/number/integer/boolean/null types, allOf/anyOf/oneOf
    composition, simple if/then/else conditionals, enum constraints, regex patterns,
    and known string formats (date-time, email, uuid).
    """
    return _generate(schema)


def _generate(schema: dict[str, Any]) -> Any:
    if "type" not in schema:
        return {}

    if schema["type"] == "object":
        obj: dict[str, Any] = {}
        for key in ("allOf", "anyOf", "oneOf"):
            if key in schema:
                if key in ("anyOf", "oneOf"):
                    obj.update(_generate(choice(schema[key])))
                else:  # allOf
                    for sub in schema[key]:
                        obj.update(_generate(sub))
        for prop, prop_schema in schema.get("properties", {}).items():
            if "if" in schema and prop in schema["if"].get("properties", {}):
                if choice([True, False]):
                    obj.update(_generate(schema["then"]))
                else:
                    obj.update(_generate(schema.get("else", {})))
            else:
                obj[prop] = _generate(prop_schema)
        return obj

    if schema["type"] == "array":
        item_schema = schema.get("items", {})
        return [_generate(item_schema) for _ in range(randint(1, 3))]

    if schema["type"] == "string":
        if "enum" in schema:
            return choice(schema["enum"])
        if "pattern" in schema:
            return exrex.getone(schema["pattern"])
        fmt = schema.get("format", "")
        if fmt == "date-time":
            return datetime.now().isoformat()
        if fmt == "email":
            return "example@example.com"
        if fmt == "uuid":
            return str(uuid.uuid4())
        return "example string"

    if schema["type"] == "number":
        min_value = schema.get("minimum", float("-inf"))
        max_value = schema.get("maximum", float("inf"))
        if min_value == float("-inf") and max_value == float("inf"):
            return 123.45
        if min_value == float("-inf"):
            return min(max_value - 1, 123.45)
        if max_value == float("inf"):
            return max(min_value + 1, 123.45)
        return (min_value + max_value) / 2

    if schema["type"] == "integer":
        return 123
    if schema["type"] == "boolean":
        return choice([True, False])
    if schema["type"] == "null":
        return None
    return {}
