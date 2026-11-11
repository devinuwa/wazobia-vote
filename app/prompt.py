import re

from app.config import APP_NAME, ICON_IDS, PROMPT_PATH

FENCE = re.compile(r"```\n(.*?)\n```", re.S)

EXTRA_SENTENCES = (
    "If the user writes in a language you do not support, say so in simple English and offer English, Hausa or Igbo. "
    "If asked whether you are a person, say you are an automated assistant, unofficial, and not INEC. "
    "If the language is unclear, ask once which language the user prefers, in English, Hausa and Igbo, use outcome B, and set language_confidence to low. "
    "A source with a blank last_verified date is unverified. If a high-stakes answer about a deadline, eligibility, a polling-unit location, or a legal right rests only on unverified sources, use outcome D, say the answer is not yet verified, and set needs_human_review to true. "
    "When you use the names INEC, PVC or CVR, explain each once in simple words: "
    "INEC is the government body that runs elections in Nigeria; "
    "PVC is your voter card, and you need it to vote; "
    "CVR is the process of registering to vote or updating your details. "
    "Do not invent a Hausa or Igbo explanation. If you are unsure of the wording in the user's language, use simple words and set needs_human_review to true."
)


def system_message(profile=None):
    raw = PROMPT_PATH.read_text(encoding="utf-8")
    match = FENCE.search(raw)
    if not match:
        raise RuntimeError("Master prompt block was not found.")
    text = match.group(1)
    text = text.replace("{app_name}", APP_NAME)
    text = text.replace("{accessibility_profile}", profile or "none given")
    text = text.replace("{icon_ids}", ", ".join(ICON_IDS))
    return text.rstrip() + "\n\n" + EXTRA_SENTENCES + "\n"
