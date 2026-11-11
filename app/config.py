import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load_env_file():
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

KNOWLEDGE_DIR = Path(os.environ.get("KNOWLEDGE_DIR", ROOT / "knowledge"))
DATA_DIR = Path(os.environ.get("DATA_DIR", ROOT / "data"))
PHRASES_PATH = Path(os.environ.get("PHRASES_PATH", Path(__file__).parent / "phrases.json"))
GLOSSARY_PATH = Path(os.environ.get("GLOSSARY_PATH", Path(__file__).parent / "glossary.json"))
TOPICS_PATH = Path(os.environ.get("TOPICS_PATH", Path(__file__).parent / "topics.json"))

APP_NAME = os.environ.get("APP_NAME", "Wazobia vote")
MODEL_BASE_URL = os.environ.get("MODEL_BASE_URL", "https://api.openai.com/v1").rstrip("/")
MODEL_NAME = os.environ.get("MODEL_NAME", "gpt-4o-mini")
MODEL_API_KEY = os.environ.get("MODEL_API_KEY", "")

TOP_K = int(os.environ.get("TOP_K", "6"))
MIN_PASSAGE_SCORE = float(os.environ.get("MIN_PASSAGE_SCORE", "8"))
SOURCE_TOKEN_CAP = int(os.environ.get("SOURCE_TOKEN_CAP", "2500"))
STALENESS_GENERAL_DAYS = int(os.environ.get("STALENESS_GENERAL_DAYS", "90"))
STALENESS_DEADLINE_DAYS = int(os.environ.get("STALENESS_DEADLINE_DAYS", "30"))
QUESTION_LOG_RETENTION_HOURS = int(os.environ.get("QUESTION_LOG_RETENTION_HOURS", "24"))
REVIEW_RETENTION_DAYS = int(os.environ.get("REVIEW_RETENTION_DAYS", "30"))


def require_review_password():
    value = os.environ.get("REVIEW_PASSWORD", "").strip()
    if not value:
        raise RuntimeError("REVIEW_PASSWORD is unset. Refusing to start.")
    return value

ICON_IDS = (
    "id-card",
    "location-pin",
    "calendar",
    "clock",
    "phone",
    "person-assist",
    "ballot-box",
    "check",
    "warning",
    "question",
)

NIGERIA_FILES = {"src-001", "src-003", "src-004", "src-005"}
DEADLINE_FILES = {"src-001", "src-003", "src-004"}

PROMPT_PATH = ROOT / "Voter-Assistant-Prompt-Pack" / "markdown" / "01-master-prompt.md"
SCHEMA_PATH = Path(__file__).parent / "output_schema.json"
