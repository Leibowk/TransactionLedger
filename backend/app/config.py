"""Application configuration via Pydantic BaseSettings."""
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_file() -> Path:
    """Path to .env in backend root."""
    return Path(__file__).resolve().parent.parent / ".env"


class DatabaseConfig(BaseSettings):
    """Database connection settings."""

    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = ""

    @property
    def async_database_url(self) -> str:
        """PostgreSQL URL for asyncpg driver."""
        if not self.DATABASE_URL:
            return ""
        if self.DATABASE_URL.startswith("postgresql://"):
            return self.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
        if "postgresql" in self.DATABASE_URL:
            return self.DATABASE_URL.replace("postgresql+psycopg2", "postgresql+asyncpg", 1)
        return self.DATABASE_URL


class AppConfig(BaseSettings):
    """Application settings (environment, CORS, etc.)."""

    model_config = SettingsConfigDict(
        env_file=_env_file(),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ENVIRONMENT: str = "local"
    CORS_ORIGINS: str = (
        "http://localhost:5173,http://localhost:3000,"
        "http://127.0.0.1:5173,http://127.0.0.1:3000"
    )

    @property
    def cors_origins_list(self) -> list[str]:
        """CORS origins as a list."""
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


# Singleton instances (lazy-loaded to allow tests to override)
_database_config: DatabaseConfig | None = None
_app_config: AppConfig | None = None


def get_database_config() -> DatabaseConfig:
    global _database_config
    if _database_config is None:
        _database_config = DatabaseConfig()
    return _database_config


def get_app_config() -> AppConfig:
    global _app_config
    if _app_config is None:
        _app_config = AppConfig()
    return _app_config
