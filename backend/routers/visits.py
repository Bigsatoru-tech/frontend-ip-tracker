import logging
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Query, Request
from sqlalchemy.orm import Session

from core.config import get_settings
from core.database import SessionLocal, get_db
from core.security import require_admin
from core.tracker import Analysis, analyze
from crud import visit as visit_crud
from schemas import VisitIn, VisitOut, VisitRow

log = logging.getLogger("tracker")
router = APIRouter(prefix="/api", tags=["visits"])


def client_ip(request: Request) -> str | None:
    settings = get_settings()
    # Development only: pretend to be another visitor.
    if settings.is_dev:
        fake = request.headers.get("x-debug-ip")
        if fake:
            return fake.strip()
    # Behind a proxy/host the real visitor is the first X-Forwarded-For entry.
    # That header can be forged, so only trust it when TRUST_PROXY is on.
    if settings.trust_proxy:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


def format_location(a: Analysis) -> str:
    parts = [p for p in (a.city, a.region, a.country) if p]
    return ", ".join(parts) if parts else "Unknown"


def save_visit_task(analysis: Analysis, page_path: str, user_agent: str | None, visited_at: datetime) -> None:
    """Runs after the response has been sent. Must never raise.

    It opens its own session because the request's session is already closed by now.
    """
    db = SessionLocal()
    try:
        visit_crud.create_visit(
            db,
            analysis=analysis,
            page_path=page_path,
            user_agent=user_agent,
            visited_at=visited_at,
        )
    except Exception:
        log.exception("Could not save visit")
        db.rollback()
    finally:
        db.close()


@router.post("/visit", response_model=VisitOut)
def record_visit(body: VisitIn, request: Request, background: BackgroundTasks):
    """Called once by the frontend on page load. Records the visit and returns
    the details for the "This is you" card."""
    user_agent = request.headers.get("user-agent")
    now = datetime.now(timezone.utc)
    analysis = analyze(client_ip(request), user_agent)
    background.add_task(save_visit_task, analysis, body.page_path, user_agent, now)
    return VisitOut(
        ip_address=analysis.ip_truncated,
        location=format_location(analysis),
        browser=analysis.browser_name or "Unknown",
        os=analysis.os_name or "Unknown",
        device=(analysis.device_type or "unknown").capitalize(),
        visited_at=now,
    )


@router.get("/visits", response_model=list[VisitRow], dependencies=[Depends(require_admin)])
def list_visits(limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)):
    """Newest first. Needs the X-API-Key header."""
    return visit_crud.get_recent_visits(db, limit)
