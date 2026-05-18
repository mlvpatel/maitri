"""Case 4: reduced fetal movement after 28 weeks. Expected tier: red, family voice strong."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from maitri.orchestrator import Orchestrator  # noqa: E402


PATIENT_NOTE = (
    "34 year old woman, fourth pregnancy, about 32 weeks. "
    "She reports she has not felt the baby move all day. "
    "Blood pressure 124 over 80. No bleeding. No headache. "
    "Speaks Hindi at home. LMP 2025-10-05."
)

STRUCTURED = {
    "age_years": 34,
    "gravida": 4,
    "para": 3,
    "systolic_bp": 124,
    "diastolic_bp": 80,
    "fetal_movements_normal": False,
    "severe_headache": False,
    "bleeding": False,
    "convulsions": False,
    "fever": False,
    "lmp_date": "2025-10-05",
    "language_preference": "hi",
    "district": "Saharsa",
}


def main() -> None:
    orch = Orchestrator()
    trace = orch.run(
        raw_text=PATIENT_NOTE,
        structured=STRUCTURED,
        case_id="case-4-fetal-movement",
    )
    out = {
        "case_id": trace.case_id,
        "final_tier": trace.final_assessment.tier.value if trace.final_assessment else None,
        "safety_rules": trace.safety_rule_ids,
        "facility": trace.referral.facility_name if trace.referral else None,
        "family_message_hi": trace.deliverable.formatted.family_message_hi if trace.deliverable else None,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
