import asyncio
import re
import uuid
from pathlib import Path
from typing import Literal

import aiohttp
import edge_tts
from edge_tts.data_classes import TTSConfig
from edge_tts.typing import Voice
from fastapi import BackgroundTasks
from googletrans import Translator
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.crud.tts_audio_crud import (
    SORTABLE_COLUMNS,
    delete_tts_audios_by_ids,
    get_paginated_tts_audios,
    get_tts_audio_by_id,
    get_tts_audio_by_key,
    save_or_update_tts_audio,
)
from src.db.session import AsyncSessionLocal
from src.schemas.edge_tts_schema import TtsAudioResponse
from src.schemas.page_response import PageResponse
from src.utils.logger import logger

BACKEND_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BACKEND_DIR / "data"

BoundaryType = Literal["WordBoundary", "SentenceBoundary"]
LOCALE_PATTERN = re.compile(r"^[a-zA-Z]{2,3}-[a-zA-Z]{2,4}$")
MAX_TEXT_LENGTH = 5000
_IN_FLIGHT_RECORD_IDS: set[str] = set()


def ensure_data_dir() -> Path:
    """
    Ensure the backend/data directory exists and is writable.
    """
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True, mode=0o775)
        logger.info(f"Created data directory at: {DATA_DIR}")

    return DATA_DIR


async def get_supported_languages(
    *,
    connector: aiohttp.BaseConnector | None = None,
    proxy: str | None = None,
) -> list[dict[str, str | list[str]]]:
    """
    Retrieve all supported language codes and their corresponding locales from Edge TTS.

    Args:
        connector (aiohttp.BaseConnector | None, optional): Custom aiohttp connector instance.
        proxy (str | None, optional): Proxy URL string (e.g., "http://127.0.0.1:8080").

    Returns:
        list[dict[str, str | list[str]]]: Sorted list of languages and their locales,
            e.g., [{"lang": "vi", "locales": ["vi-VN"]}, ...].
    """
    logger.info("Fetching supported languages and locales from Edge TTS")
    voices = await edge_tts.list_voices(connector=connector, proxy=proxy)

    lang_map: dict[str, set[str]] = {}
    for voice in voices:
        locale = voice.get("Locale", "")
        if not locale or "-" not in locale:
            continue
        lang_code = locale.split("-")[0]
        lang_map.setdefault(lang_code, set()).add(locale)

    result: list[dict[str, str | list[str]]] = [
        {"lang": lang_code, "locales": sorted(locales)}
        for lang_code, locales in sorted(lang_map.items())
    ]

    logger.info(f"Retrieved {len(result)} supported language group(s)")
    return result


async def get_voices_by_lang(
    lang: str = settings.TTS_DEFAULT_LOCALE,
    *,
    connector: aiohttp.BaseConnector | None = None,
    proxy: str | None = None,
) -> list[Voice]:
    """
    Retrieve available Edge TTS voices filtered strictly by locale (<language_code>-<country_code>).

    Args:
        lang (str, optional): Full locale in '<language_code>-<country_code>' format.
            Defaults to settings.TTS_DEFAULT_LOCALE.
        connector (aiohttp.BaseConnector | None, optional): Custom aiohttp connector instance.
        proxy (str | None, optional): Proxy URL string (e.g., "http://127.0.0.1:8080").

    Returns:
        list[Voice]: List of matching voices for the specified locale.
    """
    if not lang or not lang.strip():
        logger.error("Failed to list voices: 'lang' parameter is empty.")
        raise ValueError("The 'lang' parameter must not be empty.")

    cleaned_lang = lang.strip()
    if not LOCALE_PATTERN.fullmatch(cleaned_lang):
        logger.error(
            f"Invalid 'lang' format '{cleaned_lang}'. Expected '<language_code>-<country_code>' (e.g., 'vi-VN')."
        )
        raise ValueError(
            "Invalid 'lang' format. Expected '<language_code>-<country_code>' (e.g., 'vi-VN', 'en-US')."
        )

    normalized_locale = cleaned_lang.lower()
    logger.info(f"Fetching voices for locale: {cleaned_lang}")

    all_voices = await edge_tts.list_voices(connector=connector, proxy=proxy)
    matched_voices = [
        voice
        for voice in all_voices
        if voice.get("Locale", "").lower() == normalized_locale
    ]

    logger.info(f"Found {len(matched_voices)} voice(s) for locale '{cleaned_lang}'")
    return matched_voices


