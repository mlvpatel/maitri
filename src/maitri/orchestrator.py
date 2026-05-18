"""Deterministic orchestrator over the seven agent pipeline.

The orchestrator itself contains no language model calls. It runs through a fixed
state sequence so that the safety paths can be verified statically.

States: INTAKE -> RETRIEVAL -> SPECIALIST -> SAFETY_RULES -> VERIFY
        [ -> OPTIMIZE -> SPECIALIST_RETRY -> VERIFY ]   (at most once)
        -> REFERRAL -> FORMAT -> DONE
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from .agents.formatter import run_formatter
from .agents.intake import run_intake
from .agents.optimizer import run_optimizer
from .agents.referral_facility import run_referral_facility
from .agents.retrieval import run_retrieval
from .agents.specialist import run_specialist
from .agents.verifier import run_verifier
from .audit import AuditLog
from .gemma_client import GemmaClient
from .safety import evaluate_safety_rules
from .schemas import (
    Deliverable,
    EvidencePack,
    PatientSnapshot,
    ReferralPacket,
    RiskAssessment,
    VerificationVerdict,
)


@dataclass
class CaseTrace:
    case_id: str
    patient: PatientSnapshot | None = None
    evidence: EvidencePack | None = None
    initial_assessment: RiskAssessment | None = None
    safety_rule_ids: list[str] = field(default_factory=list)
    first_verdict: VerificationVerdict | None = None
    optimizer_hint: str | None = None
    revised_assessment: RiskAssessment | None = None
    second_verdict: VerificationVerdict | None = None
    final_assessment: RiskAssessment | None = None
    final_verdict: VerificationVerdict | None = None
    referral: ReferralPacket | None = None
    deliverable: Deliverable | None = None
    audit_call_ids: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


class Orchestrator:
    def __init__(self, audit: AuditLog | None = None) -> None:
        self._audit = audit or AuditLog()
        self._case_id_ctx = ""

        def _sink(entry: dict) -> None:
            self._audit.record(self._case_id_ctx, entry)
            cid = entry.get("call_id")
            if cid and cid not in self._trace.audit_call_ids:
                self._trace.audit_call_ids.append(cid)

        self._sink = _sink
        self._trace = CaseTrace(case_id="")

    def run(
        self,
        raw_text: str,
        structured: dict | None = None,
        *,
        case_id: str | None = None,
        force_demo_hallucination: bool = False,
    ) -> CaseTrace:
        case_id = case_id or f"case-{uuid.uuid4().hex[:8]}"
        self._case_id_ctx = case_id
        self._trace = CaseTrace(case_id=case_id)

        with GemmaClient(audit_sink=self._sink) as client:
            # Intake
            patient = run_intake(case_id, raw_text, structured, client=client)
            self._trace.patient = patient

            # Retrieval
            evidence = run_retrieval(patient)
            self._trace.evidence = evidence
            self._audit.record(case_id, {"agent": "retrieval", "model": "local", "call_id": f"ret-{case_id}", "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0, "latency_ms": 0, "evidence_chunks": [c.chunk_id for c in evidence.chunks]})

            # Specialist draft
            assessment = run_specialist(
                patient, evidence, client=client, force_unsupported_claim=force_demo_hallucination
            )
            self._trace.initial_assessment = assessment

            # Deterministic safety rules
            safety = evaluate_safety_rules(patient, assessment.tier)
            self._trace.safety_rule_ids = safety.fired_rule_ids
            if safety.fired:
                assessment.tier = safety.promoted_tier
                assessment.recommended_actions = list(
                    dict.fromkeys(assessment.recommended_actions + safety.reasons)
                )
                self._trace.notes.append(
                    f"Safety rules fired: {safety.fired_rule_ids}; tier promoted to {safety.promoted_tier.value}"
                )
                self._audit.record(case_id, {"agent": "safety_rules", "model": "deterministic", "call_id": f"safety-{case_id}", "prompt_tokens": 0, "completion_tokens": 0, "cost_usd": 0.0, "latency_ms": 0, "fired": safety.fired_rule_ids, "promoted_tier": safety.promoted_tier.value})

            # Verify
            verdict = run_verifier(assessment, evidence, client=client)
            self._trace.first_verdict = verdict

            # Optimizer recovery loop, at most once
            if not verdict.accepted:
                hint = run_optimizer(assessment, verdict, client=client)
                self._trace.optimizer_hint = hint
                revised = run_specialist(
                    patient, evidence, client=client, optimizer_hint=hint
                )
                self._trace.revised_assessment = revised
                second = run_verifier(revised, evidence, client=client)
                self._trace.second_verdict = second
                # The revised draft becomes final regardless of second verdict outcome;
                # if still rejected the orchestrator marks the case for manual review.
                assessment = revised
                verdict = second
                if not verdict.accepted:
                    self._trace.notes.append("Verifier still rejected after one rewrite; case escalated for manual review.")

            # Safety rules re evaluation after optimizer step
            safety2 = evaluate_safety_rules(patient, assessment.tier)
            if safety2.fired:
                assessment.tier = safety2.promoted_tier

            self._trace.final_assessment = assessment
            self._trace.final_verdict = verdict

            # Referral and Facility
            referral = run_referral_facility(patient, assessment, client=client)
            self._trace.referral = referral

            # Formatter
            formatted = run_formatter(assessment, referral, client=client)

            deliverable = Deliverable(
                case_id=case_id,
                risk=assessment,
                verdict=verdict,
                referral=referral,
                formatted=formatted,
                audit_ids=list(self._trace.audit_call_ids),
            )
            self._trace.deliverable = deliverable

        return self._trace
