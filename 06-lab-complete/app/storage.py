"""Redis-backed shared state used by every application instance."""
import json
from datetime import datetime, timezone

import redis

from app.config import settings


client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def ping() -> bool:
    return bool(client.ping())


def load_history(session_id: str) -> list[dict]:
    values = client.lrange(f"session:{session_id}:history", 0, -1)
    return [json.loads(value) for value in values]


def append_history(session_id: str, role: str, content: str) -> None:
    key = f"session:{session_id}:history"
    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    pipeline = client.pipeline(transaction=True)
    pipeline.rpush(key, json.dumps(message, ensure_ascii=False))
    pipeline.ltrim(key, -20, -1)
    pipeline.expire(key, settings.session_ttl_seconds)
    pipeline.execute()


def delete_history(session_id: str) -> bool:
    return bool(client.delete(f"session:{session_id}:history"))
