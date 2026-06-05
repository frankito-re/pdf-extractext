# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Run all tests
uv run pytest

# Run a single test file
uv run pytest tests/test_pdf_extractor.py

# Run a single test by name
uv run pytest tests/test_api.py::test_ping_server

# Run the full stack (app + MongoDB)
docker compose up

# Start MongoDB only (for local dev without Docker app)
docker compose up mongodb -d

# Start the dev server locally (hot reload, requires MongoDB running)
uv run uvicorn presentation.main:app --reload

# Add a dependency
uv add <package>
```

Tests in `test_database.py` and `test_checksum.py` require a running MongoDB instance at `mongodb://localhost:27017`. Override with `DB_URL` and `DB_NAME` env vars.

## Architecture

This is a **multilayer (Clean Architecture)** FastAPI + MongoDB project:

| Layer | Directory | Responsibility |
|-------|-----------|---------------|
| Presentation | `presentation/` | FastAPI app, route handlers, HTTP I/O |
| Application | `application/` | Business logic: PDF extraction, checksum, domain exceptions |
| Data | `data/` | Beanie ODM models, repository implementation, DB init, settings |
| `api/` | — | Vestigial entrypoint, not in active use |

`main.py` at root is the project entrypoint (re-exports the FastAPI app).

**Request flow for `POST /extract`:**
1. `presentation/main.py` reads the uploaded bytes and calls `calculate_checksum`
2. `application/pdf_extractor.py` extracts text via `pypdf` (purely in-memory, no disk writes)
3. `application/checksum.py::save_document_if_unique` checks for duplicates via the repository, raises `DuplicateDocumentError` if found → mapped to HTTP 409
4. `data/repositories.py::MongoChecksumRepository` persists `text` + `checksum` via Beanie

**Dependency inversion:** `application/checksum.py` defines the `ChecksumRepository` Protocol (interface). `data/repositories.py::MongoChecksumRepository` implements it. The application layer never imports from `data/`.

**Key constraint:** PDF bytes must never be written to disk — all processing is in-memory via `bytes` / `io.BytesIO`.

## Configuration

Settings (`data/config.py`) use `pydantic-settings` with env prefix `DB_`:
- `DB_URL` — MongoDB connection string (default: `mongodb://localhost:27017`)
- `DB_NAME` — database name (default: `pdf_extractext`)

`docker-compose.yml` defines both the `mongodb` service and the containerised `app` (sets `DB_URL=mongodb://mongodb:27017`).

## Development Methodology

This project follows **TDD strictly**: write a failing test first, verify it fails for the right reason, then write minimal production code to pass it. See `AGENT/AGENTS.md` for the full project brief.

Commit messages follow **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `perf:`, `chore:`, `docs:`).
