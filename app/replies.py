PHRASE = "This answer is not yet verified."


def with_phrase(text):
    cleaned = (text or "").strip()
    if "not yet verified" in cleaned.casefold():
        return cleaned or PHRASE
    if not cleaned:
        return PHRASE
    return cleaned + " " + PHRASE


def outcome_d(language, reason, spoken="", display="", citations=None):
    return {
        "outcome": "D",
        "language": language or "en",
        "language_confidence": "high",
        "spoken_answer": with_phrase(spoken),
        "display_answer": with_phrase(display),
        "steps": [],
        "citations": citations or [],
        "confidence": "low",
        "needs_human_review": True,
        "reason_for_review": reason,
    }
