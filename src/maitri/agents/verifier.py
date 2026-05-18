"""Independent verifier. Checks every claim against the evidence pack."""

from __future__ import annotations

import json

from ..gemma_client import GemmaClient
from ..schemas import EvidencePack, RiskAssessment, VerificationVerdict
from ._json import extract_json


_SYSTEM = (
    "You are an independent verifier. You did not author the risk assessment. "
    "Your only task is to check whether each claim in the assessment is supported "
    "by the cited evidence chunks. A claim is supported only when an evidence chunk "
    "directly entails it. Numerical specifics like doses, thresholds, and timing must "
    "appear verbatim or be unambiguously implied in the evidence. If any claim is "
    "unsupported, the verdict must be accepted=false. Return JSON only with fields: "
    "accepted (boolean), unsupported_claim_ids (array of strings), rationale (short), "
    "suggested_fix (short instruction for the specialist on how to repair the draft)."
)


def _format_assessment(a: RiskAssessment) -> str:
    return json.dumps(
        {
            "tier": a.tier.value,
            "headline": a.headline,
            "rationale": a.rationale,
            "claims": [c.model_dump() for c in a.claims],
            "recommended_actions": a.recommended_actions,
        },
        ensure_ascii=False,
        indent=2,
    )


def _format_evidence(pack: EvidencePack) -> str:
    return "\n\n".join(f"[{c.chunk_id}] {c.title}\n{c.text}" for c in pack.chunks)


def run_verifier(
    assessment: RiskAssessment,
    evidence: EvidencePack,
    *,
    client: GemmaClient,
) -> VerificationVerdict:
    user_payload = (
        f"Risk assessment to verify:\n{_format_assessment(assessment)}\n\n"
        f"Evidence pack the specialist was given:\n{_format_evidence(evidence)}"
    )
    resp = client.chat(
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user_payload},
        ],
        agent="verifier",
        temperature=0.0,
        max_tokens=700,
        response_format={"type": "json_object"},
    )
    obj = extract_json(resp.content)
    return VerificationVerdict(
        case_id=assessment.case_id,
        accepted=bool(obj.get("accepted", False)),
        unsupported_claim_ids=[str(x) for x in obj.get("unsupported_claim_ids", [])],
        rationale=str(obj.get("rationale", "")),
        suggested_fix=str(obj.get("suggested_fix", "")),
    )
