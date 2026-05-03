import pytest
from beanie import Document, init_beanie

from data.config import DatabaseSettings


class SampleDoc(Document):
    name: str
    value: int

    class Settings:
        name = "test_documents"


@pytest.mark.asyncio
async def test_write_and_read_from_database():
    settings = DatabaseSettings()

    await init_beanie(
        connection_string=f"{settings.db_url}/{settings.db_name}",
        document_models=[SampleDoc],
    )

    # Limpiar datos previos
    await SampleDoc.delete_all()

    # Escribir dato de prueba
    doc = SampleDoc(name="test", value=42)
    await doc.insert()

    # Leer dato de prueba
    found = await SampleDoc.find_one({"name": "test"})

    assert found is not None
    assert found.name == "test"
    assert found.value == 42

    # Limpiar
    await SampleDoc.delete_all()
