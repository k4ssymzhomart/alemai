"""Import files and quarantined rows (docs/05 §4, ingest adapters docs/06 §2)."""

import datetime
import uuid
from typing import Any

from sqlalchemy import ARRAY, BigInteger, DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import ImportKind, text_enum


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.UTC)


class ImportFile(Base):
    __tablename__ = "import_files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    kind: Mapped[ImportKind] = mapped_column(text_enum(ImportKind))
    filename: Mapped[str] = mapped_column(String(255))
    rows_ok: Mapped[int] = mapped_column(Integer, default=0)
    rows_quarantined: Mapped[int] = mapped_column(Integer, default=0)
    control_sum: Mapped[int | None] = mapped_column(BigInteger)  # whole tenge
    loaded_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow
    )


class QuarantineRow(Base):
    __tablename__ = "quarantine_rows"

    import_file_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("import_files.id"), primary_key=True
    )
    row_no: Mapped[int] = mapped_column(Integer, primary_key=True)
    raw: Mapped[dict[str, Any]] = mapped_column(JSONB)
    errors: Mapped[list[str]] = mapped_column(ARRAY(Text))