async def generate_audio(
    text: str,
    voice: str = settings.TTS_DEFAULT_VOICE,
    *,
    rate: str = settings.TTS_DEFAULT_RATE,
    volume: str = settings.TTS_DEFAULT_VOLUME,
    pitch: str = settings.TTS_DEFAULT_PITCH,
    boundary: BoundaryType = "SentenceBoundary",
    connector: aiohttp.BaseConnector | None = None,
    proxy: str | None = None,
    connect_timeout: int = 10,
    receive_timeout: int = 60,
    output_filename: str | None = None,
    save_metadata: bool = False,
) -> Path:
    """
    Generate an audio file from text using edge-tts and save it to backend/data.

    Args:
        text (str): The text to convert to speech (Required).
        voice (str, optional): The voice short name. Defaults to settings.TTS_DEFAULT_VOICE.
        rate (str, optional): Speaking speed modifier. Defaults to settings.TTS_DEFAULT_RATE.
        volume (str, optional): Volume modifier. Defaults to settings.TTS_DEFAULT_VOLUME.
        pitch (str, optional): Pitch modifier. Defaults to settings.TTS_DEFAULT_PITCH.
        boundary (Literal["WordBoundary", "SentenceBoundary"], optional):
            Boundary type for metadata/subtitles generation. Defaults to "SentenceBoundary".
        connector (aiohttp.BaseConnector | None, optional): Custom aiohttp connector instance.
        proxy (str | None, optional): Proxy URL string (e.g., "http://127.0.0.1:8080").
        connect_timeout (int, optional): Socket connection timeout in seconds. Defaults to 10.
        receive_timeout (int, optional): Socket receive timeout in seconds. Defaults to 60.
        output_filename (str | None, optional): Custom output filename. Auto-generates a UUID v7 if omitted.
        save_metadata (bool, optional): Whether to save accompanying metadata (.json). Defaults to False.

    Returns:
        Path: Absolute path to the generated audio file inside backend/data.
    """
    if not text or not text.strip():
        logger.error("Audio generation failed: 'text' parameter is empty.")
        raise ValueError("The 'text' parameter must not be empty.")
    if len(text) > MAX_TEXT_LENGTH:
        logger.error(f"Audio generation failed: 'text' length ({len(text)}) exceeds {MAX_TEXT_LENGTH} characters.")
        raise ValueError(f"The 'text' parameter must not exceed {MAX_TEXT_LENGTH} characters.")
    if not voice or not voice.strip():
        logger.error("Audio generation failed: 'voice' parameter is empty.")
        raise ValueError("The 'voice' parameter must not be empty.")

    data_dir = ensure_data_dir()

    file_stem = Path(output_filename).stem if output_filename else str(uuid.uuid7())
    audio_path = data_dir / f"{file_stem}.mp3"
    metadata_path = (data_dir / f"{file_stem}.json") if save_metadata else None

    logger.info(
        f"Generating audio: voice={voice}, rate={rate}, volume={volume}, pitch={pitch} -> {audio_path.name}"
    )

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
        boundary=boundary,
        connector=connector,
        proxy=proxy,
        connect_timeout=connect_timeout,
        receive_timeout=receive_timeout,
    )

    await communicate.save(
        audio_fname=str(audio_path),
        metadata_fname=str(metadata_path) if metadata_path else None,
    )

    logger.info(f"Audio saved successfully at: {audio_path}")
    return audio_path


