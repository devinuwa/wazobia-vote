import json
import math
import re
from collections import Counter
from datetime import date
from pathlib import Path

from app.config import (
    DEADLINE_FILES,
    GLOSSARY_PATH,
    KNOWLEDGE_DIR,
    MIN_PASSAGE_SCORE,
    NIGERIA_FILES,
    STALENESS_DEADLINE_DAYS,
    STALENESS_GENERAL_DAYS,
    TOP_K,
    TOPICS_PATH,
)

HEADER_SPLIT = re.compile(r"\r?\n---\r?\n")
SECTION_START = re.compile(r"^(\d{1,3})\.(?:\s*[—–]|\s+\S)")
PART_LINE = re.compile(r"^(PART\s+[IVXLC]+)\b", re.I)
OPERATIVE_START = re.compile(r"^1\.\s*[—–]\(1\)")
SCHEDULE_LINE = re.compile(
    r"^(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)\s+SCHEDULE\b|^SCHEDULE TO\b",
    re.I,
)
TOPIC_BOOST = 20.0
FOLD = {
    "registered": "register",
    "registration": "register",
    "voter": "vote",
    "voters": "vote",
    "voting": "vote",
    "cards": "card",
}
STOP = {
    "a", "an", "the", "of", "to", "do", "i", "my", "how", "what", "who", "may",
    "can", "for", "on", "with", "is", "are", "ask", "help", "there", "be", "at",
    "or", "and", "in", "it", "you", "your", "was", "me", "should",
}
TOKEN = re.compile(r"[^\W\d_]+|\d+", re.UNICODE)
K1 = 1.5
B = 0.75


def load_glossary(path=GLOSSARY_PATH):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {key.casefold(): value for key, value in data.items()}


def prepare_query(question, rewriter=None, glossary=None):
    if rewriter is not None:
        try:
            rewritten = rewriter(question)
        except Exception:
            rewritten = ""
        if rewritten and len(rewritten.split()) <= 40 and "{" not in rewritten:
            return " ".join(rewritten.split())
    return glossary_query(question, glossary)


def glossary_query(question, glossary=None):
    glossary = glossary if glossary is not None else load_glossary()
    folded = question.casefold()
    extra = [value for key, value in glossary.items() if key in folded]
    parts = [question.strip(), *extra]
    return " ".join(part for part in parts if part)


def parse_file(path: Path):
    raw = path.read_text(encoding="utf-8")
    parts = HEADER_SPLIT.split(raw, maxsplit=1)
    header_text = parts[0]
    body = parts[1] if len(parts) > 1 else ""
    meta = {}
    for line in header_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    meta["body"] = body.strip("\n")
    meta["file_id"] = meta.get("id", path.stem)
    return meta


def _scope_and_limit(meta):
    file_id = meta["file_id"]
    scope = meta.get("scope", "").strip().lower()
    if scope not in {"nigeria", "concept"}:
        scope = "nigeria" if file_id in NIGERIA_FILES else "concept"
    limit = STALENESS_DEADLINE_DAYS if file_id in DEADLINE_FILES else STALENESS_GENERAL_DAYS
    return scope, limit


def _chunk_paragraphs(meta):
    scope, limit = _scope_and_limit(meta)
    paragraphs = [block.strip() for block in re.split(r"\n\s*\n", meta["body"]) if block.strip()]
    chunks = []
    for index, paragraph in enumerate(paragraphs, start=1):
        chunks.append(
            {
                "id": f"{meta['file_id']}-p{index}",
                "file_id": meta["file_id"],
                "title": meta.get("title", meta["file_id"]),
                "url": meta.get("url", ""),
                "last_verified": meta.get("last_verified", ""),
                "scope": scope,
                "staleness_limit_days": limit,
                "section": "",
                "text": paragraph,
            }
        )
    return chunks


def _passage(meta, scope, limit, chunk_id, title, section, text):
    return {
        "id": chunk_id,
        "file_id": meta["file_id"],
        "title": title,
        "url": meta.get("url", ""),
        "last_verified": meta.get("last_verified", ""),
        "scope": scope,
        "staleness_limit_days": limit,
        "section": section,
        "text": text,
    }


def _schedule_key(line):
    match = SCHEDULE_LINE.match(line.strip())
    if not match:
        return None
    name = match.group(1)
    if name:
        return name.upper()
    return "BILL"


def _schedule_title(base_title, key):
    if key == "BILL":
        return f"{base_title}, Schedule"
    return f"{base_title}, {key.title()} Schedule"


