"""Pydantic message contracts shared by every agent."""

from __future__ import annotations

from datetime import date
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class RiskTier(str, Enum):
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class PatientSnapshot(BaseModel):
    case_id: str
    age_years: int
    gravida: int = 0
    para: int = 0
    gestational_age_weeks: Optional[float] = None
    lmp_date: Optional[date] = None
    systolic_bp: Optional[int] = None
    diastolic_bp: Optional[int] = None
    hemoglobin_g_dl: Optional[float] = None
    temperature_c: Optional[float] = None
    pulse_bpm: Optional[int] = None
    fetal_movements_normal: Optional[bool] = None
    bleeding: Optional[bool] = None
    severe_headache: Optional[bool] = None
    blurred_vision: Optional[bool] = None
    convulsions: Optional[bool] = None
    swelling_face_or_hands: Optional[bool] = None
    fever: Optional[bool] = None
    reduced_urine: Optional[bool] = None
    known_conditions: list[str] = Field(default_factory=list)
    medications: list[str] = Field(default_factory=list)
    language_preference: str = "hi"
    district: str = "Saharsa"
    free_text_notes: str = ""


class EvidenceChunk(BaseModel):
    chunk_id: str
    source: str
    title: str
    text: str
    year: Optional[int] = None
    section: Optional[str] = None


class EvidencePack(BaseModel):
    case_id: str
    query: str
    chunks: list[EvidenceChunk]


class Claim(BaseModel):
    claim_id: str
    text: str
    cites: list[str] = Field(default_factory=list)


class RiskAssessment(BaseModel):
    case_id: str
    tier: RiskTier
    headline: str
    rationale: str
    claims: list[Claim]
    recommended_actions: list[str]
    function_calls: list[dict] = Field(default_factory=list)


class VerificationVerdict(BaseModel):
    case_id: str
    accepted: bool
    unsupported_claim_ids: list[str] = Field(default_factory=list)
    rationale: str = ""
    suggested_fix: str = ""


class ReferralPacket(BaseModel):
    case_id: str
    facility_name: str
    facility_distance_km: float
    facility_phone: str
    facility_capabilities: list[str]
    transport_advice: str
    cost_advice: str
    voucher_eligibility: str
    signed_token: str


class FormattedOutputs(BaseModel):
    chw_card_en: str
    mother_message_hi: str
    family_message_hi: str


class Deliverable(BaseModel):
    case_id: str
    risk: RiskAssessment
    verdict: VerificationVerdict
    referral: ReferralPacket
    formatted: FormattedOutputs
    audit_ids: list[str] = Field(default_factory=list)
