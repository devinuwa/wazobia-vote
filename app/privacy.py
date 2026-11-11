import os
import re

PHONE = re.compile(r"(?:\+?\s?234|0)[7-9]\d{9}")
ACCOUNT_ID = re.compile(
    r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}"
)
BEARER = re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._\-]+=*")
KEY_TOKEN = re.compile(r"(?i)\b(?:sk|pk|rk)-[A-Za-z0-9_\-]{8,}")
NAMED_SECRET = re.compile(
    r"(?i)(api[_-]?key|token|secret|password)(['\"\s:=]+)[^\s'\"]{6,}"
)
LONG_DIGITS = re.compile(r"\d{8,}")
ADDRESS_CUES = (
    "my address",
    "i live at",
    "i stay at",
    "my house is",
    "my polling unit is",
)


def redact_for_log(text):
    cleaned = text or ""
    secret = os.environ.get("MODEL_API_KEY", "").strip()
    if secret and secret in cleaned:
        cleaned = cleaned.replace(secret, "[redacted]")
    cleaned = ACCOUNT_ID.sub("[id]", cleaned)
    cleaned = BEARER.sub("Bearer [redacted]", cleaned)
    cleaned = KEY_TOKEN.sub("[redacted]", cleaned)
    cleaned = NAMED_SECRET.sub(r"\1\2[redacted]", cleaned)
    return cleaned


def is_provider_error(text):
    folded = (text or "").casefold()
    if not folded.strip():
        return False
    if "model request failed" in folded or "no model is configured" in folded:
        return True
    if "does not exist" in folded and "team" in folded:
        return True
    return ACCOUNT_ID.search(text or "") is not None


def scrub_text(text):
    cleaned = PHONE.sub("[removed]", text)
    return LONG_DIGITS.sub("[removed]", cleaned)


def redact_question(question):
    folded = question.casefold()
    if any(cue in folded for cue in ADDRESS_CUES):
        return None, "unsure"
    cleaned = scrub_text(question)
    if cleaned != question:
        return cleaned, "redacted"
    return question, "ok"


def scrub_reply(reply):
    cleaned = dict(reply)
    for field in ("spoken_answer", "display_answer", "reason_for_review"):
        cleaned[field] = scrub_text(cleaned.get(field, ""))
    steps = []
    for step in cleaned.get("steps", []):
        steps.append({"text": scrub_text(step.get("text", "")), "icon": step.get("icon", "")})
    cleaned["steps"] = steps
    return cleaned


def echoes_private_data(question, reply):
    blob = " ".join(
        [
            reply.get("spoken_answer", ""),
            reply.get("display_answer", ""),
            reply.get("reason_for_review", ""),
            " ".join(step.get("text", "") for step in reply.get("steps", [])),
        ]
    )
    if PHONE.search(blob) or LONG_DIGITS.search(blob):
        return True
    folded_question = question.casefold()
    folded_blob = blob.casefold()
    for cue in ADDRESS_CUES:
        if cue not in folded_question:
            continue
        tail = folded_question.split(cue, 1)[1].strip(" :.,")[:80]
        if len(tail) > 8 and tail in folded_blob:
            return True
    return False
