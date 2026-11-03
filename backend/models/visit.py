from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True)
    # SQLite does not store time zones: treat values read back as UTC.
    visited_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    page_path: Mapped[str] = mapped_column(String(300), default="/")
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)  # truncated
    browser_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    browser_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    os_name: Mapped[str | None] = mapped_column(String(80), nullable=True)
    os_version: Mapped[str | None] = mapped_column(String(40), nullable=True)
    device_type: Mapped[str] = mapped_column(String(20), default="unknown")
    country: Mapped[str | None] = mapped_column(String(100), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    user_agent_raw: Mapped[str | None] = mapped_column(Text, nullable=True)
