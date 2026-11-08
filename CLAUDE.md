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
