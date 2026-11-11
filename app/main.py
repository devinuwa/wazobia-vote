import hmac
import logging
import re
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.answer import answer_question
from app.config import REVIEW_RETENTION_DAYS, require_review_password
from app.evidence import evidence_for
from app.security import (
    clean_text,
    clear_failures,
    note_failure,
    security_headers,
    too_many,
    too_many_failures,
)
from app.review_store import (
    list_reviews,
    purge_provider_error_text,
    report_review,
    set_review_status,
    system_error_count,
)

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / "static"
security = HTTPBasic(realm="Wazobia Vote review")


def _server_log():
    logger = logging.getLogger("wazobia")
    logger.disabled = False
    logger.setLevel(logging.WARNING)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
    return logger


@asynccontextmanager
async def lifespan(_app):
    require_review_password()
    cleared = purge_provider_error_text()
    _server_log().warning("stored provider error text cleared from %s review rows", cleared)
    yield


app = FastAPI(
    title="Wazobia vote",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)
app.mount("/static", StaticFiles(directory=STATIC), name="static")

_ROW_ID = re.compile(r"^[0-9a-f]{32}$")


@app.middleware("http")
async def shield(request: Request, call_next):
    host = request.client.host if request.client else "local"
    if too_many(request.url.path, host):
        response = JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Wait a moment and try again."},
        )
        return security_headers(response)
    response = await call_next(request)
    return security_headers(response)


class AskBody(BaseModel):
    question: str = Field(max_length=5000)
    language: str | None = None
    accessibility_profile: str | None = None


class StatusBody(BaseModel):
    status: str


class ReportBody(BaseModel):
    question: str = Field(default="", max_length=5000)
    reply: dict


PROFILES = {"voice", "text_only", "large_text", "plain"}
LANGUAGES = {"en", "ha", "ig"}
REVIEW_STATUSES = {"pending", "accepted", "rejected"}


def question_problem(question):
    text = clean_text(question)
    if not text:
        return "Type a question before asking."
    if len(text) < 3:
        return "Type at least 3 characters."
    if len(text) > 500:
        return "Keep the question to 500 characters or fewer."
    return ""


def require_reviewer(request: Request, credentials: HTTPBasicCredentials = Depends(security)):
    host = request.client.host if request.client else "local"
    if too_many_failures(host):
        raise HTTPException(status_code=429, detail="Too many attempts. Wait a moment and try again.")
    expected = require_review_password()
    if not hmac.compare_digest(credentials.password, expected):
        note_failure(host)
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
            headers={"WWW-Authenticate": "Basic"},
        )
    clear_failures(host)
    return credentials.username


@app.get("/")
def home():
    return FileResponse(STATIC / "index.html")


@app.get("/review")
def review_page(_username: str = Depends(require_reviewer)):
    return FileResponse(STATIC / "review.html")


@app.get("/api/reviews")
def reviews(_username: str = Depends(require_reviewer)):
    return {
        "reviews": list_reviews(),
        "expire_days": REVIEW_RETENTION_DAYS,
        "system_errors": system_error_count(),
    }


@app.post("/api/reviews/{row_id}")
def update_review(row_id: str, body: StatusBody, _username: str = Depends(require_reviewer)):
    if not _ROW_ID.fullmatch(row_id or ""):
        raise HTTPException(status_code=404, detail="review not found")
    if body.status not in REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="status must be pending, accepted, or rejected")
    if not set_review_status(row_id, body.status):
        raise HTTPException(status_code=404, detail="review not found")
    return {"ok": True}


@app.post("/api/report")
def report(body: ReportBody):
    display = clean_text(str((body.reply or {}).get("display_answer") or ""))
    if not display:
        raise HTTPException(status_code=400, detail="A reply is required.")
    row_id = report_review(body.question, body.reply)
    if not row_id:
        raise HTTPException(status_code=400, detail="The report could not be saved.")
    return {"ok": True}


@app.post("/api/ask")
def ask(body: AskBody):
    question = clean_text(body.question)
    problem = question_problem(question)
    if problem:
        raise HTTPException(status_code=400, detail=problem)
    language = clean_text(body.language or "").lower() or None
    profile = clean_text(body.accessibility_profile or "").lower() or None
    if language and language not in LANGUAGES:
        raise HTTPException(status_code=400, detail="language must be en, ha, or ig")
    if profile and profile not in PROFILES:
        raise HTTPException(status_code=400, detail="unknown accessibility profile")
    result = answer_question(question, language=language, profile=profile)
    payload = {
        "reply": result["reply"],
        "evidence": evidence_for(result["reply"]),
        "fallback": bool(result["fallback"]),
    }
    if result["fallback"]:
        return JSONResponse(status_code=503, content={"status": "fallback", **payload})
    return payload
