"""Climate snapshot lookup for the demo district."""

from __future__ import annotations

import json
from functools import lru_cache

from ..config import get_settings


@lru_cache(maxsize=1)
def _load_climate() -> dict:
    s = get_settings()
    path = s.repo_root / "data" / "climate" / "saharsa_may2026_snapshot.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def query_climate_risk(geo: str = "Saharsa", week: int | None = None) -> dict:
    data = _load_climate()
    return {
        "geo": geo,
        "week": week,
        "snapshot": data.get("summary") or data or {"note": "no climate snapshot loaded"},
    }
