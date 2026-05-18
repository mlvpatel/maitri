"""Gestational age estimator from a last menstrual period date."""

from __future__ import annotations

from datetime import date


def compute_gestational_age(lmp_date_iso: str, today_iso: str | None = None) -> dict:
    """Return weeks plus days since LMP. Naegele's rule for due date."""

    lmp = date.fromisoformat(lmp_date_iso)
    today = date.fromisoformat(today_iso) if today_iso else date.today()
    days = (today - lmp).days
    weeks, rem_days = divmod(max(days, 0), 7)
    due = date(lmp.year + (lmp.month + 9 > 12), ((lmp.month + 9 - 1) % 12) + 1, min(lmp.day + 7, 28))
    return {
        "weeks": weeks,
        "days": rem_days,
        "estimated_due_date": due.isoformat(),
        "trimester": 1 if weeks < 13 else (2 if weeks < 28 else 3),
    }
