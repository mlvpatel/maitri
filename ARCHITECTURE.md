# MAITRI-Gemma — Architecture (v2)

This document covers Sections 3 through 8 of the design brief. v2 applies the critique upgrades: a real seventh agent (Referral & Facility), the deterministic safety-rules block as a first-class architectural component, honest Gemma-vs-external-pipeline boundaries, immediate safe escalation, and a per-agent safety-risk justification.

---

## 3. Multi-Agent Architecture

The system is composed of seven cooperating components: **six Gemma-4-powered agents + one deterministic Safety Rules block**, all coordinated by a deterministic Orchestrator (LangGraph). Each agent has a single, narrow responsibility, communicates via typed Pydantic JSON messages, and is independently testable.

> **Why seven?** Each agent reduces *one specific safety risk*. If an agent does not reduce a named risk, it does not exist. This is the architectural defense:
>
> - Intake → missing/ambiguous field risk
> - Retrieval → unsupported medical-knowledge risk
> - Risk Specialist → contextual reasoning gap
> - Deterministic Safety Rules → dangerous under-triage
> - Verifier → hallucinated claims reaching the field
> - Referral & Facility → referring to a closed/unequipped/unaffordable facility
> - Formatter → unsafe communication to mothers/families

The Orchestrator and Audit Logger are infrastructure, not Gemma agents.

### 3.0 Orchestrator (deterministic — not Gemma)

| Field | Value |
|---|---|
| **Responsibility** | Decide what runs next. Owns the session state machine. Deterministic — does not call Gemma for routing. |
| **Input** | Session context (user, language, location, current artifacts, intent) + agent outputs as they arrive |
| **Output** | The next agent to invoke + the structured payload it should receive |
| **Tools used** | LangGraph state graph, SQLite (MVP) / Postgres (post-hackathon) session store |
| **Decision logic** | Finite state machine: `INTAKE → RETRIEVE → SPECIALIST → SAFETY_RULES → VERIFY → (loop if reject) → REFERRAL → FORMAT → AUDIT → DELIVER`. Branch points are guarded by typed predicates. |
| **Failure cases** | State desync, agent timeout, schema violation |
| **Escalation rule** | Two consecutive verifier rejections OR any safety-rule override OR any unrecoverable error → immediate safe escalation path (parallel clinician review, not blocking the referral packet from being prepared) |
| **Validation** | State graph statically checked at boot. Every edge has unit tests. |

### 3.1 Agent: Intake Agent

| Field | Value |
|---|---|
| **Safety risk reduced** | Missing or ambiguous field risk. CHWs work fast, in poor light, with handwritten cards. Without structured intake, every downstream agent operates on garbage. |
| **Responsibility** | Turn the CHW's multimodal input — photo of antenatal card, voice *transcript*, typed text — into a clean structured `PatientSnapshot`. |
| **Input** | `{ image_bytes, voice_transcript_text, typed_text, chw_profile, gps, language }` (note: voice → text transcription is performed by an *external* STT pipeline before this agent runs) |
| **Output** | `PatientSnapshot{ gestational_age_weeks, gravidity, parity, last_bp, last_weight_kg, hb_g_dl, complaints[], language, literacy_level, comorbidities[], completeness_score }` |
| **Gemma 4 role** | Vision: parse the antenatal card form (handwritten or printed) — Gemma 4 E4B's strong document/handwriting understanding. Text: normalize complaints + reconcile across modalities. **Not used for**: STT (external), TTS (external). |
| **Decision logic** | If image quality score < 0.6 → request retake. If two modalities disagree → flag conflict, prefer the more recent and surface to CHW. |
| **Failure cases** | Blurry photo, code-mixed speech, missing fields, ambient-noise-corrupted transcripts |
| **Escalation rule** | If > 3 critical fields missing → CLARIFY sub-flow before any downstream agent runs |
| **Acceptance test** | On the 50-card labelled fixture set, completeness ≥ 0.7 in 90% of cases; field-level accuracy ≥ 92% on BP, gestational age, hemoglobin |

### 3.2 Agent: Retrieval Agent

