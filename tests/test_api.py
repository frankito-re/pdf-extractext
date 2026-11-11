import typing
from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

import presentation.main as main_module
from application.checksum import ChecksumRepository
from application.document_service import DocumentDTO
from presentation.main import app, extract_text, get_checksum_repo, get_document_repo
from tests.test_pdf_extractor import make_pdf_bytes


class BaseMockRepo:
    async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
        return None

    async def get_all(self) -> list[DocumentDTO]:
        return []

    async def update(self, id: str, text: Optional[str], checksum: Optional[str]) -> Optional[DocumentDTO]:
        return None

    async def delete(self, id: str) -> bool:
        return False


@pytest.mark.asyncio
async def test_ping_server():
    with patch("presentation.container.get_database_connection", new_callable=AsyncMock):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "pong"}


@pytest.mark.asyncio
async def test_read_document_by_id_returns_200():
    class MockRepo(BaseMockRepo):
        async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
            return DocumentDTO(id=id, text="extracted text", checksum="abc123")

    app.dependency_overrides[get_document_repo] = lambda: MockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/documents/abc123")

    assert response.status_code == 200
    assert response.json() == {"id": "abc123", "text": "extracted text", "checksum": "abc123"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_read_document_by_id_returns_404_when_not_found():
    app.dependency_overrides[get_document_repo] = lambda: BaseMockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/documents/nonexistent")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_list_all_documents_returns_200():
    class MockRepo(BaseMockRepo):
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
    class MockRepo(BaseMockRepo):
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
    app.dependency_overrides[get_document_repo] = lambda: BaseMockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.patch("/documents/nonexistent", json={"text": "updated text"})

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_document_returns_204():
    class MockRepo(BaseMockRepo):
        async def delete(self, id: str) -> bool:
            return True

    app.dependency_overrides[get_document_repo] = lambda: MockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete("/documents/existing-id")

    assert response.status_code == 204
    assert response.text == ""

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_document_returns_404_when_not_found():
    app.dependency_overrides[get_document_repo] = lambda: BaseMockRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.delete("/documents/nonexistent")

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_deleted_document_returns_404():
    class MockRepo(BaseMockRepo):
        def __init__(self):
            self.deleted = False

        async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
            if self.deleted:
                return None
            return DocumentDTO(id=id, text="to be deleted", checksum="abc")

        async def delete(self, id: str) -> bool:
            self.deleted = True
            return True

    shared_repo = MockRepo()
    app.dependency_overrides[get_document_repo] = lambda: shared_repo

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        delete_response = await ac.delete("/documents/some-id")
        get_response = await ac.get("/documents/some-id")

    assert delete_response.status_code == 204
    assert get_response.status_code == 404
    assert get_response.json() == {"detail": "Document not found"}

    app.dependency_overrides.clear()


def test_extract_depends_on_checksum_port():
    assert typing.get_type_hints(extract_text)["repository"] is ChecksumRepository
    assert typing.get_type_hints(get_checksum_repo)["return"] is ChecksumRepository


@pytest.mark.asyncio
async def test_extract_persists_document_using_checksum_port():
    saved = []

    class FakeChecksumRepo:
        async def exists(self, checksum: str) -> bool:
            return False

        async def save(self, text: str, checksum: str) -> None:
            saved.append((text, checksum))

    app.dependency_overrides[get_checksum_repo] = lambda: FakeChecksumRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/extract",
            files={"file": ("document.pdf", make_pdf_bytes("Contenido"), "application/pdf")},
        )

    assert response.status_code == 200
    body = response.json()
    assert "Contenido" in body["text"]
    assert saved == [(body["text"], body["checksum"])]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_extract_returns_409_for_duplicate():
    class DuplicateChecksumRepo:
        async def exists(self, checksum: str) -> bool:
            return True

        async def save(self, text: str, checksum: str) -> None:
            raise AssertionError("save must not be called for a duplicate")

    app.dependency_overrides[get_checksum_repo] = lambda: DuplicateChecksumRepo()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/extract",
            files={"file": ("document.pdf", make_pdf_bytes("Duplicado"), "application/pdf")},
        )

    assert response.status_code == 409

    app.dependency_overrides.clear()


def test_main_has_no_infrastructure_imports():
    source = Path(main_module.__file__).read_text(encoding="utf-8")
    assert "from data" not in source
    assert "import data" not in source


def test_container_owns_repository_providers():
    from presentation import container

    assert container.get_document_repo is get_document_repo
    assert container.get_checksum_repo is get_checksum_repo
    assert callable(container.init_database)
