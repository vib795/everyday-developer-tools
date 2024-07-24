from imports import *

log_dir = os.getenv("LOG_DIRECTORY", "logs/")
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file_path = os.path.join(log_dir, "application.log")
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(log_file_path),
                        logging.StreamHandler()
                    ])
logger = logging.getLogger(__name__)
logger.info("Logging system initialized")

app = Flask(__name__)
# limiter = Limiter(key_func=get_remote_address, 
#                   storage_uri="redis://redis:6379", 
#                   default_limits=["15 per minute"])
# limiter.init_app(app)

# Route for the home page
@app.route('/')
@app.route('/home')
def home():
    # return redirect(url_for('diff_viewer'))
    logger.info(f"Home page loaded!!!")
    return render_template('index.html')

# Diff Viewer Page
@app.route('/string-tools/diff-viewer', methods=['GET', 'POST'])
def diff_viewer():
    try:
        diff_result = None
        text1 = ""
        text2 = ""
        if request.method == 'POST':
            # Retrieve text inputs
            text1 = request.form.get('text1', '')
            text2 = request.form.get('text2', '')
            # Generate diff result
            diff_result = difflib.HtmlDiff().make_file(text1.splitlines(), text2.splitlines(), 
                                                    fromdesc="Text 1", todesc="Text 2")
        # Pass the inputs back to the template, along with the diff result
        return render_template('diff_viewer.html', diff_result=diff_result, text1=text1, text2=text2)
    except Exception as e:
        logger.error(f"An error occurred. {(str(e))}")

# JSON schema generator
@app.route('/json-tools/json-schema-generator', methods=['GET', 'POST'])
def json_schema_generator():
    schema_result = None
    schema_for_copying = None
    json_input = ""
    conditionals = ""
    error_message = None

    if request.method == 'POST':
        json_input = request.form.get('json_input', '').strip()
        conditionals_input = request.form.get('conditionals', '').strip()

        if not json_input:
            error_message = "JSON input is empty. Please provide a valid JSON."
        else:
            try:
                conditionals = json.loads(conditionals_input) if conditionals_input else None
                generated_schema = generate_json_schema(json_input, conditionals=conditionals)
                schema_for_copying = json.dumps(generated_schema, indent=2)
                schema_with_lines = "\n".join(f"{i+1}: {line}" for i, line in enumerate(schema_for_copying.splitlines()))
                schema_result = schema_with_lines
            except ValueError as e:
                error_message = f"Error processing input: {e}"

    return render_template('json_schema_generator.html', json_input=json_input, conditionals=conditionals, schema_result=schema_result, schema_for_copying=schema_for_copying, error_message=error_message)

# JSON Validator
@app.route('/json-tools/json-validator', methods=['GET', 'POST'])
def json_validator():
    try:
        validation_result = None
        error_details = None
        formatted_json = None
        formatted_json_with_lines = None
        json_input = ""
        schema_input = ""  # Initialize schema_input
        
        if request.method == 'POST':
            json_input = request.form.get('json_input', '')
            schema_input = request.form.get('schema_input', '').strip()  # Get the schema input from the form
            
            try:
                parsed_json = json.loads(json_input)
                formatted_json = json.dumps(parsed_json, indent=2)
                validation_result = "JSON is valid."
                
                # If schema is provided, validate JSON against the schema
                if schema_input:
                    parsed_schema = json.loads(schema_input)
                    validate(instance=parsed_json, schema=parsed_schema)  # This will raise ValidationError if validation fails
                    validation_result += " JSON is valid against the provided schema."
                
                formatted_json_with_lines = "\n".join(f"{i+1:3}: {line}" for i, line 
                                                    in enumerate(formatted_json.splitlines()))
            except json.JSONDecodeError as e:
                validation_result = "Invalid JSON: The input is not a valid JSON format."
                error_details = f"Error at line {e.lineno}, column {e.colno}: {e.msg}"
            except ValidationError as e:
                validation_result = "Invalid JSON: Schema validation error."
                error_details = str(e)
            except Exception as e:
                validation_result = "An unexpected error occurred. Please check the JSON format and schema."
                
        return render_template('json_validator.html', 
                            validation_result=validation_result, 
                            formatted_json=formatted_json,  
                            formatted_json_with_lines=formatted_json_with_lines,  
                            json_input=json_input, error_details=error_details,
                            schema_input=schema_input)  # Return schema_input to the template
    except Exception as e:
        logger.error(f"An error occurred. {str(e)}")

