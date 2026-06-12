"""API key authentication."""
import hashlib
import hmac

from fastapi import Header, HTTPException

from app.config import settings


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    x_user_id: str | None = Header(default=None),
) -> str:
    if not x_api_key or not hmac.compare_digest(x_api_key, settings.agent_api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key")

    # X-User-ID identifies a caller in this educational shared-key setup.
    raw_identity = x_user_id or x_api_key
    return hashlib.sha256(raw_identity.encode()).hexdigest()[:24]
