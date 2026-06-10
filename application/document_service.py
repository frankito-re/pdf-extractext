from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class DocumentDTO:
    id: str
    text: str
    checksum: str


class DocumentRepository(Protocol):
    async def get_by_id(self, id: str) -> Optional[DocumentDTO]: ...
    async def get_all(self) -> list[DocumentDTO]: ...


async def get_document(id: str, repository: DocumentRepository) -> Optional[DocumentDTO]:
    return await repository.get_by_id(id)


async def get_all_documents(repository: DocumentRepository) -> list[DocumentDTO]:
    return await repository.get_all()