# RegEx Checker
@app.route('/regex-tools/regex-checker', methods=['GET', 'POST'])
# @limiter.limit("15 per minute")  # Rate limiting
def regex_checker():
    match_result = None
    regex_pattern = ''
    test_string = ''
    if request.method == 'POST':
        regex_pattern = request.form.get('regex', '')
        test_string = request.form.get('string', '')
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(re.fullmatch, regex_pattern, test_string)
            try:
                if future.result(timeout=1):  # 1 second timeout for the regex operation
                    match_result = "Pattern matches the string."
                else:
                    match_result = "Pattern does not match the string."
            except concurrent.futures.TimeoutError:
                match_result = "Execution timed out due to complex/malicious pattern."
            except re.error as e:
                match_result = f"Regex Error: {str(e)}"

    return render_template('regex_checker.html', 
                           match_result=match_result, 
                           regex_pattern=regex_pattern, 
                           test_string=test_string)

#Regex generator
@app.route('/regex-tools/regex-generator', methods=['GET', 'POST'])
def regex_generator():
    try:
        regex_pattern = ""
        text_input = ""  # Ensure text_input is defined outside the condition
        if request.method == 'POST':
            text_input = request.form.get('text_input', '')
            # Email address pattern
            if re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$", text_input):
                regex_pattern = "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}"
            # Phone number pattern (simple example, adjust as needed)
            elif re.match(r"^\+?1?\d{10,15}$", text_input):
                regex_pattern = "\+?1?\d{10,15}"
            # Birthday pattern (in the format YYYY-MM-DD)
            elif re.match(r"^\d{4}-\d{2}-\d{2}$", text_input):
                regex_pattern = "\d{4}-\d{2}-\d{2}"
            # SSN pattern (simple example, adjust as needed)
            elif re.match(r"^\d{3}-\d{2}-\d{4}$", text_input):
                regex_pattern = "\d{3}-\d{2}-\d{4}"
            else:
                regex_pattern = generate_basic_pattern(text_input)

        return render_template('regex_generator.html', 
                            regex_pattern=regex_pattern, 
                            text_input=text_input)
    except Exception as e:
        logger.error(f"An error occurred. {str(e)}")

# JSON COnverter
@app.route('/json-tools/json-converter', methods=['GET', 'POST'])
def json_converter():
    try:
        input_data = ""
        output_data = ""
        conversion_type = ""  # Determines conversion direction: 'to_json' or 'to_string'
        error = None

        if request.method == 'POST':
            input_data = request.form.get('input_data', '')
            conversion_type = request.form.get('conversion_type', '')

            try:
                if conversion_type == 'to_json':
                    # Process for converting string to JSON
                    # Decode the string as a raw string literal
                    processed_input = input_data.encode().decode('unicode_escape')
                    
                    # Strip leading and trailing double quotes if they are extra
                    if processed_input.startswith('"') and processed_input.endswith('"'):
                        processed_input = processed_input[1:-1]
                    
                    # Replace escaped double quotes with actual double quotes
                    processed_input = processed_input.replace('\\"', '"')

                    # Convert string to JSON
                    json_object = json.loads(processed_input)

                    # Format JSON for display
                    output_data = json.dumps(json_object, indent=4, sort_keys=True)
                elif conversion_type == 'to_string':
                    # Process for converting JSON to string
                    # Convert the input string to a JSON object to ensure it's valid JSON
                    json_object = json.loads(input_data)

                    # Convert the JSON object back to a string with special escaping
                    json_string = json.dumps(json_object)
                    escaped_json_string = json_string.replace('"', '\\"')

                    # Wrap the escaped string in additional quotes
                    output_data = f'"{escaped_json_string}"'
                else:
                    error = "Invalid conversion type specified."
            except Exception as e:
                logger.error(f"Error during conversion: {str(e)}")
                error = "Error during conversion: " + str(e)

        return render_template('json_converter.html', 
                            input_data=input_data, 
                            output_data=output_data, 
                            error=error, 
                            conversion_type=conversion_type)
    except Exception as e:
        logger.error(f"An error occurred. {str(e)}")

