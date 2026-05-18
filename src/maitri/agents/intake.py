"""Intake agent. Normalizes free text plus structured fields into a PatientSnapshot."""

from __future__ import annotations

from typing import Any

from ..gemma_client import GemmaClient
from ..schemas import PatientSnapshot
from ._json import extract_json
from ..config import get_settings


_SYSTEM = (
    "You are an intake assistant for community health workers. Convert the free text notes "
    "and the partial structured fields into a single JSON object that conforms exactly to "
    "the PatientSnapshot schema. Use null where unknown. Do not invent vital signs that are "
    "not mentioned. Output JSON only, no prose."
)


_SCHEMA_HINT = (
    "PatientSnapshot fields: case_id (string), age_years (int), gravida (int), para (int), "
    "gestational_age_weeks (number or null), lmp_date (ISO date or null), systolic_bp (int or null), "
    "diastolic_bp (int or null), hemoglobin_g_dl (number or null), temperature_c (number or null), "
    "pulse_bpm (int or null), fetal_movements_normal (bool or null), bleeding (bool or null), "
    "severe_headache (bool or null), blurred_vision (bool or null), convulsions (bool or null), "
    "swelling_face_or_hands (bool or null), fever (bool or null), reduced_urine (bool or null), "
    "known_conditions (array of strings), medications (array of strings), "
    "language_preference (string), district (string), free_text_notes (string)."
)


def run_intake(
    case_id: str,
    raw_text: str,
    structured: dict[str, Any] | None = None,
    *,
    client: GemmaClient,
) -> PatientSnapshot:
    structured = dict(structured or {})
    structured.setdefault("case_id", case_id)
    user_payload = (
        f"Case id: {case_id}\n"
        f"Structured fields supplied: {structured}\n"
        f"Free text from the community health worker: {raw_text}\n"
        f"Schema: {_SCHEMA_HINT}"
    )
    resp = client.chat(
        messages=[
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": user_payload},
        ],
        model=get_settings().light_model,
        agent="intake",
        temperature=0.1,
        max_tokens=900,
        response_format={"type": "json_object"},
    )
    obj = extract_json(resp.content)
    # Drop null values so Pydantic defaults take effect for required-with-default fields
    obj = {k: v for k, v in obj.items() if v is not None}
    obj["case_id"] = case_id
    for k, v in structured.items():
        if v is not None:
            obj.setdefault(k, v)
    return PatientSnapshot.model_validate(obj)
