# Developer Tools

A web app that bundles 16+ everyday developer tools — JSON validators and generators, regex helpers, string and time utilities, encoding tools, fake-data generation, and Markdown ⇄ PDF conversion.

The application is split into two pieces:

- **`backend/`** — a [FastAPI](https://fastapi.tiangolo.com/) service exposing every tool as a typed JSON endpoint under `/api/...`.
- **`frontend/`** — a [Vite](https://vitejs.dev/) + [React](https://react.dev/) + TypeScript single-page app served by the backend in production.

In production both ship in a single Docker image. In development you can run them as two processes (Vite proxies `/api` to the API).

## Tools

### JSON
- **Validator** — validate JSON, optionally against a JSON Schema.
- **Schema Generator** — produce a draft-04 JSON Schema from a sample.
- **Sample Generator** — generate sample data conforming to a schema (handles `enum`, `pattern`, `format`, `allOf`/`anyOf`/`oneOf`, `if`/`then`/`else`).
- **String ⇄ JSON Converter** — turn JSON into an escaped string and back.
- **Parser** — pretty-print JSON.

### RegEx
- **Checker** — test a pattern against a string. Each call is bounded to 1 s of CPU and rate-limited (15/min by default) to mitigate ReDoS.
- **Generator** — suggest a regex for an input; recognises emails, phone numbers, ISO dates, and SSNs.

### String
- **Diff Viewer** — side-by-side diff with line numbers and per-row colouring.
- **Char/Word Counter** — character/word/line count, with optional custom delimiter.
- **Column Extractor** — pull a column out of delimited text.
- **Clean Text** — collapse whitespace and capitalise sentence starts.
- **Text Statistics** — char/word/sentence counts plus min/max/avg word length.
- **Random Number / Random String / Shuffle Letters**.

### Encoding
- **Base64** — encode/decode UTF-8 text.
- **JWT Viewer** — decode HS256 tokens.

### Time
- **Time Converter** — accepts ISO-8601, epoch seconds, epoch milliseconds, and `YYYY-MM-DD HH:MM:SS` Postgres timestamps; emits Eastern, UTC, UNIX, day-of-week/year, leap-year, and several locale formats.
- **CRON Scheduler** — build a CRON expression from form fields.

### Document
- **Markdown ⇄ PDF** — render Markdown to a downloadable PDF (headings, bullets, fenced code) or extract text from a PDF.

### Fake Data
- **Generator** — build a synthetic dataset of up to 1000 records with 25+ field types (names, emails, vehicle make/model pairs, license plates, etc.) and export as JSON or CSV.

## Architecture

```
┌────────────────────────────────────────────────┐
│              single Docker image               │
│                                                │
│  uvicorn (FastAPI)                             │
│     ├─ /api/*  → routers/ → services/          │
│     │      json, regex, string, encoding,      │
│     │      time, document, fake_data           │
│     └─ /*      → SPA (Vite build)              │
└────────────────────────────────────────────────┘
                        │
                        └── redis  (slowapi rate limiting)
```

- **Pure-function services** in `backend/app/services/` hold the heavy lifting; routers stay thin. This is what makes the helpers easy to unit-test.
- **Pydantic v2** request/response models on every endpoint give automatic validation and a useful `/docs` (Swagger) page.
- **slowapi** sits in front of expensive routes (`/api/regex/check`, `/api/json/sample`). It uses Redis when `REDIS_URL` is set and falls back to in-memory storage otherwise.

## Local development

Prerequisites: Python 3.10+, Node 20+, [`uv`](https://docs.astral.sh/uv/).

### Backend

```bash
cd backend
uv sync                              # install deps into .venv
uv run uvicorn app.main:app --reload # http://localhost:8000
uv run pytest                        # run the test suite
```

OpenAPI docs: <http://localhost:8000/docs>.

### Frontend

```bash
cd frontend
npm install
npm run dev                          # http://localhost:5173
```

The dev server proxies `/api` → `http://localhost:8000`, so just run both processes side by side.

### Docker (dev)

```bash
docker compose -f docker-compose-dev.yml up --build
# API:    http://localhost:8000
# Vite:   http://localhost:5173
```

### Docker (prod, single image + nginx)

```bash
docker compose -f docker-compose.yml up --build
# Nginx terminates TLS on :443 and proxies everything to the FastAPI container.
```

The production Dockerfile is multi-stage:

1. `node:20-alpine` builds the SPA (`npm run build`) into `/app/frontend/dist`.
2. `python:3.12-slim` installs runtime deps with `uv sync --no-dev` and serves both the API and the built SPA from a single uvicorn process. `SPA_DIST` points at the built assets.

For HTTPS, generate (or replace) `certs/nginx-selfsigned.{crt,key}`:

```bash
mkdir -p certs && cd certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx-selfsigned.key -out nginx-selfsigned.crt
```

## Configuration

All settings are read from environment variables (or a `backend/.env` file).

| Variable                  | Default                                         | Description |
| ------------------------- | ----------------------------------------------- | ----------- |
| `LOG_DIRECTORY`           | `logs/`                                         | Log file directory; created on startup. |
| `REDIS_URL`               | (unset → in-memory)                             | Storage URI for the slowapi limiter. |
| `SPA_DIST`                | `<repo>/frontend/dist`                          | Path to the built SPA. |
| `CORS_ORIGINS`            | `http://localhost:5173,http://127.0.0.1:5173`   | Allowed dev origins. |
| `RATE_LIMIT_DEFAULT`      | `60/minute`                                     | Default per-IP limit. |
| `RATE_LIMIT_REGEX_CHECK`  | `15/minute`                                     | Limit on `/api/regex/check`. |
| `RATE_LIMIT_JSON_SAMPLE`  | `30/minute`                                     | Limit on `/api/json/sample`. |

## API quick reference

Every endpoint returns JSON unless noted. All POST bodies are JSON.

| Method | Path                          | Notes |
| ------ | ----------------------------- | ----- |
| POST   | `/api/json/validate`          |       |
| POST   | `/api/json/schema`            |       |
| POST   | `/api/json/sample`            | rate-limited |
| POST   | `/api/json/convert`           |       |
| POST   | `/api/json/parse`             |       |
| POST   | `/api/regex/check`            | rate-limited; 1 s timeout |
| POST   | `/api/regex/generate`         |       |
| POST   | `/api/string/diff`            | structured hunks |
| POST   | `/api/string/count`           |       |
| POST   | `/api/string/columns`         |       |
| POST   | `/api/string/clean`           |       |
| POST   | `/api/string/stats`           |       |
| POST   | `/api/string/random-number`   |       |
| POST   | `/api/string/random-string`   |       |
| POST   | `/api/string/shuffle`         |       |
| POST   | `/api/encoding/base64`        |       |
| POST   | `/api/encoding/jwt`           |       |
| POST   | `/api/time/convert`           |       |
| POST   | `/api/time/cron`              |       |
| POST   | `/api/document/md-to-pdf`     | streams `application/pdf` |
| POST   | `/api/document/pdf-to-md`     | multipart upload |
| GET    | `/api/fake-data/types`        | list of supported field types |
| POST   | `/api/fake-data/preview`      |       |
| POST   | `/api/fake-data/export`       | streams CSV or JSON |
| GET    | `/api/health`                 |       |

## Contributing

1. Fork the repo and create a branch.
2. Make changes; add or update tests in `backend/tests/`.
3. Ensure `cd backend && uv run pytest` and `cd frontend && npm run build` both pass.
4. Open a PR.

## License

MIT — see [LICENSE](LICENSE).
