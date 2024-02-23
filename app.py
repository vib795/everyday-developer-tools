from flask import Flask, render_template, request, redirect, url_for
import qrcode  # For QR Code generation
import difflib  # For Diff viewer
import re  # For Regex checking
from jsonschema import validate
from jsonschema.exceptions import ValidationError  # For JSON validation
import json
from genson import SchemaBuilder

app = Flask(__name__)

# Route for the home page, redirects to the Diff Viewer
@app.route('/')
def home():
    return redirect(url_for('diff_viewer'))

# Diff Viewer Page
@app.route('/diff-viewer', methods=['GET', 'POST'])
def diff_viewer():
    diff_result = None
    text1 = ""
    text2 = ""
    if request.method == 'POST':
        # Retrieve text inputs
        text1 = request.form.get('text1', '')
        text2 = request.form.get('text2', '')
        # Generate diff result
        diff_result = difflib.HtmlDiff().make_file(text1.splitlines(), text2.splitlines(), fromdesc="Text 1", todesc="Text 2")
    # Pass the inputs back to the template, along with the diff result
    return render_template('diff_viewer.html', diff_result=diff_result, text1=text1, text2=text2)

# @app.route('/diff-viewer', methods=['GET', 'POST'])
# def diff_viewer():
#     diff_result = None
#     text1 = ""
#     text2 = ""
#     if request.method == 'POST':
#         text1 = request.form.get('text1', '')
#         text2 = request.form.get('text2', '')
#         # Use difflib to generate an HTML diff view
#         diff_result = difflib.HtmlDiff().make_file(text1.splitlines(), text2.splitlines(), fromdesc="Text 1", todesc="Text 2", context=True, numlines=3)
#     return render_template('diff_viewer.html', diff_result=diff_result, text1=text1, text2=text2)

# @app.route('/diff-viewer', methods=['GET', 'POST'])
# def diff_viewer():
#     diff_result = None
#     text1 = ""
#     text2 = ""
#     if request.method == 'POST':
#         text1 = request.form.get('text1', '')
#         text2 = request.form.get('text2', '')
        
#         # Initialize HtmlDiff object
#         hd = difflib.HtmlDiff()

#         # Generate HTML diff - set context to True to show full file content
#         # If you want to limit the number of context lines, you can adjust numlines parameter
#         diff_result = hd.make_file(text1.splitlines(keepends=True), 
#                                    text2.splitlines(keepends=True), 
#                                    fromdesc="Text 1", 
#                                    todesc="Text 2",
#                                    context=True) # Show full content with diffs highlighted

#     return render_template('diff_viewer.html', diff_result=diff_result, text1=text1, text2=text2)



# JSON schema generator
def generate_json_schema(json_input):
    try:
        json_data = json.loads(json_input)
        builder = SchemaBuilder()
        builder.add_object(json_data)
        return builder.to_schema()
    except json.JSONDecodeError as e:
        raise ValueError("Invalid JSON input.") from e
    except Exception as e:
        raise ValueError("An error occurred while generating the schema: " + str(e)) from e

@app.route('/json-schema-generator', methods=['GET', 'POST'])
def json_schema_generator():
    schema_result = None
    schema_for_copying = None
    json_input = ""
    if request.method == 'POST':
        json_input = request.form.get('json_input', '')
        try:
            generated_schema = generate_json_schema(json_input)
            schema_for_copying = json.dumps(generated_schema, indent=2)
            # Add line numbers for display
            schema_with_lines = "\n".join(f"{i+1}: {line}" for i, line in enumerate(schema_for_copying.splitlines()))
            schema_result = schema_with_lines
        except ValueError as e:
            schema_result = str(e)
    return render_template('json_schema_generator.html', json_input=json_input, schema_result=schema_result, schema_for_copying=schema_for_copying)


