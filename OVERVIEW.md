# MAITRI-Gemma — Safety-Verified Maternal Referral Intelligence

> **Seven-agent Gemma 4 maternal referral co-pilot · offline-first PWA · cloud Gemma inference · verified before delivery**
>
> Built for the Kaggle Gemma 4 Good Hackathon. Final submission **May 18, 2026**.

---

## The one winning sentence

> **MAITRI is a safety-verified Gemma 4 maternal referral co-pilot that helps community health workers detect pregnancy danger signs, catches unsupported AI reasoning before it reaches the field, and produces clinic-ready, facility-aware referral packets in low-connectivity settings.**

It does not diagnose. It does not replace clinicians. It catches itself before it harms.

---

## The unforgettable signature

Every artifact in this repo points at the same moment:

> **The AI makes a realistic medical hallucination. The verifier catches it. The system recovers. The CHW gets a safe referral packet.**

If you remember nothing else from this submission, remember that loop.

---

## Tagline (for slides + Kaggle thumbnail)

**"One woman dies every two minutes. MAITRI gives every community health worker a safety-verified maternal referral co-pilot."**

---

## The problem in one paragraph

In 2023, ~260,000 women died from pregnancy and childbirth — **one death every two minutes**, 94% in low- and middle-income countries (LMICs). In **Saharsa district, Bihar, India** — the district we anchor this MVP on — there are roughly 1–2 doctors per 1,000 people, the nearest functional maternal-care facility is often 10–20 km away, and the frontline is the ASHA worker carrying a paper antenatal card and a 2GB-RAM phone. She has no decision support, no facility-readiness data, no audit trail, and no way to communicate triage urgency to the family.

## What MAITRI does

A CHW opens MAITRI on a low-end Android phone, photographs the antenatal card, speaks vitals in her local language (speech-to-text handled by an external pipeline), and within seconds Gemma 4 produces:

1. **Risk tier** — Green / Amber / Red with cited WHO + national-guideline evidence
2. **Deterministic-rule check** — red-flag rules can promote a tier upward (never down) so the model fails safe
3. **Verified rationale** — an independently-prompted Gemma 4 verifier checks every claim against retrieved evidence; unsupported claims trigger rewrite-and-re-run
4. **Facility-aware referral packet** — nearest *available, maternal-care-capable* facility, with cost context and ambulance phone, generated and signed
5. **Two human-facing outputs**: a clinical CHW card (English + local language) and a warm Hindi/Bahasa/Hausa/Swahili explanation for the mother *and* her family
6. **Audit trace** — every prompt, every cited chunk, every tool call, every model version logged to a WORM store

---

## What is Gemma 4 used for, exactly

Five visible moments — no overclaiming:

1. **Gemma 4 E4B — Field intake.** Reads the antenatal card photo, normalizes the CHW's text, structures the *transcript* of her voice (STT itself is external).
2. **Gemma 4 31B — Maternal risk reasoning.** Thinking-mode chain-of-reasoning over `PatientSnapshot + EvidencePack`, with native function calling for facility lookup and gestational-age calculation.
3. **Gemma 4 31B — Verifier.** Independent prompt template, claim-↔-evidence entailment check; rejects unsupported claims before they reach the field.
4. **Gemma 4 E4B — Multilingual formatter.** Two parallel generations: a clinical CHW card and a warm family-facing explanation, in the mother's language.
5. **Gemma 4 function calling — Tool orchestration.** Facility readiness lookup, gestational-age compute, referral-packet generation, climate-risk query.

> **Speech-to-text and text-to-speech are external pipeline components.** Gemma 4 owns multimodal understanding, reasoning, verification, tool use, and language generation. We do not claim Gemma performs production-grade audio transcription itself.

---

## Why MAITRI is multi-agent, not a chat wrapper

Every agent exists because it reduces *one specific safety risk*:

| Agent | Risk it reduces |
|---|---|
| Intake | Missing or ambiguous field risk |
| Retrieval | Unsupported medical-knowledge risk |
| Risk Specialist | Contextual reasoning gap (model alone cannot weigh district + climate + history) |
| Deterministic Safety Rules | Dangerous under-triage by the model |
| Verifier | Hallucinated claims reaching the field |
| Referral & Facility | Referring to a closed, unequipped, or unaffordable facility |
| Formatter | Unsafe communication to mothers/families (scary words, register mismatch) |
| Audit Logger | Inability to review or learn from cases post-hoc |

This is the architecture's defense. It is not multi-agent for decoration.

---

## Honest readiness signal

| Signal | Status (target by May 18) |
|---|---|
| Clinical safety reviewed by | 1 OB-GYN / maternal-health doctor (advisory) |
| Workflow reviewed by | 1 ASHA-style frontline worker (interviewed or reference-cited if not in person) |
| Language reviewed by | 1 native Hindi speaker; 1 native Bahasa speaker (target) |
| Facility data | Mock JSON for Saharsa district (pre-populated, public sources where available) |
| Live trial | Out of scope for hackathon; designed-for-trial documented in roadmap |

We will be explicit in the writeup about what is *built* vs *advisory* vs *roadmap*. No invented signal.

---

## At a glance

- **Architecture**: 7 agents (6 Gemma-powered + 1 deterministic safety-rules block, all coordinated by a deterministic Orchestrator)
- **Inference**: Gemma 4 31B (reasoning + verification) + Gemma 4 E4B (multimodal intake + formatter), served via Vertex AI / HF Inference Endpoints
- **Frontend**: Offline-first React PWA with IndexedDB queue
- **Compliance**: NIST AI RMF + WHO ethics for health AI + ISO 42001 alignment + EU AI Act Article 12 *logging discipline* (adopted as a standard, not a legal claim where not in jurisdiction)
- **Eval**: 5 runnable reference cases, hallucination harness, latency budget, false-negative-Red rate as the metric that matters most

---

## Documents in this repo

| File | Purpose |
|---|---|
| `README.md` | This file — concept, signature, doc index |
| `ARCHITECTURE.md` | Full multi-agent design with safety-risk justification (Sections 3–8) |
| `FLOWCHART.md` | Mermaid + Excalidraw diagrams (Section 9) |
| `DEMO_SCRIPT.md` | Single-hero-case 3-minute video script + live demo checklist (Section 2 + 12) |
| `EVALUATION.md` | 5 runnable reference cases + metrics + harness plan (Section 11) |
| `KAGGLE_STRATEGY.md` | Submission strategy, writeup outline, judging-score plan (Section 12) |
| `JUDGE_CRITIQUE.md` | Self-critique + v2 resolutions (Section 13) |
| `REPO_STRUCTURE.md` | Lean MVP repo layout (Section 10) |
| `TECH_STACK.md` | Chosen dev option + tech stack with rationale |
| `data/facilities/saharsa_facility_readiness.json` | Mock facility readiness for the demo district |
| `maitri_architecture.excalidraw` | Hand-drawn architecture diagram for the slide deck |

---

## Status

Design v2 (with critique applied) — May 4, 2026. Build phase: 14 days to submission.
