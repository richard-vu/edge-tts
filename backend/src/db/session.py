from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.core.config import BACKEND_DIR, settings
from src.db.base import Base
from src.models.tts_audio import TtsAudio  # noqa: F401
from src.utils.logger import logger


def _resolve_database_url(raw_url: str) -> str:
    """Resolve relative SQLite file paths against BACKEND_DIR."""
    prefix = "sqlite+aiosqlite:///./"
    if raw_url.startswith(prefix):
        relative_part = raw_url[len(prefix) :]
        abs_path = (BACKEND_DIR / relative_part).resolve()
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite+aiosqlite:///{abs_path}"
    return raw_url


DATABASE_URL = _resolve_database_url(settings.DATABASE_URL)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    poolclass=NullPool,
    connect_args={"timeout": 30},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def init_db() -> None:
    """Initialize database tables if they do not exist."""
    Path(BACKEND_DIR / "data").mkdir(parents=True, exist_ok=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully")
