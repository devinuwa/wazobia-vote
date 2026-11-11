import re

from app.retrieve import get_index
from app.security import clean_text

_EXCERPT_CHARS = 600
_FURNITURE = re.compile(r"A\s+\d+\s+2026\s+No\.\s*\d+", re.IGNORECASE)


def evidence_for(reply):
    by_id = {chunk["id"]: chunk for chunk in get_index().chunks}
    items = []
    seen = set()
    for citation in (reply or {}).get("citations") or []:
        if not isinstance(citation, dict):
            continue
        chunk_id = citation.get("id")
        if not chunk_id or chunk_id in seen:
            continue
        chunk = by_id.get(chunk_id)
        if chunk is None:
            continue
        seen.add(chunk_id)
        kept = [line for line in (chunk.get("text") or "").splitlines() if not _FURNITURE.search(line)]
        text = " ".join(clean_text(" ".join(kept)).split())
        if len(text) > _EXCERPT_CHARS:
            text = text[:_EXCERPT_CHARS].rsplit(" ", 1)[0].rstrip() + "…"
        items.append(
            {
                "id": chunk["id"],
                "title": chunk.get("title") or "",
                "excerpt": text,
            }
        )
    return items
