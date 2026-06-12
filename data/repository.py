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

    async def update(self, id: str, text: Optional[str], checksum: Optional[str]) -> Optional[DocumentDTO]:
        doc = await ExtractedDocument.get(id)
        if doc is None:
            return None
        if text is not None:
            doc.text = text
        if checksum is not None:
            doc.checksum = checksum
        await doc.save()
        return DocumentDTO(id=str(doc.id), text=doc.text, checksum=doc.checksum)

    async def delete(self, id: str) -> bool:
        doc = await ExtractedDocument.get(id)
        if doc is None:
            return False
        await doc.delete()
        return True
