from fastapi import APIRouter

from src.api.v1.endpoints import edge_tts

api_router = APIRouter()
api_router.include_router(edge_tts.router, prefix="/tts", tags=["Edge TTS"])

