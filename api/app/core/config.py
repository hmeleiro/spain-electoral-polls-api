from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=API_DIR / ".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@localhost:5432/spainelectoralpollsdb",
        alias="DATABASE_URL",
    )
    api_env: str = Field(default="development", alias="API_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    database_connect_timeout: int = Field(default=5, alias="DATABASE_CONNECT_TIMEOUT")
    cors_origins: str = Field(default="", alias="CORS_ORIGINS")
    enable_admin_endpoints: bool = Field(default=False, alias="ENABLE_ADMIN_ENDPOINTS")
    cache_enabled: bool = Field(default=True, alias="CACHE_ENABLED")
    cache_ttl_seconds: int = Field(default=300, alias="CACHE_TTL_SECONDS")
    cache_max_entries: int = Field(default=512, alias="CACHE_MAX_ENTRIES")

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