def _chunk_electoral_act(meta):
    scope, limit = _scope_and_limit(meta)
    lines = meta["body"].splitlines()
    start = 0
    for index, line in enumerate(lines):
        if OPERATIVE_START.match(line):
            start = index
            break
    schedule_at = len(lines)
    for index in range(start, len(lines)):
        if lines[index].strip() == "SCHEDULES":
            schedule_at = index
            break
    base_title = meta.get("title", "Electoral Act, 2026")
    file_id = meta["file_id"]
    chunks = []
    if start:
        preamble = "\n".join(lines[:start]).strip()
        if preamble:
            chunks.append(
                _passage(meta, scope, limit, f"{file_id}-preamble", f"{base_title}, preliminary pages", "", preamble)
            )
    part = ""
    for line in lines[:start]:
        part_match = PART_LINE.match(line.strip())
        if part_match:
            part = part_match.group(1).upper()
    current_number = 0
    current_lines = []
    section_part = part
    held_part_line = ""

    def flush_section():
        if current_number <= 0 or not any(line.strip() for line in current_lines):
            return
        title = f"{base_title}, section {current_number}"
        if section_part:
            title = f"{base_title}, {section_part}, section {current_number}"
        chunks.append(
            _passage(
                meta,
                scope,
                limit,
                f"{file_id}-s{current_number}",
                title,
                str(current_number),
                "\n".join(current_lines).strip(),
            )
        )

    for line in lines[start:schedule_at]:
        part_match = PART_LINE.match(line.strip())
        if part_match:
            part = part_match.group(1).upper()
            held_part_line = line
            continue
        section_match = SECTION_START.match(line)
        number = int(section_match.group(1)) if section_match else 0
        if section_match and number > current_number:
            flush_section()
            section_part = part
            current_number = number
            current_lines = [held_part_line, line] if held_part_line else [line]
            held_part_line = ""
        else:
            current_lines.append(line)
    flush_section()

    schedule_key = ""
    schedule_lines = []

    def flush_schedule():
        if not schedule_key or not any(line.strip() for line in schedule_lines):
            return
        slug = "bill" if schedule_key == "BILL" else schedule_key.lower()
        chunks.append(
            _passage(
                meta,
                scope,
                limit,
                f"{file_id}-sch-{slug}",
                _schedule_title(base_title, schedule_key),
                "",
                "\n".join(schedule_lines).strip(),
            )
        )

    for line in lines[schedule_at:]:
        key = _schedule_key(line)
        if key and key != schedule_key:
            flush_schedule()
            schedule_key = key
            schedule_lines = [line]
        else:
            if not schedule_key:
                schedule_key = "FIRST"
            schedule_lines.append(line)
    flush_schedule()
    return chunks


def load_chunks(directory=KNOWLEDGE_DIR):
    chunks = []
    for path in sorted(Path(directory).glob("src-*.txt")):
        meta = parse_file(path)
        if meta.get("placeholder", "").lower() == "yes":
            continue
        if meta["file_id"] == "src-001":
            chunks.extend(_chunk_electoral_act(meta))
        else:
            chunks.extend(_chunk_paragraphs(meta))
    return chunks


def tokenize(text):
    return [token.casefold() for token in TOKEN.findall(text)]


class Index:
    def __init__(self, chunks):
        self.chunks = chunks
        self.doc_tokens = [tokenize(chunk["text"] + " " + chunk["title"]) for chunk in chunks]
        self.doc_freq = Counter()
        for tokens in self.doc_tokens:
            self.doc_freq.update(set(tokens))
        self.avg_len = (
            sum(len(tokens) for tokens in self.doc_tokens) / len(self.doc_tokens)
            if self.doc_tokens
            else 0
        )
        self.n_docs = len(chunks)

    def score(self, query_tokens, doc_tokens):
        if not doc_tokens or not query_tokens:
            return 0.0
        counts = Counter(doc_tokens)
        doc_len = len(doc_tokens)
        total = 0.0
        for term in set(query_tokens):
            freq = counts.get(term, 0)
            if not freq:
                continue
            df = self.doc_freq.get(term, 0)
            idf = math.log(1 + (self.n_docs - df + 0.5) / (df + 0.5))
            denom = freq + K1 * (1 - B + B * doc_len / (self.avg_len or 1))
            total += idf * (freq * (K1 + 1)) / denom
        return total

    def scored(self, query):
        query_tokens = tokenize(query)
        return [
            (self.score(query_tokens, tokens), chunk)
            for chunk, tokens in zip(self.chunks, self.doc_tokens)
        ]


