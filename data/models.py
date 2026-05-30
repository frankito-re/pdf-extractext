from beanie import Document


class ExtractedDocument(Document):
    text: str
    checksum: str

    class Settings:
        name = "extracted_documents"
