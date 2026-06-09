from typing import Optional

from application.document_service import DocumentDTO
from data.models import ExtractedDocument


class BeanieDocumentRepository:
    async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
        doc = await ExtractedDocument.get(id)
        if doc is None:
            return None
        return DocumentDTO(id=str(doc.id), text=doc.text, checksum=doc.checksum)

    async def get_all(self) -> list[DocumentDTO]:
        docs = await ExtractedDocument.all().to_list()
        return [DocumentDTO(id=str(d.id), text=d.text, checksum=d.checksum) for d in docs]
