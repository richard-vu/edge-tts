import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_DIR = Path(__file__).resolve().parents[2]
ENV_FILE_NAME = os.getenv("ENV_FILE", ".env")
ENV_FILE_PATH = BACKEND_DIR / ENV_FILE_NAME
DEFAULT_SQLITE_PATH = BACKEND_DIR / "data" / "edge_tts.db"


def _parse_csv_setting(value: str) -> list[str]:
    """Parse a comma-separated string into a list of non-empty strings."""
    items = [item.strip() for item in value.split(",") if item.strip()]
    return items or ["*"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = f"sqlite+aiosqlite:///{DEFAULT_SQLITE_PATH}"
    TTS_DEFAULT_LOCALE: str = "en-US"
    TTS_DEFAULT_VOICE: str = "en-US-AndrewNeural"
    TTS_DEFAULT_RATE: str = "+0%"
    TTS_DEFAULT_VOLUME: str = "+0%"
    TTS_DEFAULT_PITCH: str = "+0Hz"

    CORS_ALLOW_ORIGINS: str = "*"
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: str = "*"
    CORS_ALLOW_HEADERS: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        return _parse_csv_setting(self.CORS_ALLOW_ORIGINS)

    @property
    def cors_methods_list(self) -> list[str]:
        return _parse_csv_setting(self.CORS_ALLOW_METHODS)

    @property
    def cors_headers_list(self) -> list[str]:
        return _parse_csv_setting(self.CORS_ALLOW_HEADERS)


settings = Settings()
