FROM python:3.12-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY backend/pyproject.toml backend/uv.lock* ./backend/
RUN cd backend && uv sync --no-dev

COPY backend/ ./backend/

ENV LOG_DIRECTORY=/app/logs/

RUN adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend
EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
