"""Voucher eligibility for Indian maternal cash transfer schemes."""

from __future__ import annotations


def check_voucher_eligibility(
    age_years: int,
    para: int,
    bpl_category: bool | None = None,
    institutional_delivery: bool = True,
) -> dict:
    eligible = []
    if age_years >= 19 and institutional_delivery:
        eligible.append("JSY")
    if para == 0:
        eligible.append("PMMVY")
    if bpl_category:
        eligible.append("MAA")
    return {
        "eligible_schemes": eligible,
        "notes": "Final eligibility requires verification at the facility.",
    }
