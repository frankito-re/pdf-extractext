from beanie import Document


class ExtractedDocument(Document):
    # Sin campo para los bytes originales del PDF: las reglas de negocio prohíben
    # almacenar el binario, solo se persisten el texto extraído y su checksum.
    text: str
    checksum: str

    class Settings:
        name = "extracted_documents"
