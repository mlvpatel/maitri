"""Optimizer. Turns a verifier verdict into a precise hint for the specialist rerun."""

from __future__ import annotations

from ..gemma_client import GemmaClient
from ..schemas import RiskAssessment, VerificationVerdict
from ..config import get_settings


_SYSTEM = (
    "You are a prompt optimizer. You receive a specialist draft that was rejected "
    "by the independent verifier. Produce ONE short paragraph of plain prose that "
    "tells the specialist exactly what to drop or rephrase on the next attempt. "
    "Do not include code, JSON, or examples. Maximum 80 words."
)


def run_optimizer(
    assessment: RiskAssessment,
    verdict: VerificationVerdict,
    *,
    client: GemmaClient,
) -> str:
    user_payload = (
        f"Verifier rationale: {verdict.rationale}\n"
        f"Unsupported claim ids: {verdict.unsupported_claim_ids}\n"
        f"Verifier suggested fix: {verdict.suggested_fix}\n"
        f"Specialist draft headline: {assessment.headline}\n"
        f"Specialist claims: {[c.text for c in assessment.claims]}"
    )
    resp = client.chat(
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user_payload},
        ],
        model=get_settings().light_model,
        agent="optimizer",
        temperature=0.2,
        max_tokens=200,
    )
    return resp.content.strip()
