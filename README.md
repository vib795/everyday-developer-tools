# Developer Tools Web Application

This is a Flask web application that provides various developer tools including a Diff Viewer, JSON Validator, QR Code Generator, Regex Checker, and Regex Generator.

## Features

- **Diff Viewer:** Compare two blocks of text and visualize the differences.
- **JSON Validator:** Validate JSON format and optionally validate against a JSON schema.
- **JSON Schema generator:** Generates a JSON schema based on JSON input.
- **JSON-String-JSON converter:** COnverts JSON object to string and vice-versa.
- **QR Code Generator:** Generate QR codes from text input.
- **Regex Checker:** Validate strings against regular expressions.
- **Regex Generator:** Generate regular expressions for common patterns.
- **Base64 Encoder Decoder:** Convert text to/from using base64 encoding/decoding.

## Installation

1. Clone this repository:

    ```bash
    git clone https://github.com/vib795/everyday-developer-tools.git
    ```

2. Navigate to the project directory:

    ```bash
    cd developer-tools
    ```

3. Install dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:

    ```bash
    flask run
    ```

2. Open a web browser and navigate to [http://localhost:5000](http://localhost:5000).

3. Choose a tool from the navigation menu on the left.

## Dockerized approach
Run the command:
```bash
docker compose up --build
```
to build the code and deploy it in a container.
<br/>OR<br/>
```bash
docker run -p 5000:5000 utkarshsingh/developer-tools
```

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
