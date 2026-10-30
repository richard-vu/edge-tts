from fastapi import APIRouter, BackgroundTasks, Body, Depends, Path as ApiPath, Query, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db
from src.core.config import settings
from src.schemas.base_response import BaseResponse
from src.schemas.edge_tts_schema import (
    GenerateAudioRequest,
    SupportedLanguageResponse,
    TtsAudioResponse,
    VoiceResponse,
)
from src.schemas.page_response import PageResponse
from src.services.edge_tts_service import (
    delete_audios_by_ids,
    enqueue_or_get_audio,
    get_audio_file_path,
    get_supported_languages,
    get_voices_by_lang,
    list_tts_audios,
)
from src.utils.logger import logger

router = APIRouter()


@router.get(
    "",
    response_model=BaseResponse[PageResponse[TtsAudioResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get paginated list of generated TTS audios",
)
async def get_tts_audios(
    search: str | None = Query(
        default="",
        description="Search keyword for text (if null or empty, returns all records paginated)",
    ),
    page: int = Query(
        default=0,
        ge=0,
        description="Page number (must be greater than or equal to 0)",
    ),
    size: int = Query(
        default=20,
        ge=0,
        le=100,
        description="Page size (between 0 and 100)",
    ),
    sort_by: str = Query(
        default="text",
        alias="sortBy",
        description="Field to sort by (default: 'text')",
    ),
    sort_dir: str = Query(
        default="asc",
        alias="sortDir",
        description="Sort direction: 'asc' or 'desc' (default: 'asc')",
    ),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[PageResponse[TtsAudioResponse]] | JSONResponse:
    """Retrieve paginated TTS audio records with optional search and sorting."""
    try:
        page_data = await list_tts_audios(
            db=db,
            search=search,
            page=page,
            size=size,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
        return BaseResponse.ok(
            data=page_data,
            message="Fetched TTS audio list successfully",
        )
    except ValueError as exc:
        logger.warning(f"Validation error in get_tts_audios: {exc}")
        error_resp = BaseResponse.bad_request(str(exc))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_resp.model_dump(mode="json"),
        )
    except Exception as exc:
        logger.exception(f"Unexpected error while listing TTS audios: {exc}")
        error_resp = BaseResponse.internal_error("Failed to fetch TTS audio list")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.model_dump(mode="json"),
        )


@router.get(
    "/supported-languages",
    response_model=BaseResponse[list[SupportedLanguageResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get all supported language codes and locales",
)
async def fetch_supported_languages() -> BaseResponse[list[SupportedLanguageResponse]] | JSONResponse:
    """Retrieve all supported language codes and their corresponding locales from Edge TTS."""
    try:
        data = await get_supported_languages()
        items = [SupportedLanguageResponse.model_validate(item) for item in data]
        return BaseResponse.ok(
            data=items,
            message="Fetched supported languages successfully",
        )
    except Exception as exc:
        logger.exception(f"Unexpected error while fetching supported languages: {exc}")
        error_resp = BaseResponse.internal_error("Failed to fetch supported languages")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.model_dump(mode="json"),
        )


@router.get(
    "/voices",
    response_model=BaseResponse[list[VoiceResponse]],
    status_code=status.HTTP_200_OK,
    summary="Get available voices by locale",
)
async def fetch_voices_by_lang(
    lang: str = Query(
        default=settings.TTS_DEFAULT_LOCALE,
        description="Full locale in '<language_code>-<country_code>' format (e.g., 'en-US', 'vi-VN')",
        examples=[settings.TTS_DEFAULT_LOCALE, "vi-VN"],
    ),
) -> BaseResponse[list[VoiceResponse]] | JSONResponse:
    """Retrieve available Edge TTS voices filtered strictly by locale."""
    try:
        voices = await get_voices_by_lang(lang=lang)
        items = [VoiceResponse.model_validate(voice) for voice in voices]
        return BaseResponse.ok(
            data=items,
            message=f"Fetched voices for locale '{lang}' successfully",
        )
    except ValueError as exc:
        logger.warning(f"Validation error in fetch_voices_by_lang: {exc}")
        error_resp = BaseResponse.bad_request(str(exc))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_resp.model_dump(mode="json"),
        )
    except Exception as exc:
        logger.exception(f"Unexpected error while fetching voices for locale '{lang}': {exc}")
        error_resp = BaseResponse.internal_error("Failed to fetch voices")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.model_dump(mode="json"),
        )


@router.post(
    "/generate-audio",
    response_model=BaseResponse[str],
    status_code=status.HTTP_201_CREATED,
    summary="Generate an audio file from text using Edge TTS",
)
async def create_audio(
    payload: GenerateAudioRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[str] | JSONResponse:
    """Queue speech audio generation in the background or return existing fileName immediately if already generated."""
    try:
        file_name, is_ready = await enqueue_or_get_audio(
            db=db,
            background_tasks=background_tasks,
            text=payload.text,
            voice=payload.voice,
            rate=payload.rate,
            volume=payload.volume,
            pitch=payload.pitch,
        )
        return BaseResponse.created(
            data=file_name,
            message="Audio generated successfully" if is_ready else "Audio generation started in background",
        )
    except ValueError as exc:
        logger.warning(f"Validation error in create_audio: {exc}")
        error_resp = BaseResponse.bad_request(str(exc))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_resp.model_dump(mode="json"),
        )
    except Exception as exc:
        logger.exception(f"Unexpected error while generating audio: {exc}")
        error_resp = BaseResponse.internal_error("Failed to generate audio")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.model_dump(mode="json"),
        )


