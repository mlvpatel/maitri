from maitri.safety import evaluate_safety_rules
from maitri.schemas import PatientSnapshot, RiskTier


def _base(**kw):
    kw.setdefault("age_years", 24)
    return PatientSnapshot(case_id="t", **kw)


def test_severe_bp_promotes_to_red():
    r = evaluate_safety_rules(_base(systolic_bp=170, diastolic_bp=115), RiskTier.GREEN)
    assert r.promoted_tier == RiskTier.RED
    assert "severe-hypertension" in r.fired_rule_ids


def test_active_bleeding_promotes_to_red():
    r = evaluate_safety_rules(_base(bleeding=True), RiskTier.AMBER)
    assert r.promoted_tier == RiskTier.RED


def test_high_temperature_promotes_to_amber():
    r = evaluate_safety_rules(_base(temperature_c=39.0), RiskTier.GREEN)
    assert r.promoted_tier == RiskTier.AMBER
    assert "high-fever" in r.fired_rule_ids


def test_block_can_never_demote():
    r = evaluate_safety_rules(_base(systolic_bp=110, diastolic_bp=70), RiskTier.RED)
    assert r.promoted_tier == RiskTier.RED


def test_mild_hypertension_promotes_to_amber():
    r = evaluate_safety_rules(_base(systolic_bp=145, diastolic_bp=92), RiskTier.GREEN)
    assert r.promoted_tier == RiskTier.AMBER


def test_severe_anemia_promotes_to_red():
    r = evaluate_safety_rules(_base(hemoglobin_g_dl=6.4), RiskTier.GREEN)
    assert r.promoted_tier == RiskTier.RED


def test_moderate_anemia_promotes_to_amber():
    r = evaluate_safety_rules(_base(hemoglobin_g_dl=8.5), RiskTier.GREEN)
    assert r.promoted_tier == RiskTier.AMBER


def test_preeclampsia_symptom_cluster():
    r = evaluate_safety_rules(
        _base(severe_headache=True, blurred_vision=True), RiskTier.GREEN
    )
    assert r.promoted_tier == RiskTier.RED


def test_no_signals_stays_at_current_tier():
    r = evaluate_safety_rules(_base(age_years=25, systolic_bp=115, diastolic_bp=72), RiskTier.GREEN)
    assert r.promoted_tier == RiskTier.GREEN
    assert not r.fired_rule_ids
