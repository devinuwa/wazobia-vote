import json
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.config import DATA_DIR, QUESTION_LOG_RETENTION_HOURS, REVIEW_RETENTION_DAYS
from app.privacy import is_provider_error, redact_for_log, redact_question, scrub_reply

REVIEW_PATH = DATA_DIR / "review.jsonl"
LOG_PATH = DATA_DIR / "question-log.jsonl"
ERROR_COUNT_PATH = DATA_DIR / "system-errors.json"


def _now():
    return datetime.now(timezone.utc)


def _read_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def _write_jsonl(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    path.write_text(text, encoding="utf-8")


def _expired(row, now):
    if row.get("status", "pending") == "pending":
        return False
    stamp = row.get("status_set_at")
    if not stamp:
        return False
    set_at = datetime.fromisoformat(stamp)
    return now - set_at > timedelta(days=REVIEW_RETENTION_DAYS)


def _blank_provider_text(row):
    changed = False
    if is_provider_error(row.get("reason", "")):
        row["reason"] = ""
        changed = True
    reply = row.get("reply")
    if isinstance(reply, dict) and is_provider_error(reply.get("reason_for_review", "")):
        reply["reason_for_review"] = ""
        changed = True
    return changed


def purge_provider_error_text():
    rows = _read_jsonl(REVIEW_PATH)
    changed = sum(1 for row in rows if _blank_provider_text(row))
    if changed:
        _write_jsonl(REVIEW_PATH, rows)
    return changed


def list_reviews():
    now = _now()
    rows = _read_jsonl(REVIEW_PATH)
    kept = [row for row in rows if not _expired(row, now)]
    if len(kept) != len(rows):
        _write_jsonl(REVIEW_PATH, kept)
    return kept


def system_error_count():
    if not ERROR_COUNT_PATH.exists():
        return 0
    try:
        payload = json.loads(ERROR_COUNT_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return 0
    return int(payload.get("count", 0))


def record_system_error():
    count = system_error_count() + 1
    ERROR_COUNT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ERROR_COUNT_PATH.write_text(json.dumps({"count": count}), encoding="utf-8")
    return count


def _clip(value, limit):
    return redact_for_log(str(value or ""))[:limit]


def _bounded_reply(reply):
    public = scrub_reply(reply if isinstance(reply, dict) else {})
    steps = []
    for step in (public.get("steps") or [])[:6]:
        if not isinstance(step, dict):
            continue
        steps.append({"text": _clip(step.get("text"), 400), "icon": _clip(step.get("icon"), 40)})
    citations = []
    for item in (public.get("citations") or [])[:6]:
        if not isinstance(item, dict):
            continue
        citations.append(
            {
                "id": _clip(item.get("id"), 80),
                "title": _clip(item.get("title"), 300),
                "url": _clip(item.get("url"), 300),
                "last_verified": _clip(item.get("last_verified"), 40),
            }
        )
    return {
        "outcome": _clip(public.get("outcome"), 8),
        "language": _clip(public.get("language"), 8),
        "language_confidence": _clip(public.get("language_confidence"), 8),
        "spoken_answer": _clip(public.get("spoken_answer"), 2000),
        "display_answer": _clip(public.get("display_answer"), 2000),
        "steps": steps,
        "citations": citations,
        "confidence": _clip(public.get("confidence"), 8),
        "needs_human_review": bool(public.get("needs_human_review")),
        "reason_for_review": _clip(public.get("reason_for_review"), 500),
    }


def report_review(question, reply):
    if not isinstance(reply, dict):
        return None
    stored_reply = _bounded_reply(reply)
    stored_question, state = redact_question(question or "")
    row = {
        "id": uuid.uuid4().hex,
        "created_at": _now().isoformat(),
        "status": "pending",
        "status_set_at": None,
        "reason": "Reported by the user.",
        "reply": stored_reply,
    }
    if state != "unsure" and stored_question:
        row["question"] = _clip(stored_question, 500)
    rows = list_reviews()
    rows.append(row)
    _write_jsonl(REVIEW_PATH, rows)
    return row["id"]


def save_review(question, reply):
    if not reply.get("needs_human_review"):
        return None
    stored_question, state = redact_question(question)
    public = scrub_reply(reply)
    if is_provider_error(public.get("reason_for_review", "")):
        public["reason_for_review"] = ""
    row = {
        "id": uuid.uuid4().hex,
        "created_at": _now().isoformat(),
        "status": "pending",
        "status_set_at": None,
        "reason": public.get("reason_for_review", ""),
        "reply": public,
    }
    if state != "unsure" and stored_question:
        row["question"] = _clip(stored_question, 500)
    rows = list_reviews()
    rows.append(row)
    _write_jsonl(REVIEW_PATH, rows)
    return row["id"]


def set_review_status(row_id, status):
    if status not in {"pending", "accepted", "rejected"}:
        raise ValueError("status must be pending, accepted, or rejected")
    rows = list_reviews()
    found = False
    for row in rows:
        if row["id"] != row_id:
            continue
        found = True
        if status == "pending":
            row["status"] = "pending"
            row["status_set_at"] = None
        elif row.get("status") != status:
            row["status"] = status
            row["status_set_at"] = _now().isoformat()
        break
    if not found:
        return False
    _write_jsonl(REVIEW_PATH, rows)
    return True


def log_question(question):
    stored, state = redact_question(question)
    if state == "unsure" or not stored:
        return
    cutoff = _now() - timedelta(hours=QUESTION_LOG_RETENTION_HOURS)
    kept = []
    for row in _read_jsonl(LOG_PATH):
        stamp = datetime.fromisoformat(row["at"])
        if stamp >= cutoff:
            kept.append(row)
    kept.append({"at": _now().isoformat(), "question": stored})
    _write_jsonl(LOG_PATH, kept)
