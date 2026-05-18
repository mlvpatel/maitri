"""Transport cost estimate over road distance with a monsoon multiplier."""

from __future__ import annotations

from datetime import date


def estimate_transport_cost(distance_km: float, when_iso: str | None = None) -> dict:
    rate_inr_per_km = 18.0
    monsoon = False
    if when_iso:
        m = date.fromisoformat(when_iso).month
        monsoon = m in (6, 7, 8, 9)
    multiplier = 1.4 if monsoon else 1.0
    estimate = round(distance_km * rate_inr_per_km * multiplier, 2)
    return {
        "distance_km": distance_km,
        "estimated_cost_inr": estimate,
        "monsoon_surcharge_applied": monsoon,
        "notes": "Estimate for private auto. Ambulance is free under public scheme.",
    }
