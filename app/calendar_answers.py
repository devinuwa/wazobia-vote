import json
import os
from pathlib import Path

from app.bank import citations_for
from app.replies import outcome_d
from app.textnorm import normalise

_DEFAULT = Path(__file__).parent / "calendar.json"
_DATE_CUES = (
    "when is",
    "what date",
    "which date",
    "on what date",
    "election date",
    "deadline",
    "timetable",
    "notice of election",
)


def calendar_path():
    return Path(os.environ.get("CALENDAR_PATH", _DEFAULT))


def load_calendar():
    path = calendar_path()
    if not path.exists():
        return {"dates": []}
    return json.loads(path.read_text(encoding="utf-8"))


def is_date_question(question):
    folded = normalise(question)
    return any(cue in folded for cue in _DATE_CUES)


def filled_dates(data=None):
    rows = (data if data is not None else load_calendar()).get("dates") or []
    return [row for row in rows if str(row.get("date") or "").strip()]


def calendar_reply(question, language=None):
    rows = filled_dates()
    if not rows:
        return outcome_d(
            language,
            "No confirmed date is in the calendar.",
            "The date is not confirmed.",
            "The date is not confirmed.",
        )
    lines = []
    source_ids = []
    for row in rows:
        event = str(row.get("event") or "").strip() or "Election date"
        date = str(row.get("date") or "").strip()
        source_id = str(row.get("source_id") or "").strip()
        page = str(row.get("page") or "").strip()
        line = f"{event}: {date}."
        if source_id:
            line += f" Source {source_id}."
            source_ids.append(source_id)
        if page:
            line += f" Page {page}."
        lines.append(line)
    return outcome_d(
        language,
        "The calendar date is shown, and the source has no last checked date.",
        "The date is written on the screen.",
        " ".join(lines),
        citations_for(source_ids),
    )