# Base64 Encoder Decoder
@app.route('/base64', methods=['GET', 'POST'])
def base64_encode_decode():
    try:
        output = ""
        input_text = ""
        operation = "encode"  # Default operation

        if request.method == 'POST':
            input_text = request.form.get('input_text', '')
            operation = request.form.get('operation', 'encode')

            try:
                if operation == 'encode':
                    output = base64.b64encode(input_text.encode()).decode()
                elif operation == 'decode':
                    output = base64.b64decode(input_text.encode()).decode()
            except Exception as e:
                output = f"Error: {str(e)}"

        return render_template('base64_encoder_decoder.html', 
                            output=output, 
                            input_text=input_text, 
                            operation=operation)
    except Exception as e:
        logger.error(f"An error occurred. {str(e)}")

# Word/Character counter
@app.route('/string-tools/counter', methods=['GET', 'POST'])
def counter():
    text_input = ''
    count = 0
    output = ''
    filter_option = request.form.get('filter_option', 'Character')
    custom_delimiter = request.form.get('custom_delimiter', '')

    if request.method == 'POST':
        text_input = request.form.get('text_input', '')
        
        if filter_option == 'Character':
            count = len(text_input)
            output = '\n'.join(text_input)
        elif filter_option == 'Word':
            count = len(text_input.split())
            output = '\n'.join(text_input.split())
        elif filter_option == 'Line':
            count = len(text_input.split('\n'))
            output = text_input
        elif filter_option == 'Custom Delimiter' and custom_delimiter:
            count = len(text_input.split(custom_delimiter))
            output = custom_delimiter.join(text_input.split(custom_delimiter))

    return render_template('counter.html', text_input=text_input, count=count, output=output, filter_option=filter_option, custom_delimiter=custom_delimiter)

