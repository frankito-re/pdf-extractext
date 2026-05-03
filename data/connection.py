from beanie import init_beanie
from .config import DatabaseSettings


async def get_database_connection(document_models: list):
    settings = DatabaseSettings()

    await init_beanie(
        connection_string=f"{settings.db_url}/{settings.db_name}",
        document_models=document_models,
    )