@app.route('/json-validator', methods=['GET', 'POST'])
def json_validator():
    validation_result = None
    error_details = None
    original_json = None  # This will hold the input with line numbers
    formatted_json_with_lines = None
    json_input = ""  # Initialize json_input to ensure it's always defined
    schema_input = None  # Initialize schema_input
    if request.method == 'POST':
        json_input = request.form.get('json_input', '')
        schema_input = request.form.get('schema_input', None)  # Get schema input, if provided
        # Add line numbers to the original input
        original_json = "\n".join(f"{i+1:3}: {line}" for i, line in enumerate(json_input.splitlines()))
        try:
            parsed_json = json.loads(json_input)
            # If schema_input is provided, parse and validate against the schema
            if schema_input:
                parsed_schema = json.loads(schema_input)
                validate(instance=parsed_json, schema=parsed_schema)
                validation_result = "JSON is valid and conforms to the schema."
            else:
                validation_result = "JSON is valid."
            # Format the valid JSON
            formatted_json = json.dumps(parsed_json, indent=2)
            # Add line numbers to the formatted output
            formatted_json_with_lines = "\n".join(f"{i+1:3}: {line}" for i, line in enumerate(formatted_json.splitlines()))
        except json.JSONDecodeError as e:
            validation_result = "Invalid JSON: The input is not a valid JSON format."
            error_details = f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
        except ValidationError as e:
            validation_result = f"Invalid JSON: Schema validation error - {e.message}."
        except Exception as e:
            validation_result = "An unexpected error occurred. Please check the JSON format and schema."
            error_details = str(e)
    # Pass the raw json_input and optionally schema_input back to the template, along with other variables
    return render_template('json_validator.html', validation_result=validation_result, original_json=original_json, formatted_json_with_lines=formatted_json_with_lines, json_input=json_input, schema_input=schema_input, error_details=error_details)

# QR Code Generator Page
@app.route('/qr-generator', methods=['GET', 'POST'])
def qr_generator():
    qr_img = None
    if request.method == 'POST':
        # Generate QR Code
        data = request.form.get('data', '')
        img = qrcode.make(data)
        img_path = 'static/qr_code.png'
        img.save(img_path)
        qr_img = url_for('static', filename='qr_code.png')
    return render_template('qr_generator.html', qr_img=qr_img)

@app.route('/regex-checker', methods=['GET', 'POST'])
def regex_checker():
    match_result = None
    regex_pattern = ''
    test_string = ''
    if request.method == 'POST':
        regex_pattern = request.form.get('regex', '')
        test_string = request.form.get('string', '')
        try:
            # Use re.fullmatch() for exact whole string matching
            if re.fullmatch(regex_pattern, test_string):
                match_result = "Pattern matches the string."
            else:
                match_result = "Pattern does not match the string."
        except re.error as e:
            match_result = f"Regex Error: {e}"

    return render_template('regex_checker.html', match_result=match_result, regex_pattern=regex_pattern, test_string=test_string)


def generate_basic_pattern(text_input):
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

#Regex generator
@app.route('/regex-generator', methods=['GET', 'POST'])
def regex_generator():
    regex_pattern = ""
    text_input = ""  # Ensure text_input is defined outside the condition
    if request.method == 'POST':
        text_input = request.form.get('text_input', '')
        # Email address pattern
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$', text_input):
            regex_pattern = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
        # Phone number pattern (simple example, adjust as needed)
        elif re.match(r'^\+?1?\d{10,15}$', text_input):
            regex_pattern = "\+?1?\d{10,15}"
        # Birthday pattern (in the format YYYY-MM-DD)
        elif re.match(r'^\d{4}-\d{2}-\d{2}$', text_input):
            regex_pattern = "\d{4}-\d{2}-\d{2}"
        # SSN pattern (simple example, adjust as needed)
        elif re.match(r'^\d{3}-\d{2}-\d{4}$', text_input):
            regex_pattern = "\d{3}-\d{2}-\d{4}"
        else:
            regex_pattern = generate_basic_pattern(text_input)

    return render_template('regex_generator.html', regex_pattern=regex_pattern, text_input=text_input)

if __name__ == '__main__':
    app.run(debug=True)