# Time Converter
@app.route('/time-converter', methods=['GET', 'POST'])
def time_converter():
    converted_time = ""
    output = {}
    if request.method == 'POST':
        time_input = request.form.get('time_input', '')

        try:
            # Initialize input_time as None for other time formats handling
            input_time = None

            # Specific handling for PostgreSQL timestamp format
            if " " in time_input and "-" in time_input and ":" in time_input:
                # Parse PostgreSQL timestamp
                input_time = datetime.strptime(time_input, '%Y-%m-%d %H:%M:%S')
                # Localize to Eastern Time considering DST
                eastern = pytz.timezone('America/New_York')
                input_time = eastern.localize(input_time, is_dst=None)
                # Format the output, appending 'Z' to denote Eastern Time handling
                converted_time = input_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
            
            # Handling for ISO 8601 format
            if input_time is None:
                try:
                    input_time = datetime.fromisoformat(time_input)
                    # Convert to Eastern Time
                    input_time = input_time.astimezone(pytz.timezone('America/New_York'))
                    converted_time = input_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
                except ValueError:
                    pass  # If parsing fails, proceed to next format

            # Handling for Epoch time (seconds then milliseconds)
            if input_time is None:
                try:
                    # First, try assuming seconds
                    input_time = datetime.fromtimestamp(float(time_input), tz=pytz.utc)
                except ValueError:
                    try:
                        # Then try milliseconds
                        input_time = datetime.fromtimestamp(float(time_input) / 1000, tz=pytz.utc)
                    except ValueError:
                        pass

                if input_time:
                    # Convert to Eastern Time
                    input_time = input_time.astimezone(pytz.timezone('America/New_York'))
                    converted_time = input_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

            if not converted_time:
                raise ValueError("Input time format not recognized.")
            
            if input_time:
                et_time = input_time.astimezone(pytz.timezone('America/New_York'))
                output['Local Time'] = et_time.strftime('%m/%d/%Y, %I:%M:%S %p')
                output['UTC Time'] = et_time.astimezone(pytz.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')
                # output['Relative Time'] = "Use JavaScript for live relative time"
                output['UNIX Time'] = str(int(et_time.timestamp()))
                output['Day of week'] = et_time.strftime('%A')
                output['Day of year'] = str(et_time.timetuple().tm_yday)
                output['Is leap year?'] = "Yes" if et_time.year % 4 == 0 and (et_time.year % 100 != 0 or et_time.year % 400 == 0) else "No"
                output['Other date formats (local time)'] = [
                    et_time.strftime('%Y-%m-%d'),
                    et_time.strftime('%m-%d-%Y'),
                    et_time.strftime('%Y/%m/%d'),
                    et_time.strftime('%m/%d/%Y'),
                    et_time.strftime('%a %B %d, %Y'),
                    et_time.strftime('%A %B %d, %Y'),
                    et_time.strftime('%a %b %d, %Y'),
                    et_time.strftime('%A %b %d, %Y'),
                ]
                # Append original format
                output['ISO Format'] = input_time.strftime('%Y-%m-%dT%H:%M:%S') + 'Z'



        except Exception as e:
            converted_time = f"Error converting time: {str(e)}"

    return render_template('time_converter.html', output=output)

# JSON Parser - beautify JSON
@app.route('/json-tools/json-parser', methods=['GET', 'POST'])
def json_parser():
    input_json = ""
    output_json = ""
    error = None

    if request.method == 'POST':
        input_json = request.form.get('input_json', '')

        try:
            # Parse the input JSON to ensure it's valid
            parsed_json = json.loads(input_json)
            # Beautify the JSON
            output_json = json.dumps(parsed_json, indent=4)
        except json.JSONDecodeError as e:
            error = f"Invalid JSON: {e.msg} at line {e.lineno}, column {e.colno}"

    return render_template('json_parser.html', 
                           input_json=input_json, 
                           output_json=output_json, 
                           error=error)

# Generate JSON from JSON schema
@app.route('/json-tools/json-sample-generator', methods=['GET', 'POST'])
# @limiter.limit("15 per minute")  # Rate limiting
def json_sample_generator():
    sample_data = None
    schema_input = ""
    if request.method == 'POST':
        schema_input = request.form.get('schema_input', '').strip()
        if schema_input:
            try:
                sample_data = json.dumps(generate_sample_data(json.loads(schema_input)), indent=4)
            except Exception as e:
                sample_data = f"Error generating sample data: {str(e)}"
    return render_template('json_sample_generator.html', schema_input=schema_input, sample_data=sample_data or "")

# CRON Expression generator
@app.route('/schedule_cron', methods=['GET', 'POST'])
def schedule_cron():
    if request.method == 'POST':
        # Process the form data and generate CRON expression
        minute = request.form.get('minute')
        hour = request.form.get('hour')
        day_of_month = request.form.get('day_of_month')
        month = request.form.get('month')
        day_of_week = request.form.get('day_of_week')
        
        cron_expression = f"{minute} {hour} {day_of_month} {month} {day_of_week}"
        # You can then save this expression, display it, or use it as needed
        return make_response(f"CRON Expression: {escape(cron_expression)}")
    else:
        # Display the form
        return render_template('cron_scheduler.html')

# Random string generator
@app.route('/string-tools/random-string-generator', methods=['GET', 'POST'])
def random_string_generator():
    random_string = ''
    original_text = ''
    if request.method == 'POST':
        length = int(request.form.get('length', 16))
        characters = string.ascii_letters + string.digits + string.punctuation
        random_string = ''.join(random.choice(characters) for _ in range(length))
        original_text = request.form.get('length', '16')
    return render_template('random_string_generator.html', random_string=random_string, original_text=original_text)

# Random number generator
@app.route('/string-tools/random-number-generator', methods=['GET', 'POST'])
def random_number_generator():
    random_number = None
    original_min = ''
    original_max = ''
    if request.method == 'POST':
        min_val = int(request.form.get('min_val', 0))
        max_val = int(request.form.get('max_val', 100))
        random_number = random.randint(min_val, max_val)
        original_min = request.form.get('min_val', '0')
        original_max = request.form.get('max_val', '100')
    return render_template('random_number_generator.html', random_number=random_number, original_min=original_min, original_max=original_max)

# Shuffle letters
@app.route('/string-tools/shuffle-letters', methods=['GET', 'POST'])
def shuffle_letters():
    shuffled_text = ''
    original_text = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        shuffled_text = ''.join(random.sample(text, len(text)))
        original_text = text
    return render_template('shuffle_letters.html', shuffled_text=shuffled_text, original_text=original_text)

# Clean text
@app.route('/string-tools/clean-text', methods=['GET', 'POST'])
def clean_text():
    cleaned_text = ''
    original_text = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        cleaned_text = re.sub(r'([.!?])\s*', r'\1 ', cleaned_text)
        sentences = re.split(r'([.!?] )', cleaned_text)
        cleaned_text = ''.join([s.capitalize() if i % 2 == 0 else s for i, s in enumerate(sentences)])
        original_text = text
    return render_template('clean_text.html', cleaned_text=cleaned_text, original_text=original_text)

# Text statistics
@app.route('/string-tools/text-statistics', methods=['GET', 'POST'])
def text_statistics():
    stats = {}
    original_text = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        original_text = text
        words = text.split()
        num_words = len(words)
        num_chars = len(text)
        num_chars_no_space = len(text.replace(' ', ''))
        num_lines = text.count('\n') + 1
        num_sentences = len(re.findall(r'[.!?]', text))
        word_lengths = [len(word) for word in words]
        unique_words = set(words)
        stats = {
            'num_chars': num_chars,
            'num_chars_no_space': num_chars_no_space,
            'num_lines': num_lines,
            'num_words': num_words,
            'num_sentences': num_sentences,
            'num_unique_words': len(unique_words),
            'percent_unique_words': (len(unique_words) / num_words) * 100 if num_words > 0 else 0,
            'length_shortest_word': min(word_lengths) if words else 0,
            'length_longest_word': max(word_lengths) if words else 0,
            'avg_word_length': sum(word_lengths) / num_words if num_words > 0 else 0
        }
    return render_template('text_statistics.html', stats=stats, original_text=original_text)

# Column extractor
@app.route('/string-tools/column-extractor', methods=['GET', 'POST'])
def column_extractor():
    extracted_columns = []
    original_text = ''
    original_column_number = ''
    original_delimiter = ''
    if request.method == 'POST':
        text = request.form.get('text', '')
        column_number = int(request.form.get('column_number', 1)) - 1
        delimiter = request.form.get('delimiter', ',')
        lines = text.split('\n')
        for line in lines:
            columns = line.split(delimiter)
            if len(columns) > column_number:
                extracted_columns.append(columns[column_number].strip())
        original_text = text
        original_column_number = request.form.get('column_number', '1')
        original_delimiter = request.form.get('delimiter', ',')
    return render_template('column_extractor.html', extracted_columns=extracted_columns, original_text=original_text, original_column_number=original_column_number, original_delimiter=original_delimiter)

@app.route('/jwt_viewer', methods=['GET', 'POST'])
def jwt_viewer():
    decoded_jwt = None
    error = None
    if request.method == 'POST':
        jwt_token = request.form.get('jwt_token')
        secret_key = request.form.get('secret_key')
        try:
            decoded_jwt = jwt.decode(jwt_token, secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            error = "Token has expired"
        except jwt.InvalidTokenError:
            error = "Invalid token"
    return render_template('jwt_viewer.html', decoded_jwt=decoded_jwt, error=error)



if __name__ == '__main__':
    app.run(debug=True)
