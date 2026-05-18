"""Hero case running entirely offline against Ollama hosted Gemma 4.

Prerequisites:
    1. Install Ollama from https://ollama.com
    2. Pull a Gemma 4 weight that runs on your hardware. Examples:
           ollama pull gemma3:27b
           ollama pull gemma3:4b
       Replace with gemma-4 tags when the upstream library publishes them.
    3. Ensure the Ollama daemon is running at http://localhost:11434
    4. Set MAITRI_PROVIDER=ollama in your environment

Run:
    MAITRI_PROVIDER=ollama python -m examples.case_2_offline_ollama
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

_SRC = Path(__file__).resolve().parents[1] / "src"
if _SRC.exists() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

os.environ["MAITRI_PROVIDER"] = "ollama"

from maitri.orchestrator import Orchestrator  # noqa: E402


PATIENT_NOTE = (
    "32 year old woman, second pregnancy, about 30 weeks. "
    "Severe persistent headache for 24 hours, blurred vision, swelling of the face. "
    "Blood pressure today 168 over 112. No active bleeding. "
    "Speaks Hindi. From Saharsa block. LMP 2025-10-22."
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
        case_id="offline-hero",
        force_demo_hallucination=True,
    )
    out = {
        "case_id": trace.case_id,
        "provider": "ollama",
        "final_tier": trace.final_assessment.tier.value if trace.final_assessment else None,
        "first_verdict_accepted": trace.first_verdict.accepted if trace.first_verdict else None,
        "first_verdict_unsupported": trace.first_verdict.unsupported_claim_ids if trace.first_verdict else [],
        "second_verdict_accepted": trace.second_verdict.accepted if trace.second_verdict else None,
        "facility": trace.referral.facility_name if trace.referral else None,
        "facility_phone": trace.referral.facility_phone if trace.referral else None,
        "audit_calls": len(trace.audit_call_ids),
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
