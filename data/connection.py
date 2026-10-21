from beanie import init_beanie
from .config import DatabaseSettings


# Única responsabilidad: inicializar la conexión de Beanie a Mongo (SOLID: SRP).
async def get_database_connection(document_models: list):
    # Los settings se leen acá, no al importar el módulo, para respetar las
    # variables DB_URL/DB_NAME seteadas justo antes del startup (tests, contenedores).
    settings = DatabaseSettings()

    await init_beanie(
        connection_string=f"{settings.url}/{settings.name}",
        document_models=document_models,
    )
