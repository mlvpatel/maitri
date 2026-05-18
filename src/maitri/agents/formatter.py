"""Formatter agent. Produces CHW card and mother and family messages."""

from __future__ import annotations

import json

from ..config import get_settings
from ..gemma_client import GemmaClient
from ..schemas import FormattedOutputs, ReferralPacket, RiskAssessment
from ._json import extract_json


_SYSTEM = (
    "You produce three short outputs for one maternal triage case. Output JSON only "
    "with three string fields: chw_card_en (a concise clinical card in English with "
    "tier, the one sentence headline, the top two clinical actions, the facility name "
    "and phone), mother_message_hi (Hindi, warm, second person, 2 to 3 sentences, "
    "no technical jargon, mention the facility name in Hindi or English, no diagnosis "
    "labels), family_message_hi (Hindi, addressed to the household decision maker, "
    "2 to 3 sentences, explain why transport is recommended now, mention voucher "
    "scheme by name if listed)."
)


def run_formatter(
    assessment: RiskAssessment,
    referral: ReferralPacket,
    *,
    client: GemmaClient,
) -> FormattedOutputs:
    payload = {
        "tier": assessment.tier.value,
        "headline": assessment.headline,
        "top_actions": assessment.recommended_actions[:2],
        "facility_name": referral.facility_name,
        "facility_phone": referral.facility_phone,
        "transport_advice": referral.transport_advice,
        "cost_advice": referral.cost_advice,
        "voucher_eligibility": referral.voucher_eligibility,
    }
    resp = client.chat(
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        model=get_settings().light_model,
        agent="formatter",
        temperature=0.3,
        max_tokens=900,
        response_format={"type": "json_object"},
    )
    parsed = extract_json(resp.content)
    return FormattedOutputs(
        chw_card_en=str(parsed.get("chw_card_en", "")),
        mother_message_hi=str(parsed.get("mother_message_hi", "")),
        family_message_hi=str(parsed.get("family_message_hi", "")),
    )
