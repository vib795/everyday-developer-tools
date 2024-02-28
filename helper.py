import json
from genson import SchemaBuilder
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_json_schema(json_input, conditionals=None):
    try:
        json_data = json.loads(json_input)
        builder = SchemaBuilder(schema_uri="http://json-schema.org/draft-04/schema#")
        builder.add_object(json_data)
        base_schema = builder.to_schema()

        base_schema['$schema'] = "http://json-schema.org/draft-04/schema#"

        if conditionals:
            apply_conditions_to_schema(base_schema, conditionals)

        return base_schema
    except json.JSONDecodeError as e:
        logger.error(f"An error occurred decoding JSON: {str(e)}")
        raise ValueError("Invalid JSON input.") from e
    except Exception as e:
        logger.error(f"An error occurred in schema generation: {str(e)}")
        raise ValueError("An error occurred while generating the schema.") from e

def apply_conditions_to_schema(schema, conditions):
    for condition in conditions:
        path_parts = condition["path"].split('.')
        current = schema

        # Iterate through the path to find or create the target location
        for part in path_parts[:-1]:
            if part:  # Skip any empty parts which could indicate a misplaced dot or root-level indication
                if 'properties' not in current:
                    current['properties'] = {}
                if part not in current['properties']:
                    current['properties'][part] = {}
                current = current['properties'][part]

        # Apply the condition at the specified path
        # If the path is empty or ends with a dot, apply the condition at the current level
        target_key = path_parts[-1]
        if target_key:  # Non-root condition
            if 'properties' not in current:
                current['properties'] = {}
            current['properties'][target_key] = condition["condition"]
        else:  # Root-level condition
            schema.update(condition["condition"])

def generate_basic_pattern(text_input):
    try:
        # Initialize sets to hold unique character types
        char_types = {
            'lower': False,
            'upper': False,
            'digit': False,
            'special': set()
        }

        # Analyze the input to determine which character types it contains
        for char in text_input:
            if char.islower():
                char_types['lower'] = True
            elif char.isupper():
                char_types['upper'] = True
            elif char.isdigit():
                char_types['digit'] = True
            else:
                # Add special characters to the set, escaping them as needed
                char_types['special'].add(re.escape(char))

        # Build the regex pattern from the collected character types
        pattern_parts = []
        if char_types['lower']:
            pattern_parts.append('a-z')
        if char_types['upper']:
            pattern_parts.append('A-Z')
        if char_types['digit']:
            pattern_parts.append('0-9')
        # Combine special characters into a single string if present
        if char_types['special']:
            pattern_parts.append(''.join(char_types['special']))

        # Form the final pattern
        regex_pattern = f"[{''.join(pattern_parts)}]{{{len(text_input)}}}"
        return regex_pattern
    except Exception as e:
        logger.error(f"An error occurred. {str(e)}")
