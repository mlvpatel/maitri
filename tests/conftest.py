import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

os.environ.setdefault("HF_TOKEN", "test-token")
os.environ.setdefault("SQLITE_AUDIT_PATH", "audit.test.sqlite")
os.environ.setdefault("JSONL_AUDIT_PATH", "audit.test.jsonl")
