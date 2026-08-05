import hashlib
from typing import Protocol

from application.exceptions import DuplicateDocumentError


# Protocol angosto (solo exists/save) en vez de reutilizar el DocumentRepository
# completo de document_service.py: /extract no necesita get/update/delete (SOLID: ISP).
class ChecksumRepository(Protocol):
    async def exists(self, checksum: str) -> bool: ...
    async def save(self, text: str, checksum: str) -> None: ...


def calculate_checksum(content: bytes) -> str:
    # Una sola responsabilidad, calcular el hash (SOLID: SRP), resuelta con hashlib
    # de la librería estándar sin envolturas extra (KISS).
    # SHA-256 sobre los bytes crudos del PDF (no sobre el texto extraído): dos
    # archivos distintos nunca deben colisionar, y re-extraer debe ser siempre determinístico.
    return hashlib.sha256(content).hexdigest()


# Separada de save_document_if_unique para que la regla de unicidad tenga una
# sola fuente de verdad, reutilizable y testeable de forma aislada (DRY / SOLID: SRP).
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
