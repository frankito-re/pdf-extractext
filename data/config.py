from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    url: str = "mongodb://localhost:27017"
    name: str = "pdf_extractext"

    model_config = {"env_prefix": "DB_"}
