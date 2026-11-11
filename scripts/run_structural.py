import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tests.run_cases import structural

raise SystemExit(0 if structural() else 1)
