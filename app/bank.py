import copy
import json
import os
from pathlib import Path

from app.replies import outcome_d, with_phrase
from app.retrieve import get_index
from app.textnorm import normalise

_DEFAULT = Path(__file__).parent / "answer_bank.json"


def bank_path():
    return Path(os.environ.get("ANSWER_BANK_PATH", _DEFAULT))


def load_bank():
    path = bank_path()
    if not path.exists():
        return {"entries": []}
    return json.loads(path.read_text(encoding="utf-8"))


def citations_for(source_ids):
    by_id = {chunk["id"]: chunk for chunk in get_index().chunks}
    citations = []
    for source_id in source_ids or []:
        chunk = by_id.get(source_id)
        if chunk is None:
            continue
        citations.append(
            {
                "id": chunk["id"],
                "title": chunk.get("title", ""),
                "url": chunk.get("url", ""),
                "last_verified": chunk.get("last_verified", ""),
            }
        )
    return citations


def match_entry(question):
    wanted = normalise(question)
    if not wanted:
        return None
    for entry in load_bank().get("entries", []):
        questions = entry.get("questions") or {}
        for variants in questions.values():
            for variant in variants or []:
                if normalise(variant) == wanted:
                    return entry
    return None


def reply_from_entry(entry, language=None):
    reply = copy.deepcopy(entry.get("reply") or {})
    reply["citations"] = citations_for(entry.get("source_ids")) or reply.get("citations") or []
    if not str(entry.get("approved_on") or "").strip():
        return outcome_d(
            reply.get("language") or language,
            reply.get("reason_for_review") or "The answer bank entry has no approval date.",
            with_phrase(reply.get("spoken_answer", "")),
            with_phrase(reply.get("display_answer", "")),
            reply["citations"],
        )
    if language and not reply.get("language"):
        reply["language"] = language
    return reply


def bank_reply(question, language=None):
    entry = match_entry(question)
    if entry is None:
        return None
    return reply_from_entry(entry, language)
