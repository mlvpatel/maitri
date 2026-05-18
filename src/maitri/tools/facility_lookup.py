"""Facility lookup over the committed Saharsa readiness snapshot."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from ..config import get_settings


@lru_cache(maxsize=1)
def _load_facilities() -> list[dict[str, Any]]:
    s = get_settings()
    path = s.repo_root / "data" / "facilities" / "saharsa_facility_readiness.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    return list(raw.get("facilities") or [])


def lookup_facility_readiness(
    capability_required: list[str] | None = None,
    *,
    open_only: bool = True,
    exclude_high_cost: bool = False,
    max_distance_km: float | None = None,
) -> list[dict[str, Any]]:
    """Return facilities matching the requested constraints, sorted by distance."""

    capability_required = list(capability_required or [])
    out: list[dict[str, Any]] = []
    for f in _load_facilities():
        if open_only and not f.get("open_now"):
            continue
        if exclude_high_cost and f.get("cost_level") == "private_high_cost":
            continue
        caps = f.get("capabilities") or {}
        if any(not caps.get(c) for c in capability_required):
            continue
        if max_distance_km is not None and (f.get("distance_km_from_demo_origin") or 0) > max_distance_km:
            continue
        out.append(f)
    out.sort(key=lambda x: x.get("distance_km_from_demo_origin", 999))
    return out