| Field | Value |
|---|---|
| **Safety risk reduced** | Unsupported medical-knowledge risk. The Specialist must reason from authoritative current evidence, not memorized priors. |
| **Responsibility** | Pull the right evidence from a curated, versioned guideline corpus and a climate-health feed (mocked for hackathon) |
| **Input** | `PatientSnapshot` + the active specialist's query |
| **Output** | `EvidencePack{ guideline_chunks[], climate_signals, citations[], retrieval_confidence }` |
| **Gemma 4 role** | Query rewriting (CHW-language complaint → clinical query terms), reranking top-50 chunks → top-5, generating retrieval_confidence |
| **Tools** | LanceDB (MVP, embedded) → Qdrant (post-hackathon). bge-m3 embeddings. Hybrid BM25 + dense. Climate API mocked from a static snapshot for the demo. |
| **Decision logic** | Always retrieve from at least two independent sources (international + national). If retrieval_confidence < 0.6 → trigger Retrieval Improvement Loop (rewrite query 2 more times, then escalate). |
| **Failure cases** | Stale guideline version, missing language, unsupported condition |
| **Escalation rule** | If no chunk crosses 0.4 similarity → mark `EVIDENCE_INSUFFICIENT`, do not let Specialist proceed; trigger immediate safe escalation |
| **Acceptance test** | Recall@5 ≥ 0.85 against 200 expert-tagged Q&A pairs |

### 3.3 Agent: Risk Triage Specialist

| Field | Value |
|---|---|
| **Safety risk reduced** | Contextual reasoning gap. Rules alone cannot weigh history + climate + comorbidities + cultural context. |
| **Responsibility** | Produce a Green / Amber / Red maternal risk tier with a structured rationale |
| **Input** | `PatientSnapshot` + `EvidencePack` |
| **Output** | `RiskAssessment{ tier, rationale, red_flags[], time_to_referral_hours, recommended_actions[], cited_evidence_ids[], confidence }` |
| **Gemma 4 role** | The core reasoning engine. Gemma 4 31B with thinking mode on (chain exposed but collapsed for clinician audit). Native function calling for: `lookup_drug_safety_in_pregnancy`, `compute_gestational_age`, `query_climate_risk(geo, week)` |
| **Decision logic** | Output is *always* sent to the deterministic Safety Rules block before reaching the Verifier. Specialist is the proposer, not the decider. |
| **Failure cases** | Hallucinated red flags, safety-hedging (everything → Red), confidence high but rationale incoherent |
| **Escalation rule** | Verifier rejection → loop with retrieved counter-evidence injected into prompt (max 2 loops) → safe escalation |
| **Acceptance test** | On 500 clinician-scored cases: tier accuracy ≥ 85%, false-negative Red rate < 2% (the metric that matters most) |

### 3.4 Component: Deterministic Safety Rules (not Gemma)

| Field | Value |
|---|---|
| **Safety risk reduced** | Dangerous under-triage by the model. Even a well-aligned LLM may miss textbook obstetric red flags. |
| **Responsibility** | Apply hard, auditable, version-controlled red-flag rules. Tier may only move *upward* — never down. |
| **Input** | `PatientSnapshot` + Specialist's `RiskAssessment` |
| **Output** | `RiskAssessment` with possibly-promoted `tier` + `rule_overrides[]` |
| **Implementation** | Pure Python, fully unit-tested, no LLM in this path |
| **Example rules** | `BP ≥ 160/110 → Red`; `seizure | severe headache + visual changes → Red`; `vaginal bleeding T2/T3 → Red`; `Hb < 7 g/dL → Red`; `fever ≥ 38°C + chills + dengue-active district → Amber minimum` |
| **Failure cases** | Rule out-of-date; data point in wrong unit |
| **Acceptance test** | 100 textbook red-flag cases — 100% promoted to Red |

### 3.5 Agent: Verifier Agent

