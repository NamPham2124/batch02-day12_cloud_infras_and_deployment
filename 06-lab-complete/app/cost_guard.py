"""Atomic monthly LLM budget protection backed by Redis."""
from datetime import datetime, timezone

from fastapi import HTTPException

from app.config import settings
from app.storage import client


INPUT_USD_PER_1K = 0.00015
OUTPUT_USD_PER_1K = 0.0006
MICRO_USD = 1_000_000

_RECORD_SCRIPT = client.register_script(
    """
    local current = tonumber(redis.call('GET', KEYS[1]) or '0')
    local increment = tonumber(ARGV[1])
    local budget = tonumber(ARGV[2])
    if current + increment > budget then
      return {-1, current}
    end
    local total = redis.call('INCRBY', KEYS[1], increment)
    redis.call('EXPIRE', KEYS[1], 2764800)
    return {1, total}
    """
)


def estimate_cost_micro_usd(text: str, output: bool = False) -> int:
    tokens = max(1, len(text.split()) * 2)
    price = OUTPUT_USD_PER_1K if output else INPUT_USD_PER_1K
    return max(1, round(tokens / 1000 * price * MICRO_USD))


def record_cost(user_id: str, cost_micro_usd: int) -> float:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    budget_micro_usd = round(settings.monthly_budget_usd * MICRO_USD)
    allowed, total = _RECORD_SCRIPT(
        keys=[f"cost:{user_id}:{month}"],
        args=[cost_micro_usd, budget_micro_usd],
    )
    if int(allowed) != 1:
        raise HTTPException(status_code=402, detail="Monthly budget exceeded")
    return int(total) / MICRO_USD


def get_cost(user_id: str) -> float:
    month = datetime.now(timezone.utc).strftime("%Y-%m")
    return int(client.get(f"cost:{user_id}:{month}") or 0) / MICRO_USD
