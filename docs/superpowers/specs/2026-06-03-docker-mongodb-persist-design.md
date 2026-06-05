# Docker + MongoDB Persistence Design

**Date:** 2026-06-03  
**Branch:** 10-issue-8-guardar-documento-y-checksum-en-bd-nosql  
**Status:** Approved

## Context

The `/extract` endpoint currently extracts text from PDFs but does not persist anything to the database. The `ExtractedDocument` Beanie model and `ChecksumRepository` protocol exist but are unused at runtime. This design closes that gap by:

1. Running MongoDB in a Docker container (alongside the FastAPI app)
2. Wiring `/extract` to validate uniqueness, extract text, and save to MongoDB
3. Making the full stack runnable with `docker compose up`

## Architecture Overview

No new architectural layers are introduced. The existing four-layer structure (presentation → application → data → MongoDB) is preserved. The missing pieces are:

- Infrastructure: `docker-compose.yml` + `Dockerfile`
- Data layer: `data/repositories.py` — concrete `MongoChecksumRepository`
- Presentation layer: lifespan startup, dependency injection, updated `/extract` route

## Docker Infrastructure

### `docker-compose.yml`

Two services:

| Service | Image | Key config |
|---------|-------|-----------|
| `mongodb` | `mongo:8` | Named volume `mongo_data:/data/db`, healthcheck via `mongosh --eval "db.adminCommand('ping')"`, port `27017:27017` |
| `app` | Built from `Dockerfile` | Port `8000:8000`, env vars `DB_URL=mongodb://mongodb:27017` + `DB_NAME=pdf_extractext`, `depends_on: mongodb` with `condition: service_healthy` |

Named volume `mongo_data` declared at root level so data persists across `docker compose down` / `up` cycles.

Port `27017` exposed to host so `uv run pytest` (running outside Docker) can still hit the real MongoDB for integration tests.

### `Dockerfile`

Single-stage, `python:3.13-slim` base:
1. Install `uv` binary from official release
2. Copy `pyproject.toml` + `uv.lock`, run `uv sync --frozen --no-dev`
3. Copy source code
4. `CMD ["uv", "run", "uvicorn", "presentation.main:app", "--host", "0.0.0.0", "--port", "8000"]`

## Data Layer

### `data/repositories.py` (new file)

```python
class MongoChecksumRepository:
    async def exists(self, checksum: str) -> bool:
        return await ExtractedDocument.find_one(
            ExtractedDocument.checksum == checksum
        ) is not None
```

Satisfies the `ChecksumRepository` protocol from `application/checksum.py`. Single responsibility: query existence by checksum.

## Presentation Layer

### `presentation/main.py` changes

1. **Lifespan context manager** — calls `get_database_connection([ExtractedDocument])` on app startup so Beanie is initialized before any request is served.

2. **Dependency** — `get_repository() -> MongoChecksumRepository` injected via `Depends`.

3. **Updated `POST /extract`** — full flow:
   ```
   read bytes → calculate_checksum → ensure_unique_checksum (raises DuplicateDocumentError if duplicate)
             → extract_text_from_bytes → ExtractedDocument.insert() → return {text, checksum}
   ```

4. **Exception handler** — converts `DuplicateDocumentError` to `HTTPException(status_code=409, detail=...)`.

### Response schema change

`POST /extract` now returns:
```json
{"text": "...", "checksum": "sha256hex..."}
```

## Test Strategy

All new tests follow TDD: failing test written first, then production code.

| Test file | What's tested | DB required |
|-----------|--------------|-------------|
| `tests/test_api.py` | `GET /health` — patch `get_database_connection` so lifespan doesn't need MongoDB | No |
| `tests/test_database.py` | `MongoChecksumRepository.exists()` returns False/True; `POST /extract` saves document; `POST /extract` with duplicate returns 409 | Yes (MongoDB at `DB_URL`) |

## Verification

```bash
# Full stack via Docker
docker compose up --build
curl -F "file=@sample.pdf" http://localhost:8000/extract

# Local dev (MongoDB already running)
uv run pytest
uv run uvicorn presentation.main:app --reload

# Re-upload same PDF → expect 409
curl -F "file=@sample.pdf" http://localhost:8000/extract
```

## Files Changed

| File | Action |
|------|--------|
| `docker-compose.yml` | Create |
| `Dockerfile` | Create |
| `data/repositories.py` | Create |
| `presentation/main.py` | Modify (lifespan, dependency, `/extract` route) |
| `tests/test_api.py` | Modify (mock DB connection in fixture) |
| `tests/test_database.py` | Modify (add repository + endpoint integration tests) |
