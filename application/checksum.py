import hashlib
from typing import Protocol

from application.exceptions import DuplicateDocumentError


class ChecksumRepository(Protocol):
    async def exists(self, checksum: str) -> bool: ...


def calculate_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


async def ensure_unique_checksum(checksum: str, repository: ChecksumRepository) -> None:
    if await repository.exists(checksum):
        raise DuplicateDocumentError(checksum)