| Field | Value |
|---|---|
| **Safety risk reduced** | Hallucinated claims reaching the field. The single biggest failure mode for clinical LLMs. |
| **Responsibility** | Reject or accept the Specialist's output by checking every claim against retrieved evidence |
| **Input** | `RiskAssessment` + `EvidencePack` + `PatientSnapshot` |
| **Output** | `VerificationVerdict{ accepted: bool, hallucination_flags[], unsupported_claims[], safety_flags[], reason }` |
| **Gemma 4 role** | Independent prompt template, different temperature, different system message — *not* a continuation of the Specialist's chain. Two-step: (a) extract every factual claim from the rationale; (b) check each claim against cited evidence chunks via NLI entailment. |
| **Decision logic** | Reject if any of: claim has no supporting chunk, claim contradicts a chunk, recommendation contradicts a deterministic safety rule, language mismatch, PII leak |
| **Failure cases** | Verifier rubber-stamps (false negative); verifier over-rejects safe outputs |
| **Escalation rule** | Two rejections in a row OR verifier disagrees with a deterministic rule → safe escalation (Referral & Facility Agent still runs to prepare a default referral; clinician review fires in parallel) |
| **Acceptance test** | Adversarial set: 100 deliberately-poisoned RiskAssessments. Verifier catches ≥ 95%. False reject rate on clean cases ≤ 5%. |

### 3.6 Agent: Optimizer Agent (per-call rewrite + offline prompt opt)

| Field | Value |
|---|---|
| **Safety risk reduced** | Stuck Specialist with no path to recovery |
| **Responsibility** | Per-call: when the Verifier rejects, rewrite the Specialist's prompt with counter-evidence so the next attempt is grounded. Offline (post-hackathon): batch prompt optimization. |
| **Input** | Per-call: rejected verdict + failing assessment. |
| **Output** | Per-call: revised system prompt for the Specialist. |
| **Gemma 4 role** | Diagnose *why* the output was rejected and rewrite the prompt accordingly |
| **Decision logic** | Bounded to 2 iterations per call. After 2, escalate. |
| **Failure cases** | Loops without converging; prompt drift; prompt injection from CHW input |
| **Acceptance test** | On 50 known-failure cases, Optimizer produces an Accept on retry in ≥ 70% of cases |

### 3.7 Agent: Referral & Facility Agent (the real seventh agent)

| Field | Value |
|---|---|
| **Safety risk reduced** | Referring to a closed, unequipped, or unaffordable facility — a real failure mode in LMICs that turns "Refer to nearest clinic" into harm. |
| **Responsibility** | Resolve the right *available, maternal-care-capable* facility for this patient at this time, with cost and transport context, and assemble a signed referral packet |
| **Input** | Verified `RiskAssessment` + GPS + tier + time-of-day |
| **Output** | `ReferralPacket{ facility_name, facility_id, open_now, maternal_emergency_capable, blood_pressure_check, ambulance_phone, distance_km, cost_level, voucher_eligibility, packet_pdf_url, signed_jwt }` |
| **Gemma 4 role** | Native function calling: `lookup_facility_readiness(gps, capability_required)`, `estimate_transport_cost(origin, dest, time)`, `check_voucher_eligibility(patient, scheme)`. Composes the reasoning that selects the right facility from the candidates returned by the tools. |
| **Tools used** | `data/facilities/saharsa_facility_readiness.json` (mock, hackathon) → Healthsites.io API + MOH facility readiness feed (post-hackathon). Voucher schemes: JSY (India), JKN (Indonesia), Linda Mama (Kenya). |
| **Decision logic** | Select the *nearest* facility that satisfies *capability* requirements for the tier. Surface cost-level and voucher eligibility in the packet. If no capable facility within 30 km → escalate with a note ("nearest capable facility is X km away — recommend ambulance dispatch"). |
| **Failure cases** | Facility data stale; ambulance line dead; cost estimate wrong |
| **Escalation rule** | No capable facility found → safe escalation + ambulance recommendation |
| **Acceptance test** | On 30 mocked districts, packet includes facility, distance, capability flags, cost level, voucher eligibility, and ambulance phone — 100% |

### 3.8 Agent: Formatter Agent

