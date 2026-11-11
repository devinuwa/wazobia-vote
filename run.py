import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.config import require_review_password

try:
    require_review_password()
except RuntimeError as exc:
    print(exc, file=sys.stderr)
    raise SystemExit(1)

uvicorn.run("app.main:app", host="127.0.0.1", port=8000)
