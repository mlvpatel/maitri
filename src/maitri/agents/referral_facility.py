"""Referral and Facility agent. Selects a safe, open, capable facility."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from ..gemma_client import GemmaClient
from ..schemas import PatientSnapshot, ReferralPacket, RiskAssessment, RiskTier
from ..tools.facility_lookup import lookup_facility_readiness
from ..tools.registry import REFERRAL_TOOLS, dispatch_tool
from ._json import extract_json


_SYSTEM = (
    "You are a referral and facility selection agent. Given the patient and the risk "
    "assessment, you must choose a single safe destination. The chosen facility must "
    "be open, must have the maternal care capabilities the case requires, and should "
    "favour shorter distance and lower cost when capability allows. Use the tools to "
    "list facilities, estimate transport cost, and check voucher eligibility. Return "
    "JSON only with fields: facility_name, facility_distance_km, facility_phone, "
    "facility_capabilities (array of strings), transport_advice (one sentence), "
    "cost_advice (one sentence), voucher_eligibility (one sentence)."
)


def _required_caps(tier: RiskTier) -> list[str]:
    if tier == RiskTier.RED:
        return ["maternal_emergency", "obstetric_surgery", "blood_bank"]
    if tier == RiskTier.AMBER:
        return ["maternal_emergency", "blood_pressure_check"]
    return ["blood_pressure_check"]


def _sign(packet: dict[str, Any]) -> str:
    payload = json.dumps(packet, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:32]


def run_referral_facility(
    patient: PatientSnapshot,
    assessment: RiskAssessment,
    *,
    client: GemmaClient,
) -> ReferralPacket:
    caps = _required_caps(assessment.tier)
    shortlist = lookup_facility_readiness(capability_required=caps, open_only=True)

    user_payload = (
        f"Patient age={patient.age_years} para={patient.para} district={patient.district}.\n"
        f"Risk tier: {assessment.tier.value}\n"
        f"Required capabilities: {caps}\n"
        f"Shortlist of capable open facilities, nearest first: "
        f"{json.dumps([{ 'id': f['facility_id'], 'name': f['facility_name'], 'distance_km': f['distance_km_from_demo_origin'], 'cost': f['cost_level'], 'phone': f['contact'].get('ambulance_phone') or f['contact'].get('labour_room_phone'), 'capabilities': [c for c, v in f['capabilities'].items() if v]} for f in shortlist], ensure_ascii=False)}\n"
        "Pick one. Then use tools to estimate transport cost and check voucher eligibility."
    )

    messages: list[dict] = [
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": user_payload},
    ]
    resp = client.chat(
        messages=messages,
        agent="referral_facility",
        temperature=0.2,
        max_tokens=900,
        tools=REFERRAL_TOOLS,
        response_format={"type": "json_object"},
    )

    fn_results: list[dict] = []
    if resp.tool_calls:
        for tc in resp.tool_calls[:3]:
            try:
                args = json.loads(tc["function"]["arguments"])
            except Exception:
                args = {}
            name = tc["function"]["name"]
            fn_results.append({"name": name, "arguments": args, "result": dispatch_tool(name, args)})
        messages.append({"role": "assistant", "content": resp.content, "tool_calls": resp.tool_calls})
        for tc, r in zip(resp.tool_calls[:3], fn_results, strict=False):
            messages.append({
                "role": "tool",
                "tool_call_id": tc.get("id", ""),
                "content": json.dumps(r["result"]),
            })
        resp = client.chat(
            messages=messages,
            agent="referral_facility",
            temperature=0.2,
            max_tokens=900,
            response_format={"type": "json_object"},
        )

    parsed = extract_json(resp.content)
    facility_name = str(parsed.get("facility_name", shortlist[0]["facility_name"] if shortlist else "Saharsa District Hospital"))
    chosen = next((f for f in shortlist if f["facility_name"] == facility_name), shortlist[0] if shortlist else None)
    if chosen is None:
        raise RuntimeError("No facility available for the required capabilities")

    base = {
        "case_id": patient.case_id,
        "facility_name": chosen["facility_name"],
        "facility_distance_km": float(chosen["distance_km_from_demo_origin"]),
        "facility_phone": (chosen["contact"].get("ambulance_phone") or chosen["contact"].get("labour_room_phone") or ""),
        "facility_capabilities": [k for k, v in chosen["capabilities"].items() if v],
        "transport_advice": str(parsed.get("transport_advice", "")),
        "cost_advice": str(parsed.get("cost_advice", "")),
        "voucher_eligibility": str(parsed.get("voucher_eligibility", "")),
    }
    return ReferralPacket(**base, signed_token=_sign(base))
