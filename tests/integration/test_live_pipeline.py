"""Live end to end integration tests.

These tests call Gemma 4 via the configured provider and therefore cost real
inference. They are skipped by default and only run when MAITRI_LIVE_TESTS is
set to a truthy value.

Each case asserts an invariant a judge can verify: the hero verifier rejection,
the green tier on a routine ANC, the safe routing skip on a closed or incapable
facility.
"""

from __future__ import annotations

import os

import pytest

from maitri.orchestrator import Orchestrator
from maitri.schemas import RiskTier


pytestmark = pytest.mark.skipif(
    os.environ.get("MAITRI_LIVE_TESTS", "").lower() not in {"1", "true", "yes"},
    reason="set MAITRI_LIVE_TESTS=1 to enable live integration tests",
)


def test_hero_loop_verifier_catches_planted_hallucination():
    orch = Orchestrator()
    trace = orch.run(
        raw_text=(
            "32 year old woman, second pregnancy, about 30 weeks. "
            "Severe headache, blurred vision, facial swelling. BP 168 over 112."
        ),
        structured={
            "age_years": 32, "gravida": 2, "para": 1,
            "systolic_bp": 168, "diastolic_bp": 112,
            "severe_headache": True, "blurred_vision": True, "swelling_face_or_hands": True,
            "lmp_date": "2025-10-22", "language_preference": "hi", "district": "Saharsa",
        },
        force_demo_hallucination=True,
    )
    assert trace.first_verdict is not None
    assert trace.first_verdict.accepted is False
    assert trace.final_assessment.tier == RiskTier.RED


def test_routine_case_stays_green_or_amber():
    orch = Orchestrator()
    trace = orch.run(
        raw_text="24 year old, first pregnancy, 22 weeks, BP 118 over 76, no concerns.",
        structured={
            "age_years": 24, "gravida": 1, "para": 0,
            "systolic_bp": 118, "diastolic_bp": 76, "hemoglobin_g_dl": 11.6,
            "lmp_date": "2025-12-14", "language_preference": "hi", "district": "Saharsa",
        },
    )
    assert trace.final_assessment.tier in (RiskTier.GREEN, RiskTier.AMBER)


def test_red_case_does_not_route_to_incapable_phc():
    orch = Orchestrator()
    trace = orch.run(
        raw_text="29 year old, gravida 3, para 2, active bleeding at 38 weeks.",
        structured={
            "age_years": 29, "gravida": 3, "para": 2,
            "systolic_bp": 130, "diastolic_bp": 86, "hemoglobin_g_dl": 9.1,
            "bleeding": True,
            "lmp_date": "2025-08-22", "language_preference": "hi", "district": "Saharsa",
        },
    )
    assert trace.final_assessment.tier == RiskTier.RED
    assert trace.referral is not None
    assert trace.referral.facility_name != "Sahuriya PHC"
