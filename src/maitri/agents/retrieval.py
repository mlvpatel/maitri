"""Retrieval agent. Builds an evidence pack relevant to the patient."""

from __future__ import annotations

from ..rag import retrieve
from ..schemas import EvidencePack, PatientSnapshot


def _build_query(p: PatientSnapshot) -> str:
    parts: list[str] = ["antenatal pregnancy"]
    if p.systolic_bp and p.systolic_bp >= 140:
        parts.append("hypertension blood pressure")
    if p.severe_headache:
        parts.append("severe headache")
    if p.blurred_vision or p.swelling_face_or_hands:
        parts.append("pre eclampsia warning signs")
    if p.convulsions:
        parts.append("eclampsia magnesium sulphate")
    if p.hemoglobin_g_dl is not None and p.hemoglobin_g_dl < 10:
        parts.append("anemia hemoglobin pregnancy")
    if p.bleeding:
        parts.append("antepartum hemorrhage bleeding")
    if p.fetal_movements_normal is False:
        parts.append("reduced fetal movement")
    if p.fever or (p.temperature_c is not None and p.temperature_c >= 38):
        parts.append("fever sepsis pregnancy")
    if not parts[1:]:
        parts.append("iron folic acid supplementation pregnancy weight gain")
    return " ".join(parts)


def run_retrieval(patient: PatientSnapshot, top_k: int = 5) -> EvidencePack:
    return retrieve(patient.case_id, _build_query(patient), top_k=top_k)
