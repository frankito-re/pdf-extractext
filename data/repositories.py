from data.models import ExtractedDocument


class MongoChecksumRepository:
    async def exists(self, checksum: str) -> bool:
        return await ExtractedDocument.find_one(
            ExtractedDocument.checksum == checksum
        ) is not None

    async def save(self, text: str, checksum: str) -> None:
        await ExtractedDocument(text=text, checksum=checksum).insert()
