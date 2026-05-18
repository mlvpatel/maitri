# MAITRI-Gemma — Demo & 3-Minute Video Script (v2)

This is the v2 single-hero-case version. The whole video centers on **one emotional case + one AI mistake caught by the verifier**. We do not stack three countries, climate, dashboards, and multilingual side-by-sides into the main video. Multilingual is a 15-second bonus segment at most. The hero is the rejection-recovery loop.

---

## 2. The User Story (Hero Case)

### Persona

**Sunita Devi**, 38, ASHA worker in **Saharsa district, Bihar, India**. Eighth-grade education. Walks 6 km a day. Carries a paper register and a 2GB-RAM Android phone. Visits 22 pregnant women per month. **Today she is visiting Lakshmi, 19, second pregnancy, week 32.**

### Before (the problem)

Sunita writes Lakshmi's BP — **142/94** — on the antenatal card. The number "feels high" but she does not know if it qualifies as preeclampsia risk. The nearest doctor is 14 km away. Last week a different mother lost her baby; the family says "she also had high BP." Sunita radios her supervisor; voicemail. She tells Lakshmi to "rest." She moves on. She is doing her best.

This is happening in 260,000 households a year.

### During (with MAITRI)

Sunita opens MAITRI on her phone (works offline; queues if no signal).

1. **0:00** — She points the camera at the antenatal card. Gemma 4 E4B reads the handwriting, pre-fills the snapshot. She corrects two fields by voice in Hindi *(an external STT pipeline turns voice into text; Gemma reads the text)*.
2. **0:04** — She speaks: "Sir dard hai, paer suje hain" (headache, swollen feet). Intake Agent extracts symptoms.
3. **0:06** — Retrieval pulls WHO 2025 hypertension thresholds + India RMNCH+A protocols + the Saharsa-district heat-wave snapshot. EvidencePack confidence 0.78.
4. **0:08** — Specialist (Gemma 4 31B + thinking mode) outputs **AMBER** — confidence 0.82. Rationale includes the line "proteinuria detected" — but this claim has no supporting chunk.
5. **0:09** — Deterministic Safety Rules apply: BP 142/94 is below the auto-Red threshold of 160/110. Tier remains Amber. (If BP had been 162/110, the rules would have promoted to Red.)
6. **0:10** — Verifier rejects: "proteinuria detected" is not in evidence. Optimizer rewrites the Specialist prompt with counter-evidence. Specialist re-runs.
7. **0:12** — Verifier accepts. Tier remains AMBER. Reasoning is now grounded in 3 cited chunks.
8. **0:13** — Referral & Facility Agent runs function calls: `lookup_facility_readiness(saharsa_gps)` → "Saharsa District Hospital, open now, maternal-emergency capable, 14 km, public/free, ambulance +91-xxxx, JSY-eligible".
9. **0:14** — Formatter generates three outputs in parallel:
   - **CHW card** (English + Hindi clinical summary, action-first)
   - **Mother explanation** (warm Hindi, no scary words, action-clear: "Beti, today we will go to Patna PHC together…")
   - **Family explanation** (Hindi, aimed at husband/mother-in-law: "Lakshmi has symptoms that should be checked today. This does not mean something bad will happen, but waiting can be risky. Going now helps the doctor prevent complications early.")
10. **0:14** — Audit log entry written: every agent call, every prompt version, every cited chunk, every tool call, every model version, timestamps. Required artifact for Article 12 logging discipline.

Total time: **14 seconds** (cloud round-trip in Saharsa-region demo conditions).

### After (measurable improvement)

- **Triage time** per case: ~3 min mental + radio → 14 s
- **Referral lead time** for Amber/Red: 4–18 hours → < 30 min
- **CHW confidence** (Likert 1–5): 2.6 → 4.4 (target, internal trial)
- **Coverage**: 22 visits/day → 30+ responsibly handled
- **Audit**: every Red has a complete trace; clinicians stop spending Friday afternoon reconstructing Tuesday

### The wow moment

The verifier rejection lights up red on screen, the optimizer fires, the specialist re-runs, and the screen turns green — all in three seconds, on tape. *That* is the moment judges remember. (Multilingual is a tasteful 15-second bonus at the end; not the main event.)

### What to show in the live demo

1. The CHW phone interface (real or recorded).
2. The agent trace panel — agent-by-agent JSON messages live-streaming, with the verification REJECT in red.
3. The Optimizer rewrite + Specialist re-run.
4. The Verifier ACCEPT in green.
5. The Referral & Facility Agent's tool calls and the assembled packet (facility, distance, cost, ambulance, JSY).
6. The audit log entry.
7. (Bonus, if time): switch language to Hindi and play the family explanation.

---

## 12.A. 3-Minute Video Script (180 seconds, v2 — single hero case structure)

> **Format:** voice-over with cuts. No talking-head. Two-line max on-screen text.

### 0:00 – 0:20  ·  HUMAN STAKES

**Visual:** Black frame. White serif text fades in: **"Every two minutes, a woman dies giving birth."** Cut to slow drone over a Bihar village at dusk. Hold.

**VO:** "Every two minutes, a woman dies giving birth. Ninety-four percent of those deaths happen where there is one doctor for every thousand patients. The frontline is not a doctor. It is a community health worker. Today she is visiting Lakshmi — week thirty-two, blood pressure one-forty-two over ninety-four. The nearest doctor is fourteen kilometres away. There is no signal."

### 0:20 – 0:45  ·  SIMPLE WORKFLOW

