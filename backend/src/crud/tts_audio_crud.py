from sqlalchemy import asc, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.tts_audio import TtsAudio

SORTABLE_COLUMNS = {
    "id": TtsAudio.id,
    "text": TtsAudio.text,
    "vnMeaning": TtsAudio.vn_meaning,
    "vn_meaning": TtsAudio.vn_meaning,
    "voice": TtsAudio.voice,
    "rate": TtsAudio.rate,
    "volume": TtsAudio.volume,
    "pitch": TtsAudio.pitch,
    "fileName": TtsAudio.file_name,
    "file_name": TtsAudio.file_name,
}


async def get_tts_audio_by_id(
    db: AsyncSession,
    record_id: str,
) -> TtsAudio | None:
    """Fetch a TtsAudio record by its primary key ID."""
    stmt = select(TtsAudio).where(TtsAudio.id == record_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_tts_audio_by_key(
    db: AsyncSession,
    *,
    text: str,
    voice: str,
    rate: str,
) -> TtsAudio | None:
    """Fetch a TtsAudio record by its unique constraint (text, voice, rate)."""
    stmt = select(TtsAudio).where(
        TtsAudio.text == text,
        TtsAudio.voice == voice,
        TtsAudio.rate == rate,
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def save_or_update_tts_audio(
    db: AsyncSession,
    *,
    existing_record: TtsAudio | None,
    text: str,
    vn_meaning: str | None = None,
    voice: str,
    rate: str,
    volume: str,
    pitch: str,
    file_name: str | None,
) -> TtsAudio:
    """Create a new TtsAudio record or update the existing one with the new file_name and vn_meaning."""
    if existing_record is None:
        record = TtsAudio(
            text=text,
            vn_meaning=vn_meaning,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
            file_name=file_name,
        )
        db.add(record)
    else:
        if vn_meaning is not None:
            existing_record.vn_meaning = vn_meaning
        existing_record.volume = volume
        existing_record.pitch = pitch
        existing_record.file_name = file_name
        record = existing_record

    await db.commit()
    await db.refresh(record)
    return record


async def get_paginated_tts_audios(
    db: AsyncSession,
    *,
    search: str | None = "",
    page: int = 0,
    size: int = 20,
    sort_by: str = "text",
    sort_dir: str = "asc",
) -> tuple[list[TtsAudio], int]:
    """
    Query paginated TtsAudio records with optional text search and dynamic sorting.
    """
    base_stmt = select(TtsAudio)
    count_stmt = select(func.count()).select_from(TtsAudio)

    if search and search.strip():
        keyword = f"%{search.strip()}%"
        base_stmt = base_stmt.where(TtsAudio.text.ilike(keyword))
        count_stmt = count_stmt.where(TtsAudio.text.ilike(keyword))

    total_result = await db.execute(count_stmt)
    total_elements = int(total_result.scalar_one() or 0)

    if size <= 0 or total_elements == 0:
        return [], total_elements

    sort_column = SORTABLE_COLUMNS.get(sort_by, TtsAudio.text)
    order_expr = desc(sort_column) if sort_dir.strip().lower() == "desc" else asc(sort_column)

    stmt = (
        base_stmt.order_by(order_expr)
        .offset(page * size)
        .limit(size)
    )
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    return items, total_elements


async def delete_tts_audios_by_ids(
    db: AsyncSession,
    ids: list[str],
) -> list[TtsAudio]:
    """Fetch and delete TtsAudio records matching the provided list of IDs."""
    if not ids:
        return []

    stmt = select(TtsAudio).where(TtsAudio.id.in_(ids))
    result = await db.execute(stmt)
    records = list(result.scalars().all())

    if not records:
        return []

    for record in records:
        await db.delete(record)

    await db.commit()
    return records
