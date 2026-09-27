# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

Academic project for **Desarrollo de Software 2026** at UTN Facultad Regional San Rafael (Ingeniería en Sistemas). The app receives PDF files, extracts their text content, and persists it in a NoSQL database with a checksum for deduplication. It exposes a full CRUD API over the persisted documents.

## Business Rules (Non-negotiable)

These constraints are core requirements — never violate them:

- **No temporary files**: the PDF binary must never be written to disk during processing.
- **No duplicates**: before persisting, compute SHA-256 checksum and reject if already stored.
- **Validate on upload**: reject files that are not valid PDFs or exceed the allowed size limit.
- **Text only**: only the extracted text is persisted; the PDF binary is never stored in the database.

## Methodology

**TDD is required.** Every feature must follow Red → Green → Refactor:

1. Write a failing test that describes the expected behavior.
2. Write the minimum code to make it pass.
3. Refactor without breaking the test.

Never add implementation code without a test written first. If a test doesn't exist, the feature doesn't exist.

## Design Principles

Code is evaluated against these criteria — apply them actively:

- **YAGNI**: only build what is explicitly required. No speculative features or abstractions.
- **DRY**: if logic appears twice, extract it. One source of truth.
- **KISS**: prefer the simplest solution that satisfies the requirement.
- **SOLID**: Single Responsibility in services and handlers; Dependency Inversion already applied via `Protocol` interfaces.
- **Clean Code**: descriptive names, small functions, no comments that explain *what* the code does (names do that).
- **12-Factor App**: config via environment variables (already: `DB_URL`, `DB_NAME`); dependencies declared in `pyproject.toml`; single codebase.

## Commands

```bash
# Run the API server (dev)
uv run uvicorn presentation.main:app --reload

# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_api.py

# Run a single test by name
uv run pytest tests/test_api.py::test_ping_server

# Start MongoDB locally (required for the app and integration tests)
docker compose up mongodb -d

# Start full stack with hot reload
docker compose up --watch
```

Environment variables (all prefixed `DB_`):
- `DB_URL` — MongoDB connection string (default: `mongodb://localhost:27017`)
- `DB_NAME` — database name (default: `pdf_extractext`)

## Architecture

Clean Architecture with three layers satisfying the Enterprise Application Architecture requirement. Dependencies flow inward only: `presentation → application ← data`.

**`application/`** — pure business logic, no framework imports. Defines `Protocol` interfaces (`DocumentRepository`, `ChecksumRepository`) that the data layer implements. Service functions (`get_document`, `get_all_documents`, `update_document`, `save_document_if_unique`) receive repositories as arguments.

**`presentation/main.py`** — the real FastAPI app. Wires FastAPI `Depends` to concrete repository classes. Owns all request/response models (e.g. `UpdateDocumentRequest`). The `lifespan` context manager initialises the Beanie/MongoDB connection on startup.

**`data/`** — Beanie ODM models and two repository classes:
- `BeanieDocumentRepository` (`data/repository.py`) — implements the `DocumentRepository` Protocol for full CRUD.
- `MongoChecksumRepository` (`data/repositories.py`) — implements `ChecksumRepository`; used only by the `/extract` endpoint to enforce uniqueness.

`api/main.py` is a minimal stub; the production app lives in `presentation/main.py`.

## Testing patterns

Tests are written **before** implementation code (TDD). The test is the spec.

API tests in `tests/test_api.py` use `httpx.AsyncClient` with `ASGITransport` to call the app in-process. The real MongoDB connection is bypassed by patching `get_database_connection` or by overriding FastAPI dependencies via `app.dependency_overrides`. Always clear overrides after each test with `app.dependency_overrides.clear()`.

`tests/test_database.py` contains integration tests that require a live MongoDB instance.

## Stage 2 — Microservices Split: Load/Stress Testing & Optimization

Context for the project's next phase (assignment brief, not yet implemented): the PDF text/Markdown extraction responsibility is split out into its own independent microservice, benchmarked under load/stress with Grafana k6 and Vegeta against a reference implementation from the professor.

### New microservice contract
- Dedicated service exposing `POST /extract`, receiving the raw PDF binary (`multipart/form-data` or a direct binary body).
- Response: `200 OK`, `application/json`, shaped as `{ "content": "<extracted text>", "page_count": <int> }`.
- Stack is unconstrained — any language/framework/PDF library, independent of the current Python/FastAPI stack.

### Deployment constraints (for fair benchmarking)
- Packaged as a Docker image, deployed via `docker compose`.
- Horizontal scaling up to a max of 5 replicas (e.g. `deploy.replicas: 5`) behind a reverse proxy/load balancer (Traefik/Caddy).
- Explicit per-container resource limits in `docker-compose.yml` (e.g. max 1.0 CPU, 512MB–1GB RAM per replica).
- Load tests run against the official PDF corpus in `tests/stress/pdfs` (variable size/density, up to ~9MB).

### Reference benchmarks to beat
- **Spike test (k6, closed model)**: ramp to 100 VUs over 10s, hold 20s, ramp down 10s. Reference numbers: 1,037 requests in 40s, 25.35 req/s sustained throughput, 0.00% error rate, p50 1.88s, p90/p95 7.83s/8.80s, max latency 13.94s.
- **Fixed-rate load test (Vegeta, open model)**: 50 req/s continuous for 30s (1,500 requests rotating 4 test PDFs), 30s client timeout. Reference numbers: 16.65 req/s effective throughput, 66.53% success (998/1,500), 33.40% client timeouts (501 requests) from CPU queue saturation above ~25 sustainable req/s, p50 14.89s.

### Optimization directions to investigate
- Low-CPU/memory PDF extraction libraries that read the stream directly, without dumping the file to disk or duplicating buffers in memory.
- Backpressure and concurrency limiting: avoid unbounded request queues past their useful lifetime; return `429 Too Many Requests` / `503 Service Unavailable` in a controlled way instead.
- Replica strategy and load balancing across the 5 instances.
- Separate the HTTP runtime process from the text-extraction worker pool.

### Grading criteria
- Base grade: technical approval, runs in Docker (up to 5 replicas), functional `/extract`, working test scripts.
- +1.5 points (2nd midterm) for beating the professor's throughput, success rate, and latencies under the same hardware constraints.
- +1.0 extra point for the best overall balance of throughput, failure rate, and latency percentiles across all submissions.
- Qualitative evaluation: Twelve-Factor App compliance (env-var config, port binding, stateless processes, logs to stdout), code structure/modularity/readability, architecture write-up, before/after optimization metrics comparison, and a documented investigation process (required to be eligible for the extra point).

### Deliverables
- Reproducible repo with `Dockerfile` and `docker-compose.yml`, single-command `docker compose up --build`.
- Test scripts: adapted k6 script for the spike test, Vegeta script for the fixed-load test.
- Markdown/PDF report: architecture justification and identified bottleneck analysis.
