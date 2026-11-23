import pytest
import pytest_asyncio
from pymongo import AsyncMongoClient

from data.config import DatabaseSettings
from data.connection import get_database_connection
from data.models import ExtractedDocument
from data.repositories import MongoChecksumRepository
from data.repository import BeanieDocumentRepository


async def _mongodb_available() -> bool:
    client = AsyncMongoClient(DatabaseSettings().url, serverSelectionTimeoutMS=500)
    try:
        await client.admin.command("ping")
        return True
    except Exception:
        return False
    finally:
        await client.close()


@pytest_asyncio.fixture(autouse=True)
async def initialized_database():
    if not await _mongodb_available():
        pytest.skip("MongoDB is not available; skipping integration tests")
    await get_database_connection([ExtractedDocument])
    await ExtractedDocument.delete_all()
    yield
    await ExtractedDocument.delete_all()


@pytest.mark.asyncio
async def test_checksum_repository_saves_and_detects_document():
    repo = MongoChecksumRepository()
    assert await repo.exists("chk-1") is False
    await repo.save("hola", "chk-1")
    assert await repo.exists("chk-1") is True


@pytest.mark.asyncio
async def test_document_repository_lists_and_reads_persisted_documents():
    await MongoChecksumRepository().save("hola", "chk-1")
    repo = BeanieDocumentRepository()
    docs = await repo.get_all()
    assert len(docs) == 1
    found = await repo.get_by_id(docs[0].id)
    assert found is not None
    assert found.text == "hola"
    assert found.checksum == "chk-1"


@pytest.mark.asyncio
async def test_document_repository_updates_and_deletes():
    await MongoChecksumRepository().save("hola", "chk-1")
    repo = BeanieDocumentRepository()
    doc_id = (await repo.get_all())[0].id

    updated = await repo.update(doc_id, text="nuevo", checksum=None)
    assert updated is not None
    assert updated.text == "nuevo"
    assert updated.checksum == "chk-1"

    assert await repo.delete(doc_id) is True
    assert await repo.get_by_id(doc_id) is None
