import pytest

from application.checksum import calculate_checksum, ensure_unique_checksum, save_document_if_unique
from application.exceptions import DuplicateDocumentError

STATIC_CONTENT = b"pdf-extractext static test content"
EXPECTED_SHA256 = "3a5b2ee6379e440b13f8686c74b2a9e2f19650fd1c32c8a0de9fda7bcbc66a40"


def test_checksum_of_known_content_returns_expected_hash():
    result = calculate_checksum(STATIC_CONTENT)
    assert result == EXPECTED_SHA256


@pytest.mark.asyncio
async def test_ensure_unique_checksum_raises_on_duplicate():
    class AlwaysExistsRepo:
        async def exists(self, checksum: str) -> bool:
            return True

    with pytest.raises(DuplicateDocumentError) as exc:
        await ensure_unique_checksum("abc123", AlwaysExistsRepo())

    assert exc.value.checksum == "abc123"


@pytest.mark.asyncio
async def test_ensure_unique_checksum_passes_when_unique():
    class NeverExistsRepo:
        async def exists(self, checksum: str) -> bool:
            return False

    await ensure_unique_checksum("abc123", NeverExistsRepo())


@pytest.mark.asyncio
async def test_document_is_inserted_after_successful_uniqueness_check():
    saved = []

    class TrackingRepo:
        async def exists(self, checksum: str) -> bool:
            return False

        async def save(self, text: str, checksum: str) -> None:
            saved.append((text, checksum))

    await save_document_if_unique("extracted text", "abc123", TrackingRepo())

    assert saved == [("extracted text", "abc123")]
