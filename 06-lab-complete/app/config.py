"""Application configuration loaded from environment variables."""
import os
from dataclasses import dataclass, field


def _bool_env(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).lower() in {"1", "true", "yes"}


@dataclass(frozen=True)
class Settings:
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8000")))
    environment: str = field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    debug: bool = field(default_factory=lambda: _bool_env("DEBUG"))

    app_name: str = field(default_factory=lambda: os.getenv("APP_NAME", "Production AI Agent"))
    app_version: str = field(default_factory=lambda: os.getenv("APP_VERSION", "2.0.0"))
    llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "mock-llm"))

    agent_api_key: str = field(default_factory=lambda: os.getenv("AGENT_API_KEY", ""))
    allowed_origins: list[str] = field(
        default_factory=lambda: os.getenv("ALLOWED_ORIGINS", "*").split(",")
    )

    redis_url: str = field(
        default_factory=lambda: os.getenv("REDIS_URL", "redis://localhost:6379/0")
    )
    rate_limit_per_minute: int = field(
        default_factory=lambda: int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
    )
    monthly_budget_usd: float = field(
        default_factory=lambda: float(os.getenv("MONTHLY_BUDGET_USD", "10.0"))
    )
    session_ttl_seconds: int = field(
        default_factory=lambda: int(os.getenv("SESSION_TTL_SECONDS", "86400"))
    )

    def validate(self) -> "Settings":
        if not self.agent_api_key:
            raise ValueError("AGENT_API_KEY must be set")
        if self.environment == "production" and self.agent_api_key.startswith("dev-"):
            raise ValueError("Use a non-development AGENT_API_KEY in production")
        if self.rate_limit_per_minute < 1 or self.monthly_budget_usd <= 0:
            raise ValueError("Rate limit and monthly budget must be positive")
        return self


settings = Settings().validate()
