"""Hero case. Forces the verifier rejection recovery loop end to end."""

from __future__ import annotations

import json

from maitri.orchestrator import Orchestrator


PATIENT_NOTE = (
    "32 year old woman, second pregnancy, gestational age about 30 weeks. "
    "Severe persistent headache for 24 hours, blurred vision, and swelling of the face. "
    "Blood pressure measured today at 168 over 112. No active bleeding. "
    "She is from Saharsa block, speaks Hindi at home. "
    "Last menstrual period was on 2025-10-22."
)

STRUCTURED = {
    "age_years": 32,
    "gravida": 2,
    "para": 1,
    "systolic_bp": 168,
    "diastolic_bp": 112,
    "severe_headache": True,
    "blurred_vision": True,
    "swelling_face_or_hands": True,
    "lmp_date": "2025-10-22",
    "language_preference": "hi",
    "district": "Saharsa",
}


def main() -> None:
    orch = Orchestrator()
    trace = orch.run(
        raw_text=PATIENT_NOTE,
        structured=STRUCTURED,
        case_id="hero-case-2",
        force_demo_hallucination=True,
    )
    out = {
        "case_id": trace.case_id,
        "initial_tier": trace.initial_assessment.tier.value if trace.initial_assessment else None,
        "initial_claims": [c.text for c in (trace.initial_assessment.claims if trace.initial_assessment else [])],
        "first_verdict_accepted": trace.first_verdict.accepted if trace.first_verdict else None,
        "first_verdict_unsupported_claims": trace.first_verdict.unsupported_claim_ids if trace.first_verdict else [],
        "optimizer_hint": trace.optimizer_hint,
        "second_verdict_accepted": trace.second_verdict.accepted if trace.second_verdict else None,
        "final_tier": trace.final_assessment.tier.value if trace.final_assessment else None,
        "final_referral_facility": trace.referral.facility_name if trace.referral else None,
        "final_referral_phone": trace.referral.facility_phone if trace.referral else None,
        "safety_rules_fired": trace.safety_rule_ids,
        "notes": trace.notes,
        "audit_calls": len(trace.audit_call_ids),
        "chw_card_en": trace.deliverable.formatted.chw_card_en if trace.deliverable else None,
        "mother_message_hi": trace.deliverable.formatted.mother_message_hi if trace.deliverable else None,
        "family_message_hi": trace.deliverable.formatted.family_message_hi if trace.deliverable else None,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
