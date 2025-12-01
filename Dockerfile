# Use an official Python runtime as a parent image
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies + curl for uv installer
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Install uv (single, static binary)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh -s -- --install-dir /usr/local/bin --exe-name uv

# Copy project metadata first to leverage Docker cache
COPY pyproject.toml uv.lock ./

# Install dependencies (no dev deps) into .venv inside /app
RUN uv sync --frozen --no-dev

# Now copy the rest of the app
COPY . /app

# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos '' myuser
USER myuser

EXPOSE 5000

ENV FLASK_APP=app.py \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_ENV=production

# Run with gunicorn via uv so the .venv is used automatically
CMD ["uv", "run", "gunicorn", "--workers=4", "--bind=0.0.0.0:5000", "app:app"]