async def translate_to_vietnamese(text: str, timeout: float = 8.0) -> str | None:
    """
    Translate input text to Vietnamese using googletrans with a strict timeout.

    Args:
        text (str): Source text to translate.
        timeout (float, optional): Max seconds to wait for translation. Defaults to 8.0.

    Returns:
        str | None: Translated Vietnamese text, or None if translation fails or times out.
    """
    if not text or not text.strip():
        return None

    async def _do_translate() -> str | None:
        async with Translator() as translator:
            result = await translator.translate(text.strip(), dest="vi")
            translated_text = getattr(result, "text", None)
            if translated_text:
                logger.info(f"Translated text to Vietnamese successfully: '{translated_text}'")
                return str(translated_text)
        return None

    try:
        return await asyncio.wait_for(_do_translate(), timeout=timeout)
    except Exception as exc:
        logger.warning(f"Failed or timed out translating text to Vietnamese via googletrans: {exc}")
        return None


def validate_tts_params(
    *,
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
) -> None:
    """Validate text and Edge TTS parameters synchronously before queueing work."""
    if not text or not text.strip():
        raise ValueError("The 'text' parameter must not be empty.")
    if len(text) > MAX_TEXT_LENGTH:
        raise ValueError(f"The 'text' parameter must not exceed {MAX_TEXT_LENGTH} characters.")
    if not voice or not voice.strip():
        raise ValueError("The 'voice' parameter must not be empty.")
    TTSConfig(
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
        boundary="SentenceBoundary",
    )


async def process_audio_generation_task(
    *,
    record_id: str,
    text: str,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
    output_filename: str,
    need_translation: bool = True,
) -> None:
    """
    Background worker that concurrently generates the MP3 file and translates text to Vietnamese,
    then updates the TtsAudio record in the database.
    """
    audio_path: Path | None = None
    try:
        logger.info(f"Starting background audio generation for record_id={record_id} -> {output_filename}")
        if need_translation:
            vn_meaning, audio_path = await asyncio.gather(
                translate_to_vietnamese(text),
                generate_audio(
                    text=text,
                    voice=voice,
                    rate=rate,
                    volume=volume,
                    pitch=pitch,
                    output_filename=output_filename,
                ),
            )
        else:
            vn_meaning = None
            audio_path = await generate_audio(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch,
                output_filename=output_filename,
            )

        async with AsyncSessionLocal() as db:
            record = await get_tts_audio_by_id(db, record_id)
            if record is None:
                logger.warning(
                    f"Record {record_id} was deleted while generating '{audio_path.name}', removing orphan file."
                )
                audio_path.unlink(missing_ok=True)
                return

            if vn_meaning:
                record.vn_meaning = vn_meaning
            record.file_name = audio_path.name
            record.volume = volume
            record.pitch = pitch
            await db.commit()
            logger.info(f"Background audio generation completed for record_id={record_id}: {audio_path.name}")
    except Exception as exc:
        logger.exception(f"Background audio generation failed for record_id={record_id}: {exc}")
        if audio_path is not None:
            audio_path.unlink(missing_ok=True)
    finally:
        _IN_FLIGHT_RECORD_IDS.discard(record_id)


