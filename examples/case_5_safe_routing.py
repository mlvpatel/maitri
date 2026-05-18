"""Case 5: red tier with the closer facility incapable. The referral agent must
skip the closer primary health centre and pick a maternal emergency capable target.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from maitri.orchestrator import Orchestrator  # noqa: E402
from maitri.schemas import RiskTier  # noqa: E402


PATIENT_NOTE = (
    "29 year old woman, third pregnancy, about 38 weeks. "
    "Active bleeding from the genital tract started today. "
    "Blood pressure 130 over 86, hemoglobin 9.1. "
    "Speaks Hindi. LMP 2025-08-22."
)

STRUCTURED = {
    "age_years": 29,
    "gravida": 3,
    "para": 2,
    "systolic_bp": 130,
    "diastolic_bp": 86,
    "hemoglobin_g_dl": 9.1,
    "bleeding": True,
    "severe_headache": False,
    "convulsions": False,
    "fever": False,
    "lmp_date": "2025-08-22",
    "language_preference": "hi",
    "district": "Saharsa",
}


def main() -> None:
    orch = Orchestrator()
    trace = orch.run(
        raw_text=PATIENT_NOTE,
        structured=STRUCTURED,
        case_id="case-5-safe-routing",
    )
    chosen = trace.referral.facility_name if trace.referral else None
    out = {
        "case_id": trace.case_id,
        "final_tier": trace.final_assessment.tier.value if trace.final_assessment else None,
        "safety_rules": trace.safety_rule_ids,
        "facility_chosen": chosen,
        "facility_distance_km": trace.referral.facility_distance_km if trace.referral else None,
        "facility_capabilities": trace.referral.facility_capabilities if trace.referral else None,
        "should_not_be": "Sahuriya PHC (closer but no maternal emergency capability)",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    # A simple invariant for the demo: never the incapable PHC for a Red case.
    if trace.final_assessment and trace.final_assessment.tier == RiskTier.RED:
        assert chosen != "Sahuriya PHC", "Referral agent picked the incapable closer facility"
        print("INVARIANT OK: incapable closer facility was not selected for a Red case")


if __name__ == "__main__":
    main()
