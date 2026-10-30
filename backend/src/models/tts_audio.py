import uuid

from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class TtsAudio(Base):
    """ORM entity representing generated TTS audio metadata."""

    __tablename__ = "tts_audios"
    __table_args__ = (
        UniqueConstraint("text", "voice", "rate", name="uq_tts_audios_text_voice_rate"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid7()),
    )
    text: Mapped[str] = mapped_column(Text, nullable=False)
    vn_meaning: Mapped[str | None] = mapped_column("vn_meaning", Text, nullable=True)
    voice: Mapped[str] = mapped_column(String(128), nullable=False)
    rate: Mapped[str] = mapped_column(String(32), nullable=False)
    volume: Mapped[str] = mapped_column(String(32), nullable=False)
    pitch: Mapped[str] = mapped_column(String(32), nullable=False)
    file_name: Mapped[str | None] = mapped_column("file_name", String(255), nullable=True)