def xml_escape(value):
    return (
        str(value)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def render_sources(passages, question, today=None):
    today = today or date.today().isoformat()
    lines = [
        (
            f'<request_limits general_days="{STALENESS_GENERAL_DAYS}" '
            f'deadline_and_polling_unit_days="{STALENESS_DEADLINE_DAYS}" '
            f'today="{today}"/>'
        ),
        "<sources>",
    ]
    for passage in passages:
        lines.append(
            "  <source "
            f'id="{xml_escape(passage["id"])}" '
            f'title="{xml_escape(passage["title"])}" '
            f'url="{xml_escape(passage["url"])}" '
            f'last_verified="{xml_escape(passage["last_verified"])}" '
            f'staleness_limit_days="{passage["staleness_limit_days"]}" '
            f'scope="{xml_escape(passage["scope"])}">'
        )
        lines.append(f"    {xml_escape(passage['text'])}")
        lines.append("  </source>")
    lines.append("</sources>")
    lines.append(
        "<note>Sources with scope concept (ACE and International IDEA) support general concepts only. "
        "Nigerian deadlines, eligibility, polling units and legal rights may be taken only from sources with scope nigeria. "
        "A blank last_verified date means the source is unverified. "
        "A high-stakes answer about a deadline, eligibility, a polling-unit location, or a legal right that rests only on unverified sources must use outcome D.</note>"
    )
    lines.append(f"<question>{xml_escape(question)}</question>")
    return "\n".join(lines) + "\n"


_INDEX = None


def get_index():
    global _INDEX
    if _INDEX is None:
        _INDEX = Index(load_chunks())
    return _INDEX


def reset_index():
    global _INDEX
    _INDEX = None


def load_topics(path=TOPICS_PATH):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _triggers(block):
    phrases = []
    for language in ("en", "ha", "ig"):
        for phrase in block.get(language, []):
            text = phrase.casefold().strip()
            if len(text) >= 2:
                phrases.append(text)
    return phrases


def _phrase_in(phrase, text):
    folded = (text or "").casefold()
    if " " in phrase:
        return phrase in folded
    return phrase in tokenize(folded)


def _matching_topics(text, topics):
    found = []
    for topic in topics.get("topics", []):
        if any(_phrase_in(phrase, text) for phrase in _triggers(topic.get("triggers", {}))):
            found.append(topic)
    return found


def _phrase_hit(text, block):
    return any(_phrase_in(phrase, text) for phrase in _triggers(block or {}))


NO_SOURCE_PHRASES = (
    "are you inec",
    "real person",
    "which party",
    "who will win",
    "rigged",
    "prove the results",
)


def sources_withheld(question):
    folded = (question or "").casefold()
    return any(phrase in folded for phrase in NO_SOURCE_PHRASES)


def _section_number(chunk):
    section = str(chunk.get("section", ""))
    return int(section) if section.isdigit() else None


def _folded_tokens(text):
    return [FOLD.get(token, token) for token in tokenize(text)]


def _overlap(query, chunk):
    wanted = {token for token in _folded_tokens(query) if token not in STOP}
    if not wanted:
        return 0.0
    present = set(_folded_tokens(chunk["text"] + " " + chunk["title"]))
    return float(len(wanted & present))


def scored_search(question, query_text=None, top_k=TOP_K):
    query = query_text if query_text is not None else question
    topics = load_topics()
    matched = []
    seen = set()
    for topic in _matching_topics(question, topics) + _matching_topics(query, topics):
        if topic["id"] in seen:
            continue
        seen.add(topic["id"])
        matched.append(topic)
    section_boost = {}
    for topic in matched:
        for number in topic.get("sections", []):
            section_boost[number] = section_boost.get(number, 0.0) + TOPIC_BOOST
    civic = bool(section_boost) or _phrase_hit(question, topics.get("nigeria_required")) or _phrase_hit(query, topics.get("nigeria_required"))
    technology = _phrase_hit(question, topics.get("technology")) or _phrase_hit(query, topics.get("technology"))
    allow_concept = technology and not civic
    ranked = []
    for score, chunk in get_index().scored(query):
        number = _section_number(chunk)
        extra = 0.0
        if number is not None and number in section_boost:
            extra = section_boost[number] + _overlap(query or question, chunk)
        ranked.append((score + extra, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    if allow_concept:
        chosen = [(score, chunk) for score, chunk in ranked if chunk["scope"] == "concept" and score > 0]
        if not chosen:
            chosen = [(score, chunk) for score, chunk in ranked if score > 0]
    else:
        chosen = [(score, chunk) for score, chunk in ranked if chunk["scope"] == "nigeria"]
        if civic and len(chosen) < 3:
            chosen = ranked
    return chosen[:top_k]


def search(question, query_text=None, top_k=TOP_K):
    return [chunk for _, chunk in scored_search(question, query_text=query_text, top_k=top_k)]


_SECTION_ASK = re.compile(r"\bsection\s+(\d{1,3})\b", re.IGNORECASE)


def named_section_number(question):
    match = _SECTION_ASK.search(question or "")
    if not match:
        return ""
    return str(int(match.group(1)))


def pin_named_section(question, passages, top_k=TOP_K):
    number = named_section_number(question)
    if not number or sources_withheld(question):
        return passages
    pinned = None
    for chunk in get_index().chunks:
        if chunk["file_id"] == "src-001" and str(chunk.get("section")) == number:
            pinned = chunk
            break
    if pinned is None:
        return passages
    rest = [item for item in passages if item["id"] != pinned["id"]]
    return [pinned, *rest][:top_k]


def sources_for_prompt(question, query_text=None, top_k=TOP_K):
    ranked = scored_search(question, query_text=query_text, top_k=top_k)
    passages = []
    if ranked and not sources_withheld(question) and ranked[0][0] >= MIN_PASSAGE_SCORE:
        passages = [chunk for _, chunk in ranked]
    return pin_named_section(question, passages, top_k)
