from datetime import datetime

from pydantic import BaseModel, ConfigDict


class VisitIn(BaseModel):
    """Body the frontend sends when a page loads."""
    page_path: str = "/"


class VisitOut(BaseModel):
    """What the "This is you" card shows."""
    ip_address: str | None
    location: str
    browser: str
    os: str
    device: str
    visited_at: datetime


class VisitRow(BaseModel):
    """One row of the admin list (built straight from the database model)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    visited_at: datetime
    page_path: str
    ip_address: str | None
    browser_name: str | None
    browser_version: str | None
    os_name: str | None
    os_version: str | None
    device_type: str
    country: str | None
    region: str | None
    city: str | None