**Visual:** Sunita opens MAITRI. Camera on antenatal card. Snapshot fills. Voice waveform. Then a clean trace panel showing the agent boxes lighting up in sequence.

**VO:** "Sunita opens MAITRI. She photographs the card. Gemma 4 reads the handwriting. She speaks her observations. Within seconds, six Gemma agents and one deterministic safety rules block have intercepted the case, retrieved WHO and Indian protocols, and reasoned about the risk."

### 0:45 – 1:20  ·  TECHNICAL PROOF

**Visual:** The trace panel — the seven boxes light up one by one. Confidence scores appear next to each. The Specialist box outputs an AMBER chip.

**VO:** "The deterministic safety rules check first — BP one-forty-two over ninety-four is below the automatic-Red threshold of one-sixty over one-ten, so the model's tier holds. Then the verifier runs."

### 1:20 – 1:45  ·  TENSION — THE AI MISTAKE

**Visual:** The Verifier box turns red. A line in the rationale highlights: "*proteinuria detected*". A red callout appears: "NOT IN EVIDENCE."

**VO:** "Here is where most LLM systems would fail in production. The Specialist's first attempt cited a finding — 'proteinuria detected' — that was *not* in the retrieved evidence. A confident hallucination, headed for the field."

### 1:45 – 2:05  ·  THE WINNER MOMENT — RECOVERY

**Visual:** The Verifier hands back to the Optimizer (purple flash). The Optimizer rewrites. The Specialist re-runs. The Verifier turns green. ACCEPT.

**VO:** "The verifier — running an independent prompt with claim-to-evidence entailment — catches it. The optimizer rewrites the prompt with counter-evidence. The specialist re-runs. This time, every claim is grounded in a cited chunk. *Now* the system is allowed to act."

*[Half-second of silence.]*

### 2:05 – 2:30  ·  REAL ACTION — REFERRAL PACKET

**Visual:** The Referral & Facility Agent activates. Tool calls scroll: `lookup_facility_readiness`, `estimate_transport_cost`, `check_voucher_eligibility`. A signed referral packet renders: facility name, distance, ambulance phone, "JSY eligible · public · low cost".

**VO:** "The referral agent finds the nearest *available, maternal-care-capable* facility — open now, fourteen kilometres, public hospital, ambulance phone, JSY voucher eligible. The packet is signed, audit-logged, and ready to share."

### 2:30 – 2:45  ·  EMOTIONAL CLOSE — FAMILY SCRIPT

**Visual:** Phone shows the Hindi family-facing explanation. The mother's hand holds the phone. Audio plays: a warm Hindi voice (external TTS).

**VO (over Hindi audio):** "And then — for the family. Not for a chatbot, not for a clinician. For the husband and mother-in-law in the room. Same facts. Different voice. No scary words. Just: 'going now helps the doctor prevent complications early.'"

### 2:45 – 3:00  ·  CREDIBILITY — AUDIT + GEMMA

**Visual:** Audit log panel opens. Rows: prompt v3, evidence chunks 12/47/89, model version `gemma-4-31b-it-0426`, timestamps. Cut to numbers: "Triage 3 min → 14 s. Referral lead time < 30 min. False-negative Red rate < 2%."

**VO:** "Every prompt, every evidence chunk, every tool call, every model version — logged. Audit-grade by design. MAITRI-Gemma. For two hundred and sixty thousand mothers a year. Built on Gemma 4."

Cut to credits: "Clinical safety reviewed by [OB-GYN advisor]. Workflow input: ASHA worker interviews. Hindi reviewed by [native speaker]. Apache-2.0 · github.com/[org]/maitri-gemma."

---

## 12.B. Live Demo Checklist (5 minutes)

| # | Step | Sec |
|---|---|---|
| 1 | Phone in hand: open MAITRI, show offline indicator and queued case count | 10 |
| 2 | Photograph the antenatal card (printed mock) | 10 |
| 3 | Speak vitals in Hindi (sub-titled live) | 15 |
| 4 | Show the agent trace panel — the seven boxes light up in sequence | 25 |
| 5 | **Hero moment**: Verifier turns red on "proteinuria detected", Optimizer rewrites, Specialist re-runs, Verifier turns green | 45 |
| 6 | Show the Referral & Facility Agent: tool calls + assembled packet | 30 |
| 7 | Show the three outputs — CHW card + Mother explanation + Family explanation | 30 |
| 8 | Open the audit log panel — point to a single row showing prompt version + evidence chunk ids + model version | 20 |
| 9 | (Bonus) Switch language to Bahasa, replay the family explanation | 15 |
| 10 | Q&A buffer | 60 |

If anything breaks in step 5, the demo still works — that is the safety story in motion. *Pre-record the full hero moment as a 60-second backup video.*

---

## Why this v2 demo is stronger than v1

- **One emotional case.** No country-hopping. Lakshmi for 3 minutes.
- **One AI mistake.** Not three. The verifier catches "proteinuria detected" — that is the single line judges remember.
- **One technical signature.** Reject → Optimize → Re-run → Accept. On screen, in red and green.
- **One safety story.** Deterministic safety rules visible *before* the verifier. No hand-waving.
- **One ethical story.** Family explanation, not just mother. CHW context, not "white-savior" composition.
- **One credibility story.** Audit panel open, model version visible, prompt version visible.

The judges' job is to decide which submission to remember on the train home. We are giving them one moment. We name it. We don't dilute it.
