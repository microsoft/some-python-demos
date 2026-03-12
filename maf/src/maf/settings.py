from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    azure_openai_endpoint: str | None = None
    azure_openai_deployment_name: str = "gpt-4o"
    tickets_api_base: str = "http://localhost:8000"


@lru_cache
def get_settings() -> Settings:
    return Settings()
