import re

_MONTHS = (
    "January|February|March|April|May|June|July|August|"
    "September|October|November|December"
)
_DATE = re.compile(
    rf"\b(?:\d{{1,2}}(?:st|nd|rd|th)?\s+(?:{_MONTHS})\s+\d{{4}}"
    rf"|(?:{_MONTHS})\s+\d{{1,2}}(?:st|nd|rd|th)?,?\s+\d{{4}}"
    rf"|\d{{4}}-\d{{2}}-\d{{2}}"
    rf"|\d{{1,2}}[/-]\d{{1,2}}[/-]\d{{2,4}})\b",
    re.IGNORECASE,
)
_SECTION = re.compile(r"\bsection\s+\d{1,3}\b", re.IGNORECASE)
_NUMBER = re.compile(r"\b\d[\d,]*(?:\.\d+)?\b")


def claims_in(text):
    found = []
    for pattern in (_DATE, _SECTION, _NUMBER):
        found.extend(match.group(0) for match in pattern.finditer(text or ""))
    return found


def missing_claims(reply, passages):
    cited = {item.get("id") for item in reply.get("citations") or []}
    blob = "\n".join(
        passage.get("text") or "" for passage in passages if passage.get("id") in cited
    ).casefold()
    missing = []
    seen = set()
    for field in ("spoken_answer", "display_answer"):
        for claim in claims_in(reply.get(field) or ""):
            key = claim.casefold()
            if key in seen:
                continue
            seen.add(key)
            if key not in blob:
                missing.append(claim)
    return missing
