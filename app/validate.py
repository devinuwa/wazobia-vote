import json

from jsonschema import Draft202012Validator

from app.config import ICON_IDS, PHRASES_PATH, SCHEMA_PATH
from app.privacy import echoes_private_data

_VALIDATOR = None
_PHRASES = None

LANGUAGE_CODES = {
    "en": "en",
    "english": "en",
    "ha": "ha",
    "hausa": "ha",
    "ig": "ig",
    "igbo": "ig",
}


def schema_validator():
    global _VALIDATOR
    if _VALIDATOR is None:
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        _VALIDATOR = Draft202012Validator(schema)
    return _VALIDATOR


def phrases():
    global _PHRASES
    if _PHRASES is None:
        _PHRASES = json.loads(PHRASES_PATH.read_text(encoding="utf-8"))["not_yet_verified"]
    return _PHRASES


def reload_phrases():
    global _PHRASES
    _PHRASES = None


HIGH_STAKES_CUES = (
    "deadline",
    "eligib",
    "qualified to",
    "who can register",
    "who may register",
    "polling unit",
    "polling-unit",
    "where do i vote",
    "where to vote",
    "where can i vote",
    "legal right",
    "right to vote",
    "entitled to vote",
    "when is the election",
    "election date",
    "notice of election",
)


def is_high_stakes(question):
    folded = (question or "").casefold()
    return any(cue in folded for cue in HIGH_STAKES_CUES)


def has_unverified_phrase(text, language):
    folded = text.casefold()
    table = phrases()
    english = table.get("en", "").strip()
    if english and english.casefold() in folded:
        return True
    code = LANGUAGE_CODES.get((language or "").casefold(), (language or "").casefold())
    local = table.get(code, "").strip()
    return bool(local) and local.casefold() in folded


def validate_reply(reply, sources, profile=None, question=""):
    errors = []
    for error in schema_validator().iter_errors(reply):
        path = ".".join(str(part) for part in error.path)
        errors.append(f"{path or 'reply'}: {error.message}")
    if errors:
        return errors

    by_id = {source["id"]: source for source in sources}
    if reply["outcome"] == "A" and not reply["citations"]:
        errors.append("outcome A needs a citation")
    if reply["outcome"] == "B" and sources and not reply["citations"]:
        errors.append("outcome B needs a citation for the supported part")
    for citation in reply["citations"]:
        source = by_id.get(citation["id"])
        if source is None:
            errors.append(f"unknown citation {citation['id']}")
            continue
        for field in ("title", "url", "last_verified"):
            if citation[field] != source.get(field, ""):
                errors.append(f"citation {citation['id']} {field} does not match the source")

    spoken = reply["spoken_answer"]
    if any(char.isdigit() for char in spoken):
        errors.append("spoken_answer contains a digit")
    if "http://" in spoken.casefold() or "https://" in spoken.casefold() or "www." in spoken.casefold():
        errors.append("spoken_answer contains a url")
    if any(mark in spoken for mark in "*_`#[]<>"):
        errors.append("spoken_answer contains markdown")

    if profile == "text_only" and len(reply["steps"]) > 5:
        errors.append("text_only allows at most five steps")
    if profile == "plain":
        for step in reply["steps"]:
            if step["icon"] and step["icon"] not in ICON_IDS:
                errors.append(f"plain icon {step['icon']} is not in the icon list")

    if reply["needs_human_review"] and not reply["reason_for_review"].strip():
        errors.append("needs_human_review requires a reason")
    if not reply["needs_human_review"] and reply["reason_for_review"].strip():
        errors.append("reason_for_review must be empty when review is not needed")

    cited = []
    for citation in reply["citations"]:
        source = by_id.get(citation["id"])
        if source is not None:
            cited.append(source)
    only_unverified = bool(cited) and all(not source.get("last_verified", "").strip() for source in cited)
    if only_unverified and reply["outcome"] != "D" and is_high_stakes(question):
        errors.append("a high-stakes answer that rests only on a source with a blank last_verified must be outcome D")

    if reply["outcome"] == "D":
        if not has_unverified_phrase(reply["spoken_answer"], reply["language"]):
            errors.append("spoken_answer must say the answer is not yet verified")
        if not has_unverified_phrase(reply["display_answer"], reply["language"]):
            errors.append("display_answer must say the answer is not yet verified")

    if echoes_private_data(question, reply):
        errors.append("reply repeats a phone number, voter id, or address")
    return errors
