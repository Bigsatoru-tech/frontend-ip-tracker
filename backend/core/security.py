import secrets

from fastapi import Header, HTTPException

from core.config import get_settings


def require_admin(x_api_key: str | None = Header(default=None)) -> None:
    """Dependency that protects admin-only routes.

    The caller must send the header `X-API-Key: <ADMIN_KEY>`.
    FastAPI turns the parameter name `x_api_key` into that header name.
    """
    settings = get_settings()
    if not settings.admin_key:
        raise HTTPException(status_code=503, detail="ADMIN_KEY is not configured")
    # compare_digest takes the same time however many characters match,
    # which stops timing attacks from guessing the key one character at a time.
    if not x_api_key or not secrets.compare_digest(x_api_key, settings.admin_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
