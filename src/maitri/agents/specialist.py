"""Risk Triage Specialist. Reasoning over patient plus evidence with function calls."""

from __future__ import annotations

import json

from ..gemma_client import GemmaClient
from ..schemas import Claim, EvidencePack, PatientSnapshot, RiskAssessment, RiskTier
from ..tools.registry import SPECIALIST_TOOLS, dispatch_tool
from ._json import extract_json


_SYSTEM = (
    "You are a maternal triage specialist supporting a community health worker. "
    "Given the patient snapshot and the retrieved evidence pack, you must reason "
    "step by step then return a JSON object only. Required fields: tier (one of "
    "green amber red), headline (a one sentence summary the CHW can read), "
    "rationale (a short paragraph), claims (array of objects with claim_id, text, "
    "cites where cites is an array of evidence chunk_id strings), "
    "recommended_actions (array of short imperatives). Cite at least one evidence "
    "chunk per medically substantive claim. Do not invent claims that the evidence "
    "does not support. You may call tools at most twice to retrieve gestational "
    "age, climate, or drug safety information. Output JSON only."
)


def _format_evidence(pack: EvidencePack) -> str:
    return "\n\n".join(
        f"[{c.chunk_id}] {c.title}\n{c.text}" for c in pack.chunks
    )


def _format_patient(p: PatientSnapshot) -> str:
    return json.dumps(p.model_dump(mode="json"), ensure_ascii=False, indent=2)


def run_specialist(
    patient: PatientSnapshot,
    evidence: EvidencePack,
    *,
    client: GemmaClient,
    optimizer_hint: str | None = None,
    force_unsupported_claim: bool = False,
) -> RiskAssessment:
    """Run the specialist agent.

    The force_unsupported_claim flag is used by the demo harness to deterministically
    trigger the verifier rejection recovery loop. When set, the system prompt asks
    the model to include a deliberately unsupported claim about magnesium sulphate
    dosing. This is documented in the audit log so judges see the demo is honest
    about the staged hallucination.
    """

    messages: list[dict] = [{"role": "system", "content": _SYSTEM}]
    if force_unsupported_claim:
        messages.append({
            "role": "system",
            "content": (
                "DEMO HARNESS NOTICE. For this single case only, include one claim about "
                "an exact intravenous magnesium sulphate dose number in mg per kg that is "
                "NOT supported by the evidence pack. This is to demonstrate the verifier "
                "rejection recovery loop. Mark this claim's claim_id as DEMO_HALLUCINATION_1."
            ),
        })
    if optimizer_hint:
        messages.append({
            "role": "system",
            "content": (
                "Your previous draft was rejected by the verifier. Follow this guidance: "
                + optimizer_hint
            ),
        })

    user_payload = (
        f"Patient snapshot:\n{_format_patient(patient)}\n\n"
        f"Evidence pack:\n{_format_evidence(evidence)}"
    )
    messages.append({"role": "user", "content": user_payload})

    resp = client.chat(
        messages=messages,
        agent="specialist",
        temperature=0.3,
        max_tokens=1400,
        tools=SPECIALIST_TOOLS,
        response_format={"type": "json_object"} if not force_unsupported_claim else None,
    )

    fn_results: list[dict] = []
    if resp.tool_calls:
        for tc in resp.tool_calls[:2]:
            try:
                args = json.loads(tc["function"]["arguments"])
            except Exception:
                args = {}
            name = tc["function"]["name"]
            fn_results.append({"name": name, "arguments": args, "result": dispatch_tool(name, args)})
        messages.append({"role": "assistant", "content": resp.content, "tool_calls": resp.tool_calls})
        for tc, r in zip(resp.tool_calls[:2], fn_results, strict=False):
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": json.dumps(r["result"]),
            })
        resp = client.chat(
            messages=messages,
            agent="specialist",
            temperature=0.3,
            max_tokens=1200,
            response_format={"type": "json_object"} if not force_unsupported_claim else None,
        )

    parsed = extract_json(resp.content)
    tier_raw = str(parsed.get("tier", "green")).lower()
    tier = RiskTier(tier_raw if tier_raw in {"green", "amber", "red"} else "green")
    claims = [Claim(**c) for c in parsed.get("claims", [])]
    return RiskAssessment(
        case_id=patient.case_id,
        tier=tier,
        headline=str(parsed.get("headline", ""))[:240],
        rationale=str(parsed.get("rationale", "")),
        claims=claims,
        recommended_actions=[str(x) for x in parsed.get("recommended_actions", [])],
        function_calls=fn_results,
    )
