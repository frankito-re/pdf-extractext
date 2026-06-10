from typing import Optional
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from application.document_service import DocumentDTO
from presentation.main import app, get_document_repo

@pytest.mark.asyncio
async def test_ping_server():
    with patch("presentation.main.get_database_connection", new_callable=AsyncMock):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "pong"}


@pytest.mark.asyncio
async def test_read_document_by_id_returns_200():
    class MockRepo:
        async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
            return DocumentDTO(id=id, text="extracted text", checksum="abc123")

        async def get_all(self) -> list[DocumentDTO]:
            return []

    app.dependency_overrides[get_document_repo] = lambda: MockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/documents/abc123")

    assert response.status_code == 200
    assert response.json() == {"id": "abc123", "text": "extracted text", "checksum": "abc123"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_read_document_by_id_returns_404_when_not_found():
    class MockRepo:
        async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
            return None

        async def get_all(self) -> list[DocumentDTO]:
            return []

    app.dependency_overrides[get_document_repo] = lambda: MockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/documents/nonexistent")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_all_documents_returns_200():
    class MockRepo:
        async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
            return None

        async def get_all(self) -> list[DocumentDTO]:
            return [
                DocumentDTO(id="1", text="first", checksum="aaa"),
                DocumentDTO(id="2", text="second", checksum="bbb"),
            ]

    app.dependency_overrides[get_document_repo] = lambda: MockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/documents")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "1", "text": "first", "checksum": "aaa"},
        {"id": "2", "text": "second", "checksum": "bbb"},
    ]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_document_returns_200():
    class MockRepo:
        async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
            return DocumentDTO(id=id, text="original", checksum="old_hash")

        async def get_all(self) -> list[DocumentDTO]:
            return []

        async def update(self, id: str, text: Optional[str], checksum: Optional[str]) -> Optional[DocumentDTO]:
            return DocumentDTO(id=id, text=text or "original", checksum=checksum or "old_hash")

    app.dependency_overrides[get_document_repo] = lambda: MockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch("/documents/abc123", json={"text": "updated text"})

    assert response.status_code == 200
    assert response.json() == {"id": "abc123", "text": "updated text", "checksum": "old_hash"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_update_document_returns_404_when_not_found():
    class MockRepo:
        async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
            return None

        async def get_all(self) -> list[DocumentDTO]:
            return []

        async def update(self, id: str, text: Optional[str], checksum: Optional[str]) -> Optional[DocumentDTO]:
            return None

    app.dependency_overrides[get_document_repo] = lambda: MockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch("/documents/nonexistent", json={"text": "updated text"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()
