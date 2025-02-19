import json
from genson import SchemaBuilder
import logging
import re
import uuid
from random import choice, randint
from datetime import datetime
import exrex
import random
import uuid
from faker import Faker
from faker.providers import automotive
from random import choice, randint

logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()
fake.add_provider(automotive)

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

def generate_sample_data(schema):
    """
    Generates sample data for more complex JSON schemas, including handling
    conditional properties, compositions (allOf, anyOf, oneOf), specific data formats,
    and generating UUIDs for properties that specify a UUID format.
    
    Args:
        schema (dict): A JSON schema.
    
    Returns:
        dict: Sample data adhering to the given schema.
    """
    def generate_from_schema(schema):
        if "type" not in schema:
            return {}

        if schema["type"] == "object":
            obj = {}
            # Handle allOf, anyOf, oneOf by merging their properties or choosing one respectively
            for key in ["allOf", "anyOf", "oneOf"]:
                if key in schema:
                    if key == "anyOf" or key == "oneOf":
                        chosen_schema = choice(schema[key])
                        obj.update(generate_from_schema(chosen_schema))
                    elif key == "allOf":
                        for subschema in schema[key]:
                            obj.update(generate_from_schema(subschema))
            for prop, prop_schema in schema.get("properties", {}).items():
                # Conditional handling (simple example)
                if "if" in schema and prop in schema["if"].get("properties", {}):
                    if_choice = choice([True, False])
                    if if_choice:
                        obj.update(generate_from_schema(schema["then"]))
                    else:
                        obj.update(generate_from_schema(schema.get("else", {})))
                else:
                    obj[prop] = generate_from_schema(prop_schema)
            return obj
        elif schema["type"] == "array":
            item_schema = schema.get("items", {})
            # Generates an array with a random length of 1 to 3 items
            return [generate_from_schema(item_schema) for _ in range(randint(1, 3))]
        elif schema["type"] == "string":
            # Check for enum constraint
            if "enum" in schema:
                # Randomly choose one of the options from the enum list
                return choice(schema["enum"])
            pattern = schema.get("pattern")
            if pattern:
                return exrex.getone(pattern)
            # Handle other formats like 'date-time', 'email', 'uuid', etc.
            format = schema.get("format", "")
            if format == "date-time":
                return datetime.now().isoformat()
            elif format == "email":
                return "example@example.com"
            elif format == "uuid":
                return str(uuid.uuid4())
            else:
                return "example string"
        elif schema["type"] == "number":
            # Check if there's a minimum or maximum specified
            min_value = schema.get("minimum", float('-inf'))
            max_value = schema.get("maximum", float('inf'))
            # Generate a random number within the range
            # This is a simple case where we assume the range is not too narrow
            # For more precise control over the range, you might use a library like `numpy`
            if min_value == float('-inf') and max_value == float('inf'):
                # No bounds defined
                return 123.45
            elif min_value == float('-inf'):
                # Only maximum is defined
                return min(max_value - 1, 123.45)
            elif max_value == float('inf'):
                # Only minimum is defined
                return max(min_value + 1, 123.45)
            else:
                # Both minimum and maximum are defined
                return (min_value + max_value) / 2  # Or any other logic to pick a number within the range
            # return 123.45
        elif schema["type"] == "integer":
            return 123
        elif schema["type"] == "boolean":
            return choice([True, False])
        elif schema["type"] == "null":
            return None
        else:
            return {}

    return generate_from_schema(schema)

def generate_sample(data):
    if isinstance(data, dict):
        sample = {}
        for key, value in data.items():
            if key == "parameters" and isinstance(value, list):
                sample[key] = [generate_parameter_sample(param) for param in value]
            else:
                sample[key] = generate_sample(value) if key != "parameters" else value
        return sample
    elif isinstance(data, list):
        return [generate_sample(data[0]) if data else {}]
    else:
        return data

