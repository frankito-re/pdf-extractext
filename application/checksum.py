import hashlib
from typing import Protocol

from application.exceptions import DuplicateDocumentError


class ChecksumRepository(Protocol):
    async def exists(self, checksum: str) -> bool: ...
    async def save(self, text: str, checksum: str) -> None: ...


def calculate_checksum(content: bytes) -> str:
    # SHA-256 sobre los bytes crudos del PDF (no sobre el texto extraído): dos
    # archivos distintos nunca deben colisionar, y re-extraer debe ser siempre determinístico.
    return hashlib.sha256(content).hexdigest()


async def ensure_unique_checksum(checksum: str, repository: ChecksumRepository) -> None:
    if await repository.exists(checksum):
        raise DuplicateDocumentError(checksum)


async def save_document_if_unique(
    text: str, checksum: str, repository: ChecksumRepository
) -> None:
    # La existencia debe chequearse antes de guardar: la regla de no-duplicados
    # exige rechazar el upload directamente, no persistirlo y limpiar después.
    await ensure_unique_checksum(checksum, repository)
    await repository.save(text, checksum)
