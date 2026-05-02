import json
import logging
from typing import Any

from genson import SchemaBuilder

logger = logging.getLogger(__name__)

DRAFT_04 = "http://json-schema.org/draft-04/schema#"


def generate_json_schema(json_input: str, conditionals: list[dict] | None = None) -> dict[str, Any]:
    try:
        json_data = json.loads(json_input)
    except json.JSONDecodeError as e:
        logger.error("Schema generator received invalid JSON: %s", e)
        raise ValueError("Invalid JSON input.") from e

    builder = SchemaBuilder(schema_uri=DRAFT_04)
    builder.add_object(json_data)
    schema = builder.to_schema()
    schema["$schema"] = DRAFT_04

    if conditionals:
        apply_conditions_to_schema(schema, conditionals)
    return schema


def apply_conditions_to_schema(schema: dict[str, Any], conditions: list[dict]) -> None:
    for condition in conditions:
        path_parts = condition["path"].split(".")
        current = schema

        for part in path_parts[:-1]:
            if part:
                current.setdefault("properties", {})
                current["properties"].setdefault(part, {})
                current = current["properties"][part]

        target_key = path_parts[-1]
        if target_key:
            current.setdefault("properties", {})
            current["properties"][target_key] = condition["condition"]
        else:
            schema.update(condition["condition"])