def generate_sample_value(type_str):
    if type_str == 'string':
        return "sample_string"
    elif type_str == 'int':
        return 123
    elif type_str == 'float':
        return 123.45
    elif type_str == 'bool':
        return True
    elif type_str == 'uuid':
        return str(uuid.uuid4())
    else:
        return "sample_value"

def generate_parameter_sample(param):
    sample = {}
    for key, value in param.items():
        if key == 'name':
            sample[key] = generate_sample_value(param.get('type', 'string'))
        else:
            sample[key] = value
    return sample


def generate_fake_data(field_names, field_types, num_records):
    fake = Faker()
    car_models = {
        'BMW': ['M3', 'M5', '3 Series', '5 Series', '7 Series', 'X3', 'X5', 'X7', 'M8', 'iX', 'i4', 'X6'],
        'Mercedes-Benz': ['C-Class', 'E-Class', 'S-Class', 'GLC', 'GLE', 'G-Wagon', 'GLA', 'GLB', 'GLS', 'AMG GT'],
        'Audi': ['A3', 'A4', 'A6', 'Q3', 'Q5', 'Q7', 'RS6', 'RS7', 'e-tron', 'A8', 'Q8', 'R8'],
        'Toyota': ['Camry', 'Corolla', 'RAV4', 'Highlander', '4Runner', 'Tundra', 'Tacoma', 'Prius', 'Sienna', 'Land Cruiser'],
        'Honda': ['Civic', 'Accord', 'CR-V', 'Pilot', 'Odyssey', 'Ridgeline', 'HR-V', 'Passport', 'Fit'],
        'Ford': ['F-150', 'Mustang', 'Explorer', 'Bronco', 'Escape', 'Edge', 'Ranger', 'Expedition', 'Mach-E'],
        'Tesla': ['Model 3', 'Model Y', 'Model S', 'Model X', 'Cybertruck', 'Roadster'],
        'Porsche': ['911', 'Cayenne', 'Macan', 'Panamera', 'Taycan', '718 Cayman', '718 Boxster', 'GT3', 'GT2 RS'],
        'Ferrari': ['488', 'F8 Tributo', 'SF90', 'Roma', '812', 'Portofino', 'LaFerrari'],
        'Lamborghini': ['Urus', 'Huracán', 'Aventador', 'Revuelto', 'Countach']
    }
    faker_methods = {
        'name': fake.name,
        'email': fake.email,
        'phone': lambda: f"({randint(100,999)})-{randint(100,999)}-{randint(1000,9999)}",
        'address': fake.address,
        'company': fake.company,
        'job': fake.job,
        'date': lambda: fake.date_time().strftime('%Y-%m-%d %H:%M:%S'),
        'number': lambda: fake.random_number(digits=5),
        'text': fake.text,
        'boolean': fake.boolean,
        'uuid': lambda: str(uuid.uuid4()),
        'url': fake.url,
        'ip': fake.ipv4,
        'credit_card': fake.credit_card_number,
        'car_make': lambda: choice(list(car_models.keys())),
        'car_model': lambda current_data: choice(car_models[current_data.get('car_make', choice(list(car_models.keys())))]),
        'car_vin': fake.vin,
        'car_year': lambda: randint(1990, 2024),
        'car_color': fake.color_name,
        'car_fuel': lambda: choice(['Gasoline', 'Diesel', 'Electric', 'Hybrid']),
        'car_transmission': lambda: choice(['Automatic', 'Manual']),
        'license_plate': fake.license_plate
    }
    
    data = []
    for _ in range(num_records):
        record = {}
        make = None
        
        for name, type_ in zip(field_names, field_types):
            if type_ == 'car_make':
                make = choice(list(car_models.keys()))
                record[name] = make
            elif type_ == 'car_model' and make:
                record[name] = choice(car_models[make])
            elif type_ == 'car_model':  # If model is requested before make
                make = choice(list(car_models.keys()))
                record[name] = choice(car_models[make])
            else:
                if type_ in faker_methods:
                    record[name] = faker_methods[type_]()
                    
        data.append(record)
    
    return data