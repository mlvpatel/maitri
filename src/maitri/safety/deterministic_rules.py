"""Deterministic safety rules. Pure Python. No LLM.

A rule may only promote a tier upward toward Red, never downward toward Green.
This ensures that the deterministic block can never override an LLM call into
a less safe outcome.

Rules are derived from WHO recommendations on antenatal care for a positive
pregnancy experience (2016), the Indian Ministry of Health RMNCH+A guidelines,
and the FIGO position on the management of pre eclampsia.
"""

from __future__ import annotations

from dataclasses import dataclass

from ..schemas import PatientSnapshot, RiskTier


_TIER_ORDER = {RiskTier.GREEN: 0, RiskTier.AMBER: 1, RiskTier.RED: 2}


@dataclass(frozen=True)
class SafetyRuleResult:
    promoted_tier: RiskTier
    fired_rule_ids: list[str]
    reasons: list[str]

    @property
    def fired(self) -> bool:
        return len(self.fired_rule_ids) > 0


def _hi(a: RiskTier, b: RiskTier) -> RiskTier:
    return a if _TIER_ORDER[a] >= _TIER_ORDER[b] else b


def _bp_severe(p: PatientSnapshot) -> bool:
    return (
        (p.systolic_bp is not None and p.systolic_bp >= 160)
        or (p.diastolic_bp is not None and p.diastolic_bp >= 110)
    )


def _bp_high(p: PatientSnapshot) -> bool:
    return (
        (p.systolic_bp is not None and p.systolic_bp >= 140)
        or (p.diastolic_bp is not None and p.diastolic_bp >= 90)
    )


def _severe_anemia(p: PatientSnapshot) -> bool:
    return p.hemoglobin_g_dl is not None and p.hemoglobin_g_dl < 7.0


def _moderate_anemia(p: PatientSnapshot) -> bool:
    return p.hemoglobin_g_dl is not None and 7.0 <= p.hemoglobin_g_dl < 10.0


def _high_fever(p: PatientSnapshot) -> bool:
    return p.temperature_c is not None and p.temperature_c >= 38.5


def _adolescent_or_elderly(p: PatientSnapshot) -> bool:
    return p.age_years < 18 or p.age_years >= 35


DEFAULT_RULES: list[dict] = [
    {"id": "severe-hypertension", "tier": RiskTier.RED, "check": _bp_severe,
     "reason": "Severe hypertension at or above 160 over 110 indicates risk of eclampsia"},
    {"id": "severe-anemia", "tier": RiskTier.RED, "check": _severe_anemia,
     "reason": "Hemoglobin below 7 g per dL indicates severe anemia requiring transfusion capable facility"},
    {"id": "active-bleeding", "tier": RiskTier.RED, "check": lambda p: bool(p.bleeding),
     "reason": "Active antepartum bleeding is a Red flag for placental complication"},
    {"id": "convulsions", "tier": RiskTier.RED, "check": lambda p: bool(p.convulsions),
     "reason": "Convulsions during pregnancy are a Red flag for eclampsia"},
    {"id": "reduced-fetal-movement", "tier": RiskTier.RED,
     "check": lambda p: p.fetal_movements_normal is False,
     "reason": "Reduced fetal movement after 28 weeks requires immediate evaluation"},
    {"id": "preeclampsia-symptoms", "tier": RiskTier.RED,
     "check": lambda p: (
         bool(p.severe_headache) and bool(p.blurred_vision)
     ) or (
         bool(p.severe_headache) and bool(p.swelling_face_or_hands)
     ),
     "reason": "Headache with vision changes or facial edema suggests pre eclampsia"},
    {"id": "high-fever", "tier": RiskTier.AMBER, "check": _high_fever,
     "reason": "Temperature at or above 38.5 C suggests sepsis risk in pregnancy"},
    {"id": "mild-hypertension", "tier": RiskTier.AMBER, "check": _bp_high,
     "reason": "Blood pressure at or above 140 over 90 is gestational hypertension"},
    {"id": "moderate-anemia", "tier": RiskTier.AMBER, "check": _moderate_anemia,
     "reason": "Hemoglobin between 7 and 10 g per dL is moderate anemia"},
    {"id": "age-extremes", "tier": RiskTier.AMBER, "check": _adolescent_or_elderly,
     "reason": "Maternal age under 18 or 35 and above raises baseline risk"},
    {"id": "reduced-urine", "tier": RiskTier.AMBER, "check": lambda p: bool(p.reduced_urine),
     "reason": "Reduced urine output is a sign of dehydration or renal compromise"},
]


def evaluate_safety_rules(
    patient: PatientSnapshot,
    current_tier: RiskTier,
    rules: list[dict] | None = None,
) -> SafetyRuleResult:
    rules = rules if rules is not None else DEFAULT_RULES
    promoted = current_tier
    fired_ids: list[str] = []
    reasons: list[str] = []
    for rule in rules:
        try:
            if rule["check"](patient):
                promoted = _hi(promoted, rule["tier"])
                fired_ids.append(rule["id"])
                reasons.append(rule["reason"])
        except Exception:  # noqa: BLE001 -- a single bad rule must not break the block
            continue
    return SafetyRuleResult(promoted_tier=promoted, fired_rule_ids=fired_ids, reasons=reasons)