| Field | Value |
|---|---|
| **Safety risk reduced** | Unsafe communication to mothers and families. Scary or condescending output reduces compliance; literacy mismatch causes confusion; cultural mismatch causes refusal. |
| **Responsibility** | Render the verified result for *three* audiences: the CHW (clinical, action-first), the mother (warm, native language), and the family (grounded explanation aimed at the household decision-maker — often a husband or mother-in-law) |
| **Input** | Accepted `RiskAssessment` + `ReferralPacket` + mother's language + literacy level + CHW preference |
| **Output** | `Deliverable{ chw_card_md, mother_explanation_text, family_explanation_text, mother_audio_url (optional, external TTS), referral_packet_pdf, audit_trail_id }` |
| **Gemma 4 role** | Three parallel generations from the same verified facts. **Not used for**: TTS itself — text is generated by Gemma; audio synthesis is an external pipeline (Coqui XTTS-v2 or vendor TTS). |
| **Decision logic** | Mother script always opens with reassurance, never with the risk word. Risk is conveyed by action language ("today we go together"). Family script names the household decision-maker if known and explains the *why* without scaring. |
| **Failure cases** | Hallucinated translation, condescending tone, register mismatch |
| **Escalation rule** | Back-translation equivalence check → mismatch → regenerate (1 retry) → escalate. |
| **Acceptance test** | Native-speaker review panel scores ≥ 4/5 on naturalness for each launch language; back-translation equivalence ≥ 90% |

---

## 4. Routing Logic

The Orchestrator is a deterministic LangGraph state graph. Routing rules:

1. **Boot a session.** Every CHW interaction starts a session with `session_id`, `chw_id`, `patient_pseudo_id`, language, GPS, device class.
2. **First node is always Intake.** No downstream agent runs until Intake produces a valid `PatientSnapshot`.
3. **Confidence-gated routing.**
   - `intake.completeness_score < 0.7` → `CLARIFY` (ask the CHW for the missing fields, generated by Gemma 4 in CHW's language).
   - `intake.completeness_score ≥ 0.7` → run `RETRIEVE`.
4. **Evidence gate.** `EvidencePack.retrieval_confidence < 0.6` → loop retrieval up to 2 times with rewritten queries; on third failure → safe escalation with explicit reason (`EVIDENCE_INSUFFICIENT`).
5. **Specialist runs once.** Output goes through the deterministic Safety Rules block before reaching the Verifier.
6. **Safety Rules apply.** Tier may be promoted upward; never demoted.
7. **Verifier gate.**
   - Accept → Referral & Facility → Formatter → Audit → Deliver.
   - Reject → Optimizer rewrites Specialist prompt with counter-evidence → Specialist re-runs.
   - Two rejections → safe escalation: Referral & Facility still runs with a default-Red package; parallel clinician review notified immediately.
8. **Refusal rule.** Drug overdose query, prescription strength request, abortion legality outside policy, attempt to extract another patient's PII → refuse with structured explanation, log to audit, do not engage Specialist.
9. **All inter-agent messages are typed.** Pydantic schemas, validated at every edge. A schema violation aborts the run with a `STRUCTURED_OUTPUT_INVALID` audit entry.

### Confidence scoring

Confidence is a weighted combination of retrieval similarity (40%), self-reported model confidence (20%), agreement between Specialist and the deterministic rule layer (30%), and back-translation equivalence for output language (10%). Weights are eval-tuned, not arbitrary.

### When the system asks the user

The system asks the CHW (never the mother directly) when: (a) intake is incomplete, (b) two modalities conflict, (c) two consecutive Verifier rejections, (d) language ambiguity. At most one round-trip per case.

---

## 5. Feedback Loops

| Loop | Trigger | Action | Termination |
|---|---|---|---|
| **Answer quality** | Verifier rejects rationale | Optimizer rewrites Specialist prompt with counter-evidence | Accept, or 2 iterations |
| **Hallucination detection** | Claim ↔ evidence entailment fails | Strip unsupported claim; if removal leaves output incoherent → regenerate | 2 iterations |
| **Safety check** | Deterministic safety rule promotes tier | Tier moves upward; flagged for parallel clinician audit | Single pass — non-negotiable |
| **Facility availability** | Selected facility shows `open_now=false` or capability mismatch | Re-query with relaxed distance + capability constraints; recommend ambulance if none found | Single pass; escalate if no match |
| **CHW feedback** | CHW marks "this didn't help" | Tag flows to offline Optimization queue; weekly batch | Weekly batch (post-hackathon) |
| **Retrieval improvement** | Retrieval confidence < 0.6 | Rewriter generates 2 alternative queries | 2 query rewrites per call |

---

## 6. Failure Handling

| Failure | Detection | Fallback | Recovery | User-facing |
|---|---|---|---|---|
| Missing data | Intake schema validation | Ask CHW for exactly the missing fields | Resume after fields filled | "I need 3 more details: blood pressure, last period date, headache yes/no" |
| Ambiguous request | Specialist confidence < 0.5 OR conflicting modalities | Clarification round (max 1) | After 1 round → safe default | "I see two BP readings — which is the latest?" |
| Low model confidence | Confidence < tier-specific threshold | Promote tier upward; refer | Audit log + flag | CHW sees Amber/Red instead of Green |
| Hallucinated answer | Verifier entailment fail | Optimizer loop; if persists → safe escalation | Up to 2 rewrites | CHW sees "Awaiting clinician review — referral packet still ready" |
| Retrieval failure | retrieval_confidence < 0.4 | EVIDENCE_INSUFFICIENT short-circuit + safe escalation | Surface to ops dashboard | "Refer to nearest maternal-care-capable facility immediately" with explicit reason |
| Facility unavailable | Selected facility closed / capability missing | Re-query with relaxed constraints; ambulance recommendation | Background refresh | "Nearest capable facility is X km — ambulance Y" |
| Tool / API failure | Function-call error with retry exhausted | Stub mode (cached snapshot) | Background refresh; alert ops | "Live data unavailable — referral still standard" |
| Unsafe user request | Refusal classifier match | Hard refuse, do not engage Specialist | Audit log | "I can't help with that, but I can help triage symptoms" |
| Offline / low connectivity | Network probe + circuit breaker | Local IndexedDB queue of cases; sync when online | Background sync with conflict resolution | "Will sync when online" |
| High latency | p95 > 8s | Stream tier first, defer narrative; shed light optimizer pass | Fallback to E4B variant on shed | CHW sees streaming Green/Amber/Red while rationale composes |
| Invalid structured output | Pydantic validation fail | Single retry with stricter prompt | After retry → safe escalation | Same as hallucination path |

**Immediate safe escalation rule:** when escalation triggers, the Referral & Facility Agent still runs and prepares a default-Red packet so the CHW is *not* left empty-handed. Clinician review fires in parallel through the reviewer dashboard. We do **not** make the CHW wait 24 hours for clinician review before any action — that is unsafe for maternal danger signs.

---

## 7. Scalability and Real-World Readiness

| Dimension | MVP (hackathon) | Post-hackathon roadmap |
|---|---|---|
| **Modular agent design** | Each agent is a Python module with a single `run(input) -> output` function and Pydantic-typed I/O | Promote to gRPC services for horizontal scale |
| **API layer** | FastAPI on Cloud Run, OAuth2 stub for CHW, per-tenant rate limits | mTLS for hospital connectors, OpenAPI 3 contract published |
| **Cloud deployment** | Vertex AI for 31B agents, HF Inference Endpoints for E4B | Region-pinned per LMIC for data residency |
| **Offline / low-connectivity** | PWA with IndexedDB queue; cases captured offline are queued, hashed, signed, synced when connectivity returns | Background sync with conflict resolution + last-known-good guideline cache |
| **Data privacy** | Edge PII strip; patient_pseudo_id = HMAC(name+dob+chw_id, secret); names + addresses never leave device by default | Re-identification only on opt-in for clinic referral, gated by hospital signing key |
| **Monitoring** | LangSmith traces for every agent call; counts in console for hackathon | OpenTelemetry → Grafana Cloud post-hackathon |
| **Logging** | SQLite append-only audit log (MVP); writes JSON entries for every agent I/O + model version | Postgres + WORM S3 archive (Article-12-grade) |
| **Evaluation metrics** | Tier accuracy, false-negative Red rate, retrieval recall@5, latency p50/p95, language coverage | A/B promotion gates in CI |
| **Human-in-the-loop** | Reviewer dashboard (read-only); every Red case marked for review; immediate safe escalation never blocks the referral packet | SLAs; reviewer feedback flows to eval set |
| **Multilingual support** | Launch with 2 languages: English + Hindi. Bahasa Indonesia + Swahili as bonus | Hausa, Yoruba, Tamil, Marathi, Bengali, Telugu, French, Portuguese (Brazil), Spanish (LatAm) |
| **Low-resource device support** | PWA targets Android 10, 2GB RAM, 360x640 screens | Voice-first UI for low-literacy CHWs |
| **Cost ceiling** | ~USD 0.02 per case at 1M cases/month with caching + E4B for routing-friendly tasks | Public Vertex pricing screenshot in writeup |

---

## 8. Technical Implementation Plan

The detailed dev option, framework choices, and rationale live in `TECH_STACK.md`. Summary:

| Layer | MVP choice | Why |
|---|---|---|
| **Frontend** | React + Vite + Tailwind PWA, Workbox offline | Smallest skill ramp, PWA install on Android, offline by design |
| **Backend** | FastAPI (Python 3.12) on Cloud Run | Fast to ship, async-native, easy to put behind Vertex AI |
| **Agent framework** | LangGraph | Deterministic FSM + native streaming + LangSmith traces — better fit than CrewAI for safety-critical health flow |
| **Gemma 4 inference** | Vertex AI (Gemma 4 31B for reasoning + verifier) + HF Inference Endpoints (Gemma 4 E4B for intake + formatter) | Region-pinned, private, predictable pricing |
| **STT** | External: Whisper-faster (open) or Google STT (vendor) | Honest about Gemma's role |
| **TTS** | External: Coqui XTTS-v2 (open, multilingual) | Honest about Gemma's role |
| **Vector / RAG** | LanceDB (embedded, file-backed) for MVP → Qdrant Cloud post-hackathon | Embedded for hackathon = zero infra; bge-m3 embeddings |
| **Database** | SQLite (audit + sessions) for MVP → Postgres post-hackathon | Zero infra for hackathon |
| **API tools / function calling** | Native Gemma 4 function calling. Tools: `lookup_facility_readiness`, `query_climate_risk`, `lookup_drug_safety_in_pregnancy`, `compute_gestational_age`, `escalate_to_clinic` (mock SMS) | Showcases Gemma's strength, not bolted on |
| **Climate-health data** | Static snapshot of NASA POWER + Malaria Atlas + OpenDengue for the demo district | Refreshable later |
| **Deployment** | Cloud Run + Vertex (no Terraform required for MVP — `gcloud` deploy) | Speed |
| **Eval framework** | LangSmith + custom hallucination harness + 5 runnable case notebooks | Reproducibility |
| **CI/CD** | GitHub Actions: lint, unit, eval-gate (5 cases) | Promotion gate visible in README |

### 14-day build plan (May 4 → May 18)

| Day | Milestone |
|---|---|
| 1 | Finalize scope, repo skeleton, Pydantic schemas, sample-case fixtures |
| 2 | FastAPI + LangGraph orchestrator skeleton; SQLite audit table |
| 3 | Intake agent (Gemma 4 E4B) on photo + voice transcript + text; PatientSnapshot schema |
| 4 | LanceDB index built from a 200-chunk WHO + India RMNCH+A maternal-guideline corpus; Retrieval agent |
| 5 | Risk Specialist prompt v1 + deterministic Safety Rules block |
| 6 | Verifier prompt v1 + claim/evidence checker; reject → recover loop wired |
| 7 | Reject → Optimizer → Specialist re-run **working on Case 2** |
| 8 | Formatter: CHW card + Mother explanation + Family explanation in Hindi |
| 9 | Referral & Facility Agent + `saharsa_facility_readiness.json` mock + signed referral packet |
| 10 | Audit trace UI (read-only page) |
| 11 | 5 reference notebooks runnable; eval harness produces a one-page report |
| 12 | README + ARCHITECTURE + screenshots; record any glitches for video B-roll |
| 13 | Record demo video (single hero case) + Hindi voice generation |
| 14 | Kaggle writeup polish; submission dry-run; buffer for re-record |

---

## Reference data assumptions

- **Antenatal card dataset**: bootstrap with 50 synthetic + real-but-anonymized cards. Inter-annotator agreement documented.
- **Guideline corpus**: WHO Antenatal Care Recommendations 2016 + 2025 update; FIGO 2024 hypertensive disorders; India ICMR + RMNCH+A; ~200 chunks at 800 tokens each for the MVP.
- **Climate signals**: static snapshot for Saharsa district May 2026 — heat index, dengue activity, malaria risk.
- **Facility readiness**: hand-curated `data/facilities/saharsa_facility_readiness.json` with 6 facilities, including 1 closed-now and 1 capability-limited to test the agent's selection logic.

---

The next document — `FLOWCHART.md` — visualizes the v2 architecture in Mermaid and Excalidraw.
