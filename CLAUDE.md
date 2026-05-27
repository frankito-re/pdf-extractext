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

# Start the dev server
uv run uvicorn presentation.main:app --reload

# Add a dependency
uv add <package>
```

Tests that touch the database (`test_database.py`) require a running MongoDB instance at `mongodb://localhost:27017` (default). Override with `DB_URL` env var.

## Architecture

This is a **multilayer (Clean Architecture)** FastAPI + MongoDB project:

| Layer | Directory | Responsibility |
|-------|-----------|---------------|
| Presentation | `presentation/` | FastAPI app, route handlers, HTTP I/O |
| Application | `application/` | Business logic (PDF extraction, validation) |
| Data | `data/` | DB connection (`connection.py`), settings (`config.py`) |
| API (entry point) | `api/` | Alternative/legacy app entrypoint (currently minimal) |

`main.py` at root is the project entrypoint.

**Data flow:** HTTP request → `presentation/main.py` → `application/pdf_extractor.py` → response. DB access goes through `data/connection.py` (Beanie ODM over MongoDB).

**Key constraint:** PDF files must never be written to disk — all processing happens in-memory via `bytes` / `io.BytesIO`.

## Configuration

Settings use `pydantic-settings` with env prefix `DB_`:
- `DB_URL` — MongoDB connection string (default: `mongodb://localhost:27017`)
- `DB_NAME` — database name (default: `pdf_extractext`)

## Development Methodology

This project follows **TDD strictly**: write a failing test first, verify it fails for the right reason, then write minimal production code to pass it. See `AGENT/AGENTS.md` for the full project brief.

Commit messages follow **Conventional Commits** (`feat:`, `fix:`, `refactor:`, `perf:`, `chore:`, `docs:`).
