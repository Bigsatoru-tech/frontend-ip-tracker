from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.tracker import Analysis
from models import Visit


def create_visit(
    db: Session,
    *,
    analysis: Analysis,
    page_path: str,
    user_agent: str | None,
    visited_at: datetime,
) -> Visit:
    visit = Visit(
        visited_at=visited_at,
        page_path=page_path.split("?")[0][:300] or "/",  # never store query strings
        ip_address=analysis.ip_truncated,
        browser_name=analysis.browser_name,
        browser_version=analysis.browser_version,
        os_name=analysis.os_name,
        os_version=analysis.os_version,
        device_type=analysis.device_type,
        country=analysis.country,
        region=analysis.region,
        city=analysis.city,
        user_agent_raw=(user_agent or "")[:500] or None,
    )
    db.add(visit)
    db.commit()
    return visit


def get_recent_visits(db: Session, limit: int = 50) -> list[Visit]:
    stmt = select(Visit).order_by(Visit.visited_at.desc(), Visit.id.desc()).limit(limit)
    return list(db.scalars(stmt).all())
