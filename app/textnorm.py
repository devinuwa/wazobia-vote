import re


def normalise(text):
    folded = (text or "").casefold()
    folded = re.sub(r"[^\w\s]", " ", folded, flags=re.UNICODE)
    return " ".join(folded.split())
