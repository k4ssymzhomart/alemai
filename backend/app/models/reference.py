"""Reference data: 2026 Единый пакет mapping and regulation corpus (docs/05 §4)."""

import datetime
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date, ForeignKey, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import FundingSource, text_enum

EMBEDDING_DIM = 1024


class PackageMapping(Base):
    """A4: which funding source covers an icd10/service_code on a given date."""

    __tablename__ = "package_mapping"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    icd10: Mapped[str | None] = mapped_column(String(16), index=True)
    service_code: Mapped[str | None] = mapped_column(String(64), index=True)
    funding_source: Mapped[FundingSource] = mapped_column(text_enum(FundingSource))
    valid_from: Mapped[datetime.date] = mapped_column(Date)
    valid_to: Mapped[datetime.date | None] = mapped_column(Date)


class RegDocument(Base):
    __tablename__ = "reg_documents"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(512))
    number: Mapped[str] = mapped_column(String(64))
    lang: Mapped[str] = mapped_column(String(2))  # kk | ru
    url: Mapped[str | None] = mapped_column(String(512))


class RegChunk(Base):
    """RAG source chunks; embeddings via pgvector (docs/05 §6 regulation Q&A)."""

    __tablename__ = "reg_chunks"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    doc_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reg_documents.id"), index=True)
    anchor: Mapped[str] = mapped_column(String(128))  # e.g. "п. 12"
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(EMBEDDING_DIM))
