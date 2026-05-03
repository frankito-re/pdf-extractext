from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    db_url: str = "mongodb://localhost:27017"
    db_name: str = "pdf_extractext"

    model_config = {"env_prefix": "DB_"}