@router.get(
    "/audio/{fileName}",
    response_class=FileResponse,
    response_model=None,
    status_code=status.HTTP_200_OK,
    summary="Get MP3 audio file by fileName",
)
async def download_audio(
    file_name: str = ApiPath(
        ...,
        alias="fileName",
        description="Generated MP3 file name (e.g., '01a18b1c-c8d6-77b4-abc2-acbbc4a429e4.mp3')",
    ),
) -> FileResponse | JSONResponse:
    """Return the MP3 audio file matching the provided fileName."""
    try:
        audio_path = get_audio_file_path(file_name)
        return FileResponse(
            path=audio_path,
            media_type="audio/mpeg",
            filename=audio_path.name,
        )
    except ValueError as exc:
        logger.warning(f"Invalid fileName in download_audio: {exc}")
        error_resp = BaseResponse.bad_request(str(exc))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_resp.model_dump(mode="json"),
        )
    except FileNotFoundError as exc:
        error_resp = BaseResponse.not_found(str(exc))
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=error_resp.model_dump(mode="json"),
        )
    except Exception as exc:
        logger.exception(f"Unexpected error while serving audio file '{file_name}': {exc}")
        error_resp = BaseResponse.internal_error("Failed to retrieve audio file")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.model_dump(mode="json"),
        )


@router.delete(
    "",
    response_model=BaseResponse[list[str]],
    status_code=status.HTTP_200_OK,
    summary="Delete TTS audio records and MP3 files by a list of IDs",
)
async def delete_audios(
    ids: list[str] = Body(
        ...,
        min_length=1,
        description="List of TtsAudio IDs (UUID v7) to delete",
        examples=[["01a18b41-3eb8-7285-b25b-2985505fa15b"]],
    ),
    db: AsyncSession = Depends(get_db),
) -> BaseResponse[list[str]] | JSONResponse:
    """Delete TtsAudio records from the database and remove their corresponding MP3 files from backend/data."""
    try:
        deleted_ids = await delete_audios_by_ids(db=db, ids=ids)
        return BaseResponse.ok(
            data=deleted_ids,
            message=f"Deleted {len(deleted_ids)} audio record(s) successfully",
        )
    except ValueError as exc:
        logger.warning(f"Validation error in delete_audios: {exc}")
        error_resp = BaseResponse.bad_request(str(exc))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=error_resp.model_dump(mode="json"),
        )
    except Exception as exc:
        logger.exception(f"Unexpected error while deleting audios: {exc}")
        error_resp = BaseResponse.internal_error("Failed to delete audio records")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_resp.model_dump(mode="json"),
        )

