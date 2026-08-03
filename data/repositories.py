from data.models import ExtractedDocument


# Se mantiene separado de BeanieDocumentRepository (data/repository.py): este
# solo implementa el protocolo acotado ChecksumRepository que necesita /extract
# para garantizar unicidad, así ese endpoint no depende del CRUD completo.
class MongoChecksumRepository:
    async def exists(self, checksum: str) -> bool:
        return await ExtractedDocument.find_one(
            ExtractedDocument.checksum == checksum
        ) is not None

    async def save(self, text: str, checksum: str) -> None:
        await ExtractedDocument(text=text, checksum=checksum).insert()
