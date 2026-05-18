"""Case 1: routine second trimester check. Expected tier: green."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from maitri.orchestrator import Orchestrator  # noqa: E402


PATIENT_NOTE = (
    "24 year old woman, first pregnancy, about 22 weeks. "
    "No headache, no bleeding, no swelling. Blood pressure 118 over 76. "
    "Hemoglobin 11.6. Lives in Saharsa town. Speaks Hindi. "
    "LMP 2025-12-14."
)

STRUCTURED = {
    "age_years": 24,
    "gravida": 1,
    "para": 0,
    "systolic_bp": 118,
    "diastolic_bp": 76,
    "hemoglobin_g_dl": 11.6,
    "severe_headache": False,
    "blurred_vision": False,
    "swelling_face_or_hands": False,
    "bleeding": False,
    "convulsions": False,
    "fever": False,
    "lmp_date": "2025-12-14",
    "language_preference": "hi",
    "district": "Saharsa",
}


def main() -> None:
    orch = Orchestrator()
    trace = orch.run(
        raw_text=PATIENT_NOTE,
        structured=STRUCTURED,
        case_id="case-1-happy",
    )
    out = {
        "case_id": trace.case_id,
        "final_tier": trace.final_assessment.tier.value if trace.final_assessment else None,
        "first_verdict_accepted": trace.first_verdict.accepted if trace.first_verdict else None,
        "facility": trace.referral.facility_name if trace.referral else None,
        "safety_rules": trace.safety_rule_ids,
        "chw_card": trace.deliverable.formatted.chw_card_en if trace.deliverable else None,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
