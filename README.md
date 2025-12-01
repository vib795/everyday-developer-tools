# Developer Tools Web Application

This is a Flask web application that provides various developer tools including a Diff Viewer, JSON Validator, Regex Checker, and Regex Generator.

## Features

### JSON Tools
- **Validator:** Validate JSON format and against schema
- **Schema Generator:** Generate schema from JSON input
- **Sample Data Generator:** Create sample data from schema
- **JSON-String Converter:** Convert between JSON object and string
- **Parser:** Beautify and format JSON

### RegEx Tools
- **Checker:** Validate strings against regular expressions
- **Generator:** Generate regex patterns for common formats

### String Tools
- **Character/Word Counter:** Count chars/words/lines, supports custom delimiters
- **Column Extractor:** Extract specific columns from delimited text
- **Text Cleaner:** Clean and format text
- **Text Statistics:** Generate text metrics
- **Diff Viewer:** Compare text and visualize differences
- **Random Generators:** Generate random numbers and strings
- **Shuffle Letters:** Randomize text characters

### Data Generation
- **Fake Data Generator:** Generate sample datasets (up to 1000 records)
  - Categories: Personal, Professional, Vehicle, Technical
  - Export to JSON/CSV
  - Customizable fields and data types

### Document Tools
- **Markdown/PDF Converter:** Convert between Markdown and PDF formats
  - Preserves formatting and structure
  - Supports headings, lists, code blocks
  - Both MD to PDF and PDF to MD conversion

### Time & Scheduling
- **Time Converter:** Convert between various time formats (ISO/EPOCH)
- **CRON Scheduler:** Create CRON expressions visually

### Encoding Tools
- **Base64 Encoder/Decoder:** Convert to/from base64
- **JWT Viewer:** Decode and view JWT tokens

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/vib795/everyday-developer-tools.git
    ```

2. Navigate to the project directory:

    ```bash
    cd developer-tools
    ```

3. Install dependencies using uv (recommended):

    ```bash
    # create a virtualenv in .venv and install dependencies
    uv venv
    uv pip install -r requirements.txt

    # or, if you've migrated to pyproject.toml + uv.lock:
    # uv sync
    ```

## Usage

1. Run the Flask application:

    uv run flask run --host 0.0.0.0 --port 5000

2. Open a web browser and navigate to [http://localhost:5000](http://localhost:5000).

3. Choose a tool from the navigation menu on the left.

## Production Deployment with Docker, Gunicorn, and Nginx
### Dockerized Approach
For deploying the application in a containerized environment with Docker, ensuring scalability and ease of deployment:

1. **Build and Deploy with Docker Compose:** 
    <br/>_Dev build_
    ```bash
    docker-compose -f docker-compose-dev.yml up --build
    ```
    OR
    <br/> _Deployable build_
    ```bash
    docker-compose -f docker-compose.yml up --build
    ``` 
    
This command builds the Docker images and starts the containers as defined in the `docker-compose.yml` file.

2. **Running a Pre-Built Container:**
    ```bash
    docker run -p 5000:5000 utkarshsingh/developer-tools-dev:latest
    ```

### Making the Application HTTPS Compliant
To secure the application with HTTPS, follow these steps:

1. **Generate SSL/TLS Certificates:**
For local testing, generate a self-signed SSL certificate:
    ```bash
    mkdir -p certs && cd certs
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx-selfsigned.key -out nginx-selfsigned.crt
    ```

For production, obtain certificates from Let's Encrypt or another CA.

2. **Configure Nginx for HTTPS:**
Update `nginx/nginx.conf` to include the SSL certificate and key, and configure Nginx to listen on HTTPS:
    ```nginx
    server {
        listen 443 ssl;
        server_name localhost; # Update to your domain for production

        ssl_certificate /etc/ssl/certs/nginx-selfsigned.crt;
        ssl_certificate_key /etc/ssl/certs/nginx-selfsigned.key;

        # SSL configuration...

        location / {
            proxy_pass http://web:5000;
            # Proxy settings...
        }
    }
    ```
Update docker-compose.yml to mount the certificates directory into the Nginx container.

3. **To pull from Docker hub (dev build):**
    ```bash
    docker pull utkarshsingh/developer-tools-dev:latest
    ```

### Why and How of Nginx and Gunicorn
- **Nginx:** Acts as a reverse proxy, handling client requests efficiently before passing them to Gunicorn. It's also responsible for SSL/TLS termination, providing HTTPS support.
- **Gunicorn:** A WSGI HTTP Server for serving Flask applications in production, offering a robust option to handle concurrent requests.

### Redis for rate limiting
- We are using redis to rate limit the site to avoid DDoS or ReDoS attacks.
- This is installed as part of the docker image but you can do it manually as well, if you are running the flask app manually.
    - This installs redis on an ubuntu server and checks for its status.   
        ```bash 
        sudo apt-get update && sudo apt-get install redis-server -y && sudo systemctl status redis
        ```
    
    - Check status of redis server:
        ```bash
        redis-cli ping
        ```
        You should receive `PONG` back.
    - Install Redis python library
        ```bash
        pip install redis
        ```
    
This should set the app to be configured with redis and ready to use. Now you can run `flask app.py` and everything should work fine without docker intervention.


## Contributing

Contributions are welcome! If you would like to contribute to this project, please follow these steps:

1. Fork the [repository](https://github.com/vib795/everyday-developer-tools.git).

2. Create a new branch for your feature or bug fix:

    ```bash
    git checkout -b feature-name
    ```

3. Make your changes and commit them:

    ```bash
    git commit -m "Add feature-name"
    ```

4. Push to your branch:

    ```bash
    git push origin feature-name
    ```

5. Submit a pull request.

## Live demo
A live demo of the application can be viewed <a href="https://utkarshsingh0609.pythonanywhere.com/" target="_blank">here</a>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
