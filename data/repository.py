from typing import Optional

from application.document_service import DocumentDTO
from data.models import ExtractedDocument


# Se mantiene separado de MongoChecksumRepository (data/repositories.py): este
# implementa el protocolo completo DocumentRepository para el CRUD, mientras que
# la unicidad de checksum al escribir la maneja el repositorio más acotado de arriba.
class BeanieDocumentRepository:
    def _to_dto(self, doc: ExtractedDocument) -> DocumentDTO:
        return DocumentDTO(id=str(doc.id), text=doc.text, checksum=doc.checksum)

    async def get_by_id(self, id: str) -> Optional[DocumentDTO]:
        doc = await ExtractedDocument.get(id)
        if doc is None:
            return None
        return self._to_dto(doc)

    async def get_all(self) -> list[DocumentDTO]:
        docs = await ExtractedDocument.all().to_list()
        return [self._to_dto(d) for d in docs]

    async def update(self, id: str, text: Optional[str], checksum: Optional[str]) -> Optional[DocumentDTO]:
        doc = await ExtractedDocument.get(id)
        if doc is None:
            return None
        if text is not None:
            doc.text = text
        if checksum is not None:
            doc.checksum = checksum
        await doc.save()
        return self._to_dto(doc)

    async def delete(self, id: str) -> bool:
        doc = await ExtractedDocument.get(id)
        if doc is None:
            return False
        await doc.delete()
        return True
