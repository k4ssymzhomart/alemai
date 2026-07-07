"""Patients (hashed ids) and doctors (docs/05 §4, privacy posture docs/04 §6)."""

import datetime
import uuid

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import Sex, text_enum


class Patient(Base):
    """id is a salted SHA-256 hash of the source identifier — never raw ИИН."""

    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sex: Mapped[Sex] = mapped_column(text_enum(Sex, length=1))
    birth_year: Mapped[int] = mapped_column(Integer)
    attached: Mapped[bool] = mapped_column(Boolean, default=False)
    insured: Mapped[bool] = mapped_column(Boolean, default=False)
    death_date: Mapped[datetime.date | None] = mapped_column(Date)


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    org_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id"), index=True)
    full_name_masked: Mapped[str] = mapped_column(String(128))
    specialty: Mapped[str] = mapped_column(String(128))
    dept: Mapped[str] = mapped_column(String(128))
    schedule_ref: Mapped[str | None] = mapped_column(String(128))
