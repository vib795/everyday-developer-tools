# Developer Tools

A web app that bundles 35+ everyday developer tools — JSON and format converters, regex helpers, string and time utilities, encoding/hashing tools, color and network calculators, fake-data and QR generation, Markdown ⇄ PDF conversion, and quick HTTP/MIME reference tables.

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
- **JSONPath** — evaluate a JSONPath expression against a JSON document.

### Convert
- **Format Converter** — convert between JSON, YAML, TOML, XML, and CSV (CSV round-trips a list-of-objects shape).
- **cURL Converter** — turn a `curl` command into `fetch`, `axios`, and Python `requests` code.

### RegEx
- **Checker** — test a pattern against a string. Each call is bounded to 1 s of CPU and rate-limited (15/min by default) to mitigate ReDoS.
- **Generator** — suggest a regex for an input; recognises emails, phone numbers, ISO dates, and SSNs.

### String
- **Diff Viewer** — side-by-side diff with line numbers and per-row colouring.
- **Char/Word Counter** — character/word/line count, with optional custom delimiter.
- **Column Extractor** — pull a column out of delimited text.
- **Clean Text** — strip leading/trailing whitespace plus hidden/zero-width and control characters; preserves case and internal whitespace, with an optional toggle to collapse runs of spaces (keeping newlines).
- **Text Statistics** — char/word/sentence counts plus min/max/avg word length.
- **Random Number / Random String / Shuffle Letters**.

### Encoding
- **Base64** — encode/decode UTF-8 text.
- **URL Codec** — URL-encode/decode text and parse a query string into key/value pairs.
- **Hash & HMAC** — MD5/SHA-family digests and keyed HMAC digests.
- **JWT Viewer** — decode HS256 tokens.
- **JWT Signer** — sign a payload with HS256/384/512.
- **UUID** — generate (v1/v3/v4/v5/v7) and inspect/validate UUIDs.
- **Case Converter** — convert between camelCase, snake_case, kebab-case, CONSTANT_CASE, Title Case, and more.

### Time
- **Time Converter** — accepts ISO-8601, epoch seconds, epoch milliseconds, and `YYYY-MM-DD HH:MM:SS` Postgres timestamps; emits Eastern, UTC, UNIX, day-of-week/year, leap-year, and several locale formats.
- **CRON Scheduler** — build a CRON expression from form fields.
- **CRON Next Runs** — list the next N times a CRON expression will fire, in a chosen timezone.

### Calc
- **Color** — convert a color between hex, RGB, HSL, and OKLCH, and check WCAG contrast ratios.
- **chmod Calculator** — convert Unix permissions between numeric and symbolic forms.
- **CIDR Calculator** — derive network/broadcast addresses, host range, and host count for an IPv4/IPv6 subnet.

### Document
- **Markdown ⇄ PDF** — render Markdown to a downloadable PDF (headings, bullets, fenced code) or extract text from a PDF.
- **Markdown Preview** — render Markdown to HTML (fenced code, tables, lists).

### Fake Data
- **Generator** — build a synthetic dataset of up to 1000 records with 25+ field types (names, emails, vehicle make/model pairs, license plates, etc.) and export as JSON or CSV.
- **Lorem Ipsum** — generate filler words, sentences, or paragraphs.
- **QR Code** — encode text or a URL as an SVG QR code.

### Reference
- **HTTP Statuses** — searchable reference of HTTP status codes.
- **MIME Types** — common Content-Type / file-extension reference.

## Architecture

```
┌────────────────────────────────────────────────┐
│              single Docker image               │
│                                                │
│  uvicorn (FastAPI)                             │
│     ├─ /api/*  → routers/ → services/          │
│     │      json, convert, regex, string,       │
│     │      encoding, codec, time, calc,        │
│     │      document, fake_data, misc           │
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

### Docker (single command, recommended)

```bash
docker compose up --build
# everything on http://localhost:8000
```

One container: a multi-stage build assembles the SPA with `node:20-alpine`, then `python:3.12-slim` installs runtime deps with `uv sync --no-dev` and serves both the API and the built SPA from a single uvicorn process. `SPA_DIST` points at the built assets.

### Docker (dev with hot reload)

```bash
docker compose -f docker-compose-dev.yml up --build
# API:    http://localhost:8000
# Vite:   http://localhost:5173
```

### Docker (prod with nginx + redis + TLS)

For deployments that want TLS termination and Redis-backed rate limiting:

```bash
docker compose -f docker-compose-prod.yml up --build
```

You'll need self-signed certs in `certs/` (see below) before bringing up the nginx container.

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
| POST   | `/api/convert/format`         | JSON/YAML/TOML/XML/CSV |
| POST   | `/api/convert/jsonpath`       | evaluate a JSONPath expression |
| POST   | `/api/convert/curl`           | curl → fetch / axios / requests |
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
| POST   | `/api/encoding/jwt`           | decode |
| POST   | `/api/codec/url`              | URL encode/decode |
| POST   | `/api/codec/url/parse`        | parse query string |
| POST   | `/api/codec/hash`             | MD5/SHA digests |
| POST   | `/api/codec/hmac`             | keyed HMAC digest |
| POST   | `/api/codec/case`             | case conversion |
| POST   | `/api/codec/uuid/generate`    | UUID v1/v3/v4/v5/v7 |
| POST   | `/api/codec/uuid/inspect`     | parse/validate a UUID |
| POST   | `/api/codec/jwt/sign`         | sign HS256/384/512 |
| POST   | `/api/time/convert`           |       |
| POST   | `/api/time/cron`              |       |
| POST   | `/api/calc/cron-next`         | next N cron run times |
| POST   | `/api/calc/color`             | hex/RGB/HSL/OKLCH |
| POST   | `/api/calc/contrast`          | WCAG contrast ratio |
| POST   | `/api/calc/chmod`             | numeric ⇄ symbolic |
| POST   | `/api/calc/cidr`              | subnet calculator |
| POST   | `/api/calc/markdown`          | Markdown → HTML |
| POST   | `/api/document/md-to-pdf`     | streams `application/pdf` |
| POST   | `/api/document/pdf-to-md`     | multipart upload |
| GET    | `/api/fake-data/types`        | list of supported field types |
| POST   | `/api/fake-data/preview`      |       |
| POST   | `/api/fake-data/export`       | streams CSV or JSON |
| GET    | `/api/misc/http-statuses`     | HTTP status reference |
| GET    | `/api/misc/mime-types`        | MIME-type reference |
| POST   | `/api/misc/lorem`             | lorem ipsum generator |
| POST   | `/api/misc/qr`                | SVG QR code |
| GET    | `/api/health`                 |       |

## Contributing

1. Fork the repo and create a branch.
2. Make changes; add or update tests in `backend/tests/`.
3. Ensure `cd backend && uv run pytest` and `cd frontend && npm run build` both pass.
4. Open a PR.

## License

MIT — see [LICENSE](LICENSE).