async def enqueue_or_get_audio(
    db: AsyncSession,
    background_tasks: BackgroundTasks,
    *,
    text: str,
    voice: str = settings.TTS_DEFAULT_VOICE,
    rate: str = settings.TTS_DEFAULT_RATE,
    volume: str = settings.TTS_DEFAULT_VOLUME,
    pitch: str = settings.TTS_DEFAULT_PITCH,
) -> tuple[str, bool]:
    """
    Validate parameters, return existing audio fileName immediately if already generated on disk,
    or create a pending database record and schedule MP3 generation in BackgroundTasks.

    Returns:
        tuple[str, bool]: (file_name, is_ready_immediately)
    """
    validate_tts_params(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
    )
    data_dir = ensure_data_dir()

    existing_record = await get_tts_audio_by_key(
        db,
        text=text,
        voice=voice,
        rate=rate,
    )

    if existing_record is not None and existing_record.file_name:
        existing_file_path = data_dir / existing_record.file_name
        if existing_file_path.is_file():
            logger.info(
                f"Reusing existing audio file '{existing_record.file_name}' for voice={voice}, rate={rate}"
            )
            return existing_record.file_name, True

    if existing_record is not None and existing_record.id in _IN_FLIGHT_RECORD_IDS:
        logger.info(f"Audio generation already in progress for record_id={existing_record.id}")
        return existing_record.file_name or f"{existing_record.id}.mp3", False

    record = await save_or_update_tts_audio(
        db,
        existing_record=existing_record,
        text=text,
        vn_meaning=existing_record.vn_meaning if existing_record else None,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
        file_name=None,
    )

    target_file_name = f"{uuid.uuid7()}.mp3"
    _IN_FLIGHT_RECORD_IDS.add(record.id)
    background_tasks.add_task(
        process_audio_generation_task,
        record_id=record.id,
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
        pitch=pitch,
        output_filename=target_file_name,
        need_translation=not bool(record.vn_meaning),
    )

    return target_file_name, False


