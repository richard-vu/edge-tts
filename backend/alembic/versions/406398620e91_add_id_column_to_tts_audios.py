"""add id column to tts_audios

Revision ID: 406398620e91
Revises: bed42f2e3403
Create Date: 2026-10-30 14:17:08.004293

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '406398620e91'
down_revision: Union[str, Sequence[str], None] = 'bed42f2e3403'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tts_audios', sa.Column('id', sa.String(length=36), nullable=True))

    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT rowid, file_name FROM tts_audios WHERE id IS NULL")).fetchall()
    for row in rows:
        rowid, file_name = row
        stem = file_name[:-4] if file_name and file_name.endswith(".mp3") and len(file_name) == 40 else str(uuid.uuid7())
        conn.execute(
            sa.text("UPDATE tts_audios SET id = :id WHERE rowid = :rowid"),
            {"id": stem, "rowid": rowid},
        )

    op.create_table(
        'tts_audios_new',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('voice', sa.String(length=128), nullable=False),
        sa.Column('rate', sa.String(length=32), nullable=False),
        sa.Column('volume', sa.String(length=32), nullable=False),
        sa.Column('pitch', sa.String(length=32), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_tts_audios'),
        sa.UniqueConstraint('text', 'voice', 'rate', name='uq_tts_audios_text_voice_rate'),
    )
    op.execute(
        "INSERT INTO tts_audios_new (id, text, voice, rate, volume, pitch, file_name) "
        "SELECT id, text, voice, rate, volume, pitch, file_name FROM tts_audios"
    )
    op.drop_table('tts_audios')
    op.rename_table('tts_audios_new', 'tts_audios')


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table(
        'tts_audios_old',
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('voice', sa.String(length=128), nullable=False),
        sa.Column('rate', sa.String(length=32), nullable=False),
        sa.Column('volume', sa.String(length=32), nullable=False),
        sa.Column('pitch', sa.String(length=32), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('text', 'voice', 'rate', name='pk_tts_audios'),
    )
    op.execute(
        "INSERT INTO tts_audios_old (text, voice, rate, volume, pitch, file_name) "
        "SELECT text, voice, rate, volume, pitch, file_name FROM tts_audios"
    )
    op.drop_table('tts_audios')
    op.rename_table('tts_audios_old', 'tts_audios')
