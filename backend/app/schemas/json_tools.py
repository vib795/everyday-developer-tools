from typing import Any

from pydantic import BaseModel, Field


class JsonValidateRequest(BaseModel):
    json_input: str = Field(..., description="JSON document to validate.")
    schema_input: str | None = Field(None, description="Optional JSON Schema to validate against.")


class JsonValidateResponse(BaseModel):
    valid: bool
    message: str
    formatted_json: str | None = None
    error_details: str | None = None


class JsonSchemaRequest(BaseModel):
    json_input: str
    conditionals: list[dict[str, Any]] | None = None


class JsonSchemaResponse(BaseModel):
    schema_: dict[str, Any] = Field(..., alias="schema")

    model_config = {"populate_by_name": True}


class JsonSampleRequest(BaseModel):
    schema_input: str = Field(..., description="JSON Schema (as a string) to generate from.")


class JsonSampleResponse(BaseModel):
    sample: Any


class JsonConvertRequest(BaseModel):
    input_data: str
    conversion_type: str = Field(..., description="'to_json' or 'to_string'")


class JsonConvertResponse(BaseModel):
    output: str


class JsonParseRequest(BaseModel):
    input_json: str


class JsonParseResponse(BaseModel):
    output: str
