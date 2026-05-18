"""Case 3: moderate anemia in mid pregnancy. Expected tier: amber."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from maitri.orchestrator import Orchestrator  # noqa: E402


PATIENT_NOTE = (
    "28 year old woman, third pregnancy, about 26 weeks. "
    "Feels weak and tired. Pale tongue and palms. "
    "Blood pressure 122 over 78. Hemoglobin reading 8.2. "
    "No bleeding, no headache. Speaks Hindi. LMP 2025-11-15."
)

STRUCTURED = {
    "age_years": 28,
    "gravida": 3,
    "para": 2,
    "systolic_bp": 122,
    "diastolic_bp": 78,
    "hemoglobin_g_dl": 8.2,
    "severe_headache": False,
    "bleeding": False,
    "convulsions": False,
    "fever": False,
    "lmp_date": "2025-11-15",
    "language_preference": "hi",
    "district": "Saharsa",
}


def main() -> None:
    orch = Orchestrator()
    trace = orch.run(
        raw_text=PATIENT_NOTE,
        structured=STRUCTURED,
        case_id="case-3-anemia",
    )
    out = {
        "case_id": trace.case_id,
        "final_tier": trace.final_assessment.tier.value if trace.final_assessment else None,
        "first_verdict_accepted": trace.first_verdict.accepted if trace.first_verdict else None,
        "safety_rules": trace.safety_rule_ids,
        "facility": trace.referral.facility_name if trace.referral else None,
        "voucher_eligibility": trace.referral.voucher_eligibility if trace.referral else None,
        "mother_message_hi": trace.deliverable.formatted.mother_message_hi if trace.deliverable else None,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
