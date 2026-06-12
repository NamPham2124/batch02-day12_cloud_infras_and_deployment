"""Production-ready, Redis-backed AI agent API."""
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.auth import verify_api_key
from app.config import settings
from app.cost_guard import estimate_cost_micro_usd, get_cost, record_cost
from app.mock_llm import ask as llm_ask
from app.rate_limiter import check_rate_limit
from app.storage import append_history, delete_history, load_history, ping


logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)
START_TIME = time.time()
INSTANCE_ID = os.getenv("RAILWAY_REPLICA_ID", f"instance-{uuid.uuid4().hex[:8]}")
is_ready = False


def log_event(event: str, **fields) -> None:
    logger.info(json.dumps({"event": event, "instance": INSTANCE_ID, **fields}))


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global is_ready
    ping()
    is_ready = True
    log_event("startup", version=settings.app_version)
    yield
    # Uvicorn handles SIGTERM and waits for in-flight requests before this cleanup.
    is_ready = False
    log_event("shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url=None if settings.environment == "production" else "/docs",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type", "X-API-Key", "X-User-ID"],
)


@app.middleware("http")
async def request_logging(request: Request, call_next):
    started = time.time()
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Instance-ID"] = INSTANCE_ID
    log_event(
        "request",
        method=request.method,
        path=request.url.path,
        status=response.status_code,
        duration_ms=round((time.time() - started) * 1000, 1),
    )
    return response


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    session_id: str | None = Field(default=None, max_length=100)


class AskResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    turn: int
    served_by: str
    requests_remaining: int
    monthly_cost_usd: float
    timestamp: str


@app.get("/")
def root():
    return {"app": settings.app_name, "version": settings.app_version}


@app.post("/ask", response_model=AskResponse)
def ask_agent(body: AskRequest, user_id: str = Depends(verify_api_key)):
    remaining = check_rate_limit(user_id)
    session_id = body.session_id or str(uuid.uuid4())

    # Reserve input cost before the LLM call, then record output cost afterward.
    monthly_cost = record_cost(user_id, estimate_cost_micro_usd(body.question))
    append_history(session_id, "user", body.question)
    answer = llm_ask(body.question)
    append_history(session_id, "assistant", answer)
    monthly_cost = record_cost(user_id, estimate_cost_micro_usd(answer, output=True))
    history = load_history(session_id)

    return AskResponse(
        session_id=session_id,
        question=body.question,
        answer=answer,
        turn=sum(message["role"] == "user" for message in history),
        served_by=INSTANCE_ID,
        requests_remaining=remaining,
        monthly_cost_usd=monthly_cost,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.get("/sessions/{session_id}")
def session_history(session_id: str, _user_id: str = Depends(verify_api_key)):
    history = load_history(session_id)
    if not history:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"session_id": session_id, "messages": history}


@app.delete("/sessions/{session_id}")
def remove_session(session_id: str, _user_id: str = Depends(verify_api_key)):
    return {"deleted": delete_history(session_id)}


@app.get("/usage")
def usage(user_id: str = Depends(verify_api_key)):
    return {
        "monthly_cost_usd": get_cost(user_id),
        "monthly_budget_usd": settings.monthly_budget_usd,
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
        "instance": INSTANCE_ID,
        "uptime_seconds": round(time.time() - START_TIME, 1),
    }


@app.get("/ready")
def ready():
    if not is_ready:
        raise HTTPException(status_code=503, detail="Not ready")
    try:
        ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc
    return {"ready": True, "instance": INSTANCE_ID}
