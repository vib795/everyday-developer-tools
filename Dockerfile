FROM node:26-alpine AS spa
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libc6-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

COPY backend/pyproject.toml backend/uv.lock* ./backend/
RUN cd backend && uv sync --no-dev

COPY backend/ ./backend/
COPY --from=spa /app/frontend/dist ./frontend/dist

ENV SPA_DIST=/app/frontend/dist \
    LOG_DIRECTORY=/app/logs/

RUN adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/logs \
    && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/backend
EXPOSE 8000

# Bind to $PORT when the host injects one (Render, Cloud Run, …); fall back to
# 8000 so local `docker compose up` keeps working.
CMD exec uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
