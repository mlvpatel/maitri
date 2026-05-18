"""Runtime configuration loaded from environment."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


_REPO_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_REPO_ROOT / ".env", override=False)


@dataclass(frozen=True)
class Settings:
    hf_token: str
    reasoning_model: str
    light_model: str
    reasoning_fallback: str
    light_fallback: str
    router_url: str
    audit_sqlite: Path
    audit_jsonl: Path
    repo_root: Path

    @classmethod
    def from_env(cls) -> "Settings":
        token = os.getenv("HF_TOKEN", "").strip()
        if not token:
            raise RuntimeError("HF_TOKEN is not set in the environment")
        return cls(
            hf_token=token,
            reasoning_model=os.getenv("GEMMA_REASONING_MODEL_ID", "google/gemma-4-31B-it"),
            light_model=os.getenv("GEMMA_LIGHT_MODEL_ID", "google/gemma-4-26B-A4B-it"),
            reasoning_fallback=os.getenv(
                "GEMMA_REASONING_FALLBACK_MODEL_ID", "google/gemma-4-31B-it-assistant"
            ),
            light_fallback=os.getenv("GEMMA_LIGHT_FALLBACK_MODEL_ID", "google/gemma-4-31B-it"),
            router_url=os.getenv(
                "HF_ROUTER_URL", "https://router.huggingface.co/v1/chat/completions"
            ),
            audit_sqlite=_REPO_ROOT / os.getenv("SQLITE_AUDIT_PATH", "audit.sqlite"),
            audit_jsonl=_REPO_ROOT / os.getenv("JSONL_AUDIT_PATH", "audit.jsonl"),
            repo_root=_REPO_ROOT,
        )


def get_settings() -> Settings:
    return Settings.from_env()
