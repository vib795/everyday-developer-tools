import json
import logging

from fastapi import APIRouter, HTTPException, Request
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from ..rate_limit import limiter
from ..schemas.json_tools import (
    JsonConvertRequest,
    JsonConvertResponse,
    JsonParseRequest,
    JsonParseResponse,
    JsonSampleRequest,
    JsonSampleResponse,
    JsonSchemaRequest,
    JsonSchemaResponse,
    JsonValidateRequest,
    JsonValidateResponse,
)
from ..services.json_schema import generate_json_schema
from ..services.sample_data import generate_sample_data
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/json", tags=["json"])


@router.post("/validate", response_model=JsonValidateResponse)
def validate_json(payload: JsonValidateRequest) -> JsonValidateResponse:
    try:
        parsed = json.loads(payload.json_input)
    except json.JSONDecodeError as e:
        return JsonValidateResponse(
            valid=False,
            message="Invalid JSON: The input is not a valid JSON format.",
            error_details=f"Error at line {e.lineno}, column {e.colno}: {e.msg}",
        )

    formatted = json.dumps(parsed, indent=2)
    message = "JSON is valid."

    if payload.schema_input:
        try:
            schema = json.loads(payload.schema_input)
            validate(instance=parsed, schema=schema)
            message += " JSON is valid against the provided schema."
        except json.JSONDecodeError as e:
            return JsonValidateResponse(
                valid=False,
                message="Invalid Schema: The schema is not valid JSON.",
                formatted_json=formatted,
                error_details=f"Error at line {e.lineno}, column {e.colno}: {e.msg}",
            )
        except ValidationError as e:
            return JsonValidateResponse(
                valid=False,
                message="Invalid JSON: Schema validation error.",
                formatted_json=formatted,
                error_details=str(e),
            )

    return JsonValidateResponse(valid=True, message=message, formatted_json=formatted)


@router.post("/schema", response_model=JsonSchemaResponse)
def schema_from_json(payload: JsonSchemaRequest) -> JsonSchemaResponse:
    try:
        result = generate_json_schema(payload.json_input, conditionals=payload.conditionals)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return JsonSchemaResponse.model_validate({"schema": result})


@router.post("/sample", response_model=JsonSampleResponse)
@limiter.limit(settings.rate_limit_json_sample)
def sample_from_schema(request: Request, payload: JsonSampleRequest) -> JsonSampleResponse:
    try:
        schema = json.loads(payload.schema_input)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid schema JSON: {e.msg}")
    try:
        sample = generate_sample_data(schema)
    except Exception as e:  # noqa: BLE001 - exrex etc.
        logger.error("Sample generation failed: %s", e)
        raise HTTPException(status_code=400, detail=f"Error generating sample data: {e}")
    return JsonSampleResponse(sample=sample)


@router.post("/convert", response_model=JsonConvertResponse)
def json_convert(payload: JsonConvertRequest) -> JsonConvertResponse:
    if payload.conversion_type not in ("to_json", "to_string"):
        raise HTTPException(status_code=400, detail="Invalid conversion type specified.")
    try:
        if payload.conversion_type == "to_json":
            processed = payload.input_data.encode().decode("unicode_escape")
            if processed.startswith('"') and processed.endswith('"'):
                processed = processed[1:-1]
            processed = processed.replace('\\"', '"')
            obj = json.loads(processed)
            return JsonConvertResponse(output=json.dumps(obj, indent=4, sort_keys=True))

        obj = json.loads(payload.input_data)
        as_string = json.dumps(obj)
        escaped = as_string.replace('"', '\\"')
        return JsonConvertResponse(output=f'"{escaped}"')
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Error during conversion: {e}")


@router.post("/parse", response_model=JsonParseResponse)
def json_parse(payload: JsonParseRequest) -> JsonParseResponse:
    try:
        obj = json.loads(payload.input_json)
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}",
        )
    return JsonParseResponse(output=json.dumps(obj, indent=4))
