"""Smoke level tests on the orchestrator that do not require a live model.

The full pipeline tests live under tests/integration and are opt in via the
MAITRI_LIVE_TESTS environment variable to keep CI free of LLM cost.
"""

from __future__ import annotations

import pytest

from maitri.orchestrator import CaseTrace, Orchestrator
from maitri.safety import evaluate_safety_rules
from maitri.schemas import PatientSnapshot, RiskTier


def test_case_trace_default_phase():
    t = CaseTrace(case_id="x")
    assert t.phase == "init"
    assert t.timings_ms == {}


def test_orchestrator_constructs_without_live_calls():
    orch = Orchestrator()
    assert orch is not None


def test_safety_rules_promote_block_invariant():
    """A red tier input must always remain red or higher after the safety block."""
    snapshot = PatientSnapshot(case_id="t", age_years=24, systolic_bp=100, diastolic_bp=60)
    out = evaluate_safety_rules(snapshot, RiskTier.RED)
    assert out.promoted_tier == RiskTier.RED


def test_safety_rules_fire_on_bleeding_for_green_input():
    snapshot = PatientSnapshot(case_id="t", age_years=24, bleeding=True)
    out = evaluate_safety_rules(snapshot, RiskTier.GREEN)
    assert out.promoted_tier == RiskTier.RED
    assert "active-bleeding" in out.fired_rule_ids


@pytest.mark.parametrize(
    "systolic,diastolic,expected",
    [
        (110, 70, RiskTier.GREEN),
        (145, 92, RiskTier.AMBER),
        (170, 115, RiskTier.RED),
    ],
)
def test_bp_tier_ladder(systolic, diastolic, expected):
    snapshot = PatientSnapshot(
        case_id="t", age_years=28, systolic_bp=systolic, diastolic_bp=diastolic,
    )
    out = evaluate_safety_rules(snapshot, RiskTier.GREEN)
    assert out.promoted_tier == expected
