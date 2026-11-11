import re

from app.config import SOURCE_TOKEN_CAP

_PIECE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


def count_tokens(text):
    """Local token count: one token per short word or mark, one per four letters of a longer word."""
    if not text:
        return 0
    total = 0
    for piece in _PIECE.findall(text):
        if len(piece) > 4 and piece.isalnum():
            total += (len(piece) + 3) // 4
        else:
            total += 1
    return total


def fit_passages(passages, question, render, budget=SOURCE_TOKEN_CAP):
    chosen = [dict(passage) for passage in passages]
    while len(chosen) > 1 and count_tokens(render(chosen, question)) > budget:
        chosen.pop()
    if not chosen or count_tokens(render(chosen, question)) <= budget:
        return chosen
    original = chosen[0].get("text") or ""
    low = 0
    high = len(original)
    best = 0
    while low <= high:
        mid = (low + high) // 2
        chosen[0]["text"] = original[:mid]
        if count_tokens(render(chosen, question)) <= budget:
            best = mid
            low = mid + 1
        else:
            high = mid - 1
    chosen[0]["text"] = original[:best].rstrip()
    return chosen
