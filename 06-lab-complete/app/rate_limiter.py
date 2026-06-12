"""Atomic Redis sliding-window rate limiter."""
import time
import uuid

from fastapi import HTTPException

from app.config import settings
from app.storage import client


_SCRIPT = client.register_script(
    """
    redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', ARGV[1])
    local count = redis.call('ZCARD', KEYS[1])
    if count >= tonumber(ARGV[3]) then
      return {0, count}
    end
    redis.call('ZADD', KEYS[1], ARGV[2], ARGV[4])
    redis.call('EXPIRE', KEYS[1], 60)
    return {1, count + 1}
    """
)


def check_rate_limit(user_id: str) -> int:
    now = time.time()
    allowed, count = _SCRIPT(
        keys=[f"rate:{user_id}"],
        args=[now - 60, now, settings.rate_limit_per_minute, f"{now}:{uuid.uuid4()}"],
    )
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded",
            headers={"Retry-After": "60"},
        )
    return settings.rate_limit_per_minute - int(count)