async def get_or_create_audio(
    db: AsyncSession,
    *,
    text: str,
    voice: str = settings.TTS_DEFAULT_VOICE,
    rate: str = settings.TTS_DEFAULT_RATE,
    volume: str = settings.TTS_DEFAULT_VOLUME,
    pitch: str = settings.TTS_DEFAULT_PITCH,
) -> str:
    """
    Check if an audio record for (text, voice, rate) already exists with a valid file in backend/data.
    If it exists and the file is present on disk, return the existing fileName immediately.
    Otherwise, concurrently generate a new audio file and translate text to Vietnamese,
    save/update the record in SQLite, and return the new fileName.
    """
    data_dir = ensure_data_dir()

    existing_record = await get_tts_audio_by_key(
        db,
        text=text,
        voice=voice,
        rate=rate,
    )

    if existing_record is not None and existing_record.file_name:
        existing_file_path = data_dir / existing_record.file_name
        if existing_file_path.is_file():
            if not existing_record.vn_meaning:
                vn_meaning = await translate_to_vietnamese(text)
                if vn_meaning:
                    existing_record.vn_meaning = vn_meaning
                    await db.commit()
            logger.info(
                f"Reusing existing audio file '{existing_record.file_name}' for voice={voice}, rate={rate}"
            )
            return existing_record.file_name
        logger.warning(
            f"Record found for (voice={voice}, rate={rate}) with fileName='{existing_record.file_name}', "
            f"but file is missing in {data_dir}. Regenerating audio."
        )
    elif existing_record is not None:
        logger.warning(
            f"Record found for (voice={voice}, rate={rate}) without fileName. Generating new audio."
        )

    if existing_record is not None and existing_record.vn_meaning:
        vn_meaning = existing_record.vn_meaning
        audio_path = await generate_audio(
            text=text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
    else:
        vn_meaning, audio_path = await asyncio.gather(
            translate_to_vietnamese(text),
            generate_audio(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch,
            ),
        )

    try:
        record = await save_or_update_tts_audio(
            db,
            existing_record=existing_record,
            text=text,
            vn_meaning=vn_meaning,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
            file_name=audio_path.name,
        )
    except Exception as exc:
        logger.error(
            f"Database save failed after generating '{audio_path.name}', removing orphan file: {exc}"
        )
        audio_path.unlink(missing_ok=True)
        raise

    return record.file_name or audio_path.name


def get_audio_file_path(file_name: str) -> Path:
    """
    Resolve and validate the path to an MP3 audio file inside backend/data.

    Args:
        file_name (str): Name of the audio file (e.g., '<uuid_v7>.mp3').

    Returns:
        Path: Validated absolute path to the MP3 file.
    """
    if not file_name or not file_name.strip():
        logger.error("Failed to get audio file: 'fileName' is empty.")
        raise ValueError("The 'fileName' parameter must not be empty.")

    cleaned_name = file_name.strip()
    if Path(cleaned_name).name != cleaned_name or ".." in cleaned_name:
        logger.error(f"Invalid file name '{cleaned_name}': path traversal detected.")
        raise ValueError("Invalid 'fileName' parameter.")

    if not cleaned_name.lower().endswith(".mp3"):
        cleaned_name = f"{cleaned_name}.mp3"

    data_dir = ensure_data_dir()
    file_path = (data_dir / cleaned_name).resolve()

    if file_path.parent != data_dir.resolve() or not file_path.is_file():
        logger.warning(f"Audio file not found in data directory: {cleaned_name}")
        raise FileNotFoundError(f"Audio file '{cleaned_name}' not found.")

    logger.info(f"Serving audio file: {file_path.name}")
    return file_path


async def list_tts_audios(
    db: AsyncSession,
    *,
    search: str | None = "",
    page: int = 0,
    size: int = 20,
    sort_by: str = "text",
    sort_dir: str = "asc",
) -> PageResponse[TtsAudioResponse]:
    """
    Retrieve a paginated list of TtsAudio records with optional search and sorting.
    """
    cleaned_sort_by = (sort_by or "text").strip()
    if cleaned_sort_by not in SORTABLE_COLUMNS:
        raise ValueError(
            f"Invalid 'sortBy' field '{cleaned_sort_by}'. Allowed values: text, voice, rate, volume, pitch, fileName."
        )

    cleaned_sort_dir = (sort_dir or "asc").strip().lower()
    if cleaned_sort_dir not in ("asc", "desc"):
        raise ValueError("Invalid 'sortDir' value. Allowed values: 'asc', 'desc'.")

    logger.info(
        f"Listing TTS audios: search='{search or ''}', page={page}, size={size}, "
        f"sortBy={cleaned_sort_by}, sortDir={cleaned_sort_dir}"
    )

    items, total_elements = await get_paginated_tts_audios(
        db,
        search=search,
        page=page,
        size=size,
        sort_by=cleaned_sort_by,
        sort_dir=cleaned_sort_dir,
    )

    return PageResponse[TtsAudioResponse].of(
        content=items,
        page_no=page,
        page_size=size,
        total_elements=total_elements,
        mapper=TtsAudioResponse.model_validate,
    )


async def delete_audios_by_ids(
    db: AsyncSession,
    ids: list[str],
) -> list[str]:
    """
    Delete TtsAudio records from the database by IDs and remove their MP3 files from backend/data.

    Args:
        db (AsyncSession): Active database session.
        ids (list[str]): List of TtsAudio record IDs to delete.

    Returns:
        list[str]: List of deleted record IDs.
    """
    cleaned_ids = [item.strip() for item in ids if item and item.strip()]
    if not cleaned_ids:
        logger.error("Failed to delete audios: 'ids' list is empty.")
        raise ValueError("The 'ids' list must not be empty.")

    logger.info(f"Deleting TTS audio records for IDs: {cleaned_ids}")
    deleted_records = await delete_tts_audios_by_ids(db, cleaned_ids)

    data_dir = ensure_data_dir().resolve()
    deleted_ids: list[str] = []

    for record in deleted_records:
        deleted_ids.append(record.id)
        if not record.file_name:
            continue

        safe_name = Path(record.file_name).name
        if safe_name != record.file_name or ".." in safe_name:
            logger.warning(f"Skipped unsafe fileName during deletion: {record.file_name}")
            continue

        file_path = (data_dir / safe_name).resolve()
        if file_path.parent == data_dir and file_path.is_file():
            try:
                file_path.unlink()
                logger.info(f"Deleted MP3 file from data directory: {file_path.name}")
            except OSError as exc:
                logger.warning(f"Failed to delete MP3 file '{file_path.name}': {exc}")

    logger.info(f"Successfully deleted {len(deleted_ids)} TTS audio record(s)")
    return deleted_ids



