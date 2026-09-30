"""Application settings loaded from environment variables."""

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Define the environment-backed settings used by the backend."""

    supabase_url: str = Field(default="", validation_alias="SUPABASE_URL")
    supabase_key: str = Field(default="", validation_alias="SUPABASE_PUBLISHABLE_KEY")
    supabase_db_url: str = Field(validation_alias="SUPABASE_DB_URL")
    storage_bucket: str = Field(default="pharmalens-docs", validation_alias="STORAGE_BUCKET")
    storage_timeout_seconds: int = Field(
        default=120,
        ge=10,
        le=600,
        validation_alias="STORAGE_TIMEOUT_SECONDS",
    )
    google_api_key: str = Field(default="", validation_alias="GOOGLE_API_KEY")
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    llm_provider: str = Field(default="google", validation_alias="LLM_PROVIDER")
    llm_max_attempts: int = Field(
        default=2,
        ge=1,
        le=3,
        validation_alias="LLM_MAX_ATTEMPTS",
    )
    document_parser_provider: str = Field(
        default="native",
        validation_alias="DOCUMENT_PARSER_PROVIDER",
    )
    dolphin_model_path: str = Field(
        default="",
        validation_alias="DOLPHIN_MODEL_PATH",
    )
    dolphin_device: str = Field(default="auto", validation_alias="DOLPHIN_DEVICE")
    dolphin_max_pages: int = Field(default=100, ge=1, le=1000, validation_alias="DOLPHIN_MAX_PAGES")
    dolphin_max_new_tokens: int = Field(
        default=4096,
        ge=128,
        le=16384,
        validation_alias="DOLPHIN_MAX_NEW_TOKENS",
    )
    dolphin_native_text_threshold: int = Field(
        default=50,
        ge=0,
        le=100000,
        validation_alias="DOLPHIN_NATIVE_TEXT_THRESHOLD",
    )
    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")
    cors_origins: str = Field(
        default="http://localhost:5173,http://127.0.0.1:5173",
        validation_alias="CORS_ORIGINS",
    )
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=BACKEND_ROOT / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        """Return configured CORS origins as trimmed, non-empty values."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def database_url(self) -> str:
        """Return the configured Supabase PostgreSQL connection string."""
        return self.supabase_db_url


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings instance."""
    return Settings()


settings = get_settings()
