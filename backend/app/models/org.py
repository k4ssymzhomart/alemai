"""Organizations (docs/05 §4)."""

import uuid

from sqlalchemy import Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.enums import OrgType, text_enum


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    name_kk: Mapped[str] = mapped_column(String(255))
    name_ru: Mapped[str] = mapped_column(String(255))
    type: Mapped[OrgType] = mapped_column(text_enum(OrgType))
    attached_population: Mapped[int] = mapped_column(Integer, default=0)
