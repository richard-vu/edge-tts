from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
import sys

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.api.v1.router import api_router  # noqa: E402
from src.core.config import settings  # noqa: E402
from src.services.edge_tts_service import ensure_data_dir  # noqa: E402


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Ensure the backend/data directory exists on startup (DB tables are managed via Alembic)."""
    ensure_data_dir()
    yield


app = FastAPI(
    title="Edge TTS API",
    description="Backend API for Edge TTS",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.cors_methods_list,
    allow_headers=settings.cors_headers_list,
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"message": "Hello from FastAPI!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
