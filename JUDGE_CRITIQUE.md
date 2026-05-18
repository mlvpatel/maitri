# MAITRI-Gemma — Judge-Level Critique and Improvements (Section 13, v2)

> **v2 status:** Most issues raised in the v1 critique are now resolved in the design. See "v2 resolution log" at the bottom of this file for the per-issue status.

---


This is me reviewing MAITRI as a hackathon judge who has just watched 60 generic chatbot pitches and is openly skeptical of any "AI for good" claim. I am looking for the seams — and proposing specific, executable fixes.

---

## 13.A. What is weak

### W1. The "advisory clinician" gap is real, and judges can smell it

The strongest version of this submission has at least one *named* OB-GYN clinician on the credit slide and one CHW partner organization (WHO, BRAC, ARMMAN, mHealth Kenya, Living Goods, etc.) — even informally. Without this, the project reads like "thoughtful engineers built a thing." The Vision axis is hard-capped without it.

### W2. The dataset story is thin

We are bootstrapping from synthetic antenatal cards. Judges familiar with health AI will know that handwriting variance, ink fade, water damage, cropping under low light, and partial visibility of fields make OCR brittle. A plausible 50-card labeled set is the floor; 200 with documented inter-annotator agreement is the bar.

### W3. "Refer to nearest clinic" is the wrong fallback in many districts

In parts of LMICs the nearest clinic is closed at night, has no obstetrician, or has supplied-out medications. A "safe fallback" that recommends a closed clinic is unsafe. The Retrieval Agent must include a *facility readiness* feed (Healthsites.io has it; some MOHs publish it; some don't).

### W4. We have not addressed two of the cruelest realities in maternal health

- **Cost of referral**: a Red triage that sends a poor mother to a paid hospital can be financially catastrophic. The system silently externalizes that. We should at minimum surface cost-of-referral context and known voucher/scheme eligibility.
- **Domestic decision power**: in many regions the husband/mother-in-law decides whether the woman goes. The mother voice script that says "Beti, today we will go" assumes Sunita can negotiate that. A version of the script aimed at the *family* (not the mother alone) is needed.

### W5. The verifier may be a co-conspirator

Two prompts on the same model can collude. A real verifier would ideally be a *different* model family or at least a *different* checkpoint with structurally different prompts. With Gemma 4 only, the safest bet is: different prompt template, different temperature, mandatory entailment by an explicit NLI utility (not the generative model). We mention this; we should *measure* it.

### W6. Latency budget is optimistic for cold paths in LMIC regions

p95 ≤ 8s assumes a warm path. Cold-start in `africa-south1` against Vertex (when available) is realistically 12–25s. We should publish a *cold* p95 number and a *first-token* number so judges can't snipe the optimistic claim.

### W7. The compliance moat is also a liability if mis-stated

EU AI Act doesn't directly apply to a CHW app deployed only in India. Saying "EU AI Act high-risk classification" without nuance can read as compliance theater. The honest framing is "we adopt EU AI Act Article 12 logging discipline as a *standard* — even where not legally required — because health AI deserves it."

---

## 13.B. What is generic

### G1. "Multi-agent" by itself is hackathon-bingo

Almost every submission this year will say "multi-agent." What separates MAITRI is the *verifier-rejection-recovery* loop being on-camera in the demo. We must make this the technical signature — every artifact (writeup, video, README) should foreground it. The flowchart already does. The video does. The eval frames it. Anchor the README on it.

### G2. The Mermaid is fine but generic

A judge sees ten Mermaid flowcharts a week. Our Mermaid is honest but won't itself win points. The Excalidraw / hand-drawn version with the verification reject path *highlighted* is what gets remembered. Use that as the cover image.

### G3. "Cited" is overused and underpowered

Every RAG pitch says "cited." The differentiator is *what happens when the citation fails* — the EVIDENCE_INSUFFICIENT short-circuit. Show that explicitly in Case 2 of the eval.

### G4. The wow moment is good but can be stronger

"Same case, three languages" is good. The stronger version is **"same case, three languages, *the verifier catches a different hallucination in each*"** — proving the safety mechanism is language-aware. If we can demonstrate that, it is a 10x story.

---

## 13.C. What may fail

### F1. Gemma 4 31B function-calling reliability under load

Native function-calling has rough edges at high concurrency in some early API releases. Burn a day on stress testing with synthetic load; document failure modes; have the deterministic rule layer absorb a class of failures.

### F2. Multilingual back-translation is hard for low-resource languages

Hausa back-translation may lose nuance. The "back-translation equivalence" check could itself produce false positives on safety-relevant nuances. Mitigation: in Hausa/Yoruba/Bahasa, require *human native-speaker* confirmation in the early launch period; use back-translation as a *signal*, not a gate.

### F3. The audit log can leak PII unintentionally

If the Specialist's rationale uses the mother's name verbatim (because it was in the prompt), the audit log will hold names. Mitigation: PII redactor at the audit-write boundary (we listed it; we have to *test it adversarially*).

### F4. Demo video too polished — judges suspect VFX

If the trace panel looks too clean, judges will assume it's a mock. Show real wall-clock timing. Show one real glitch. Authenticity > polish.

### F5. Ambient noise destroys voice intake in field

We tested in a quiet room. A real CHW visit has children, hens, motorcycles. We need a noise-robustness eval and a deliberate "voice intake fails → fall back to typed structured form" path.

---

## 13.D. What is not impressive enough

### N1. The compliance section is currently a list of acronyms

`docs/compliance/eu_ai_act_mapping.md` should not be a list of articles. It should be a per-article *control mapping* — for each Article 12 obligation we list which file enforces it (`src/api/audit_log.py: line 42`). This is what auditors do, and it is a moat very few hackathon teams can produce. *It happens to be your daily job — lean on it.*

### N2. There is no UX research signal

Even one transcript from a CHW interview in the writeup ("When we asked Sunita Devi what she most needs, she said: 'I want to know if it is dangerous, in 30 seconds, in my language.'") moves the Vision score visibly. If we cannot interview a real CHW in 14 days, find a published study (Frontiers in Public Health has many) and quote it with citation.

### N3. The cost story is missing

A "USD 0.02 per case at 1M cases/month" claim with a back-of-envelope calculation and a screenshot from Vertex pricing is enormously persuasive. Without it, judges treat the claim as aspirational.

### N4. There is no failure-day story

Pitches that say "we never fail" lose. We should publish a one-page *failure mode catalog*: what happens on Vertex outage, what happens on Qdrant outage, what the CHW sees, what the audit row looks like. Honesty wins on the safety axis.

---

## 13.E. How to make it more unique

### U1. Lead with the verifier reject. Always.

In the README, in the video, in the cover image. The reject-and-recover is the part that no other team will have, because most teams will use a single specialist and call it a day. Make that loop the brand.

### U2. Anchor on a specific district

Don't say "Bihar." Say **"Saharsa district, Bihar."** Pull real public health data for that district. Quote the maternal mortality ratio for Saharsa specifically. Specificity is felt as competence.

### U3. Publish a "diagnosis dictionary" PR template

Open the door for native speakers to contribute idiomatic complaint-to-clinical translations. Open-source community in the loop is a hackathon-judge favorite.

### U4. Add a one-button "explain this to a doctor" mode

The CHW taps once and gets a 30-second voice explanation she can play to a remote doctor over WhatsApp call. This is low-effort to build and visibly delightful in demo.

### U5. Show the audit log as a feature, not a footnote

In the demo, *open* the audit log panel for one case after a referral. Show the immutable timeline: every prompt, every model version, every tool call, signed. Judges who care about deployability will star the repo immediately.

---

## 13.F. How to make the demo emotionally strong

1. **Open with silence**, then the "every two minutes" line. No music. Music starts only when MAITRI's screen lights up.
2. **Use real names** (synthetic but realistic — Lakshmi, Sunita, Aman). Anonymity reads as distance; named characters read as care.
3. **Show the mother's hands holding the phone for the voice clip.** She is the real user, not a passive subject.
4. **One quiet beat at 1:50**: after the verifier rejects, half a second of dead air, then the green ACCEPT chime. The pause sells the safety story.
5. **Closing image**: Sunita walking back down the path with the phone in her shirt pocket. The system is invisible again — as it should be. Cut to the credits.

---

## 13.G. How to make the technical architecture credible

1. **Publish prompts.** Real, versioned, in `src/prompts/`. Hide nothing.
2. **Publish the eval set.** Public 200-case subset. Hide nothing.
3. **Publish the cold p95 honestly.** Hide nothing.
4. **Publish the failure-day catalog.** Hide nothing.
5. **Have one named clinician advisor.** Even one. Real names.
6. **Map every safety control to a file:line.** The compliance doc is a control mapping, not an essay.
7. **Run the eval suite in CI on every PR.** Show the GitHub Actions badge in README.
8. **Do not invent a metric.** Every metric is operationalized in code in `eval/metrics.py`.

---

## 13.H. The five concrete additions that move us from "good submission" to "win-tier"

| # | Addition | Day | Owner |
|---|---|---|---|
| 1 | One named OB-GYN advisor + 1 NGO partner LOI | 1–4 | Outreach |
| 2 | EU AI Act Article 12 *control mapping* doc (not a list) | 6 | You — your daily job |
| 3 | A failure-day catalog (`docs/operations/failure_modes.md`) with screenshots | 9 | Eng |
| 4 | The Saharsa-district-specific framing in writeup + video | 12 | Story |
| 5 | A "verifier catches a different hallucination per language" demo segment in Case 4 | 11–12 | Eng + Story |

These five — done — push the Impact and Technical scores past the 90th percentile of submissions.

---

## 13.I. The one risk I would lose sleep over

**A Red case is missed because of a verifier false-accept on a hallucinated proteinuria claim.** If that happens in front of judges, in field, or in a real deployment, it is a story that ends the project. The mitigation is the deterministic safety rule layer (a Red can always be promoted, never demoted) AND mandatory clinician audit on every Red AND a published false-negative Red rate. We have all three on paper. We must have all three in code by day 9.

---

## 13.J. v2 resolution log (May 4, 2026)

| v1 issue | Status | How resolved in v2 |
|---|---|---|
| W1 — Missing clinician/advisor signal | Pending → in plan | README.md "Honest readiness signal" table; KAGGLE strategy day-1 outreach |
| W2 — Thin dataset story | In plan | EVALUATION.md fixture target raised; data/guidelines/_README.md sets corpus size |
| W3 — "Refer to nearest clinic" is unsafe | **Fixed** | All references now read "nearest available, maternal-care-capable facility"; Referral & Facility Agent enforces it; data/facilities/saharsa_facility_readiness.json includes a closed-facility test case |
| W4 — Cost of referral + family decision power | **Fixed** | Referral packet includes `cost_level` + `voucher_eligibility`; Formatter now produces a Family explanation prompt (`formatter_family_hindi_v1.md`) |
| W5 — Verifier may collude with Specialist | **Mitigated** | Verifier uses independent prompt template + different system message + NLI entailment utility; ARCHITECTURE.md 3.5 explicit |
| W6 — Cold p95 optimistic | Documented | EVALUATION.md L4 cold-start metric added; KAGGLE strategy commits to publish actual cold p95 |
| W7 — EU AI Act overclaim | **Fixed** | Now framed as "Article 12 logging *discipline* — adopted as a standard, not a legal claim where not in jurisdiction" |
| G1 — "Multi-agent" is bingo | **Fixed** | Verifier-rejection-recovery is now the named brand signature; appears in README hero, video, demo, eval Case 2 |
| G2 — Mermaid is generic | **Fixed** | v2 Mermaid + Excalidraw highlight Verifier (purple, bold), Safety Rules (orange, bold), and Escalation (red, bold) |
| G3 — "Cited" overused | **Fixed** | EVIDENCE_INSUFFICIENT short-circuit explicit in flowchart + Case 2 |
| G4 — Wow moment can be stronger | **Refocused** | Single hero case is now the wow; multilingual is a bonus segment, not the main act |
| F1 — Function-calling reliability under load | Plan | Day-12 stress test on roadmap |
| F2 — Multilingual back-translation hard | Acknowledged | Native speaker review required for Hindi launch; back-translation is a signal, not a gate |
| F3 — Audit log PII leak | **Fixed** | PII redactor at audit-write boundary; adversarial test added |
| F4 — Demo too polished | **Fixed** | DEMO_SCRIPT.md now calls for one real glitch + half-second pause at the verifier reject |
| F5 — Ambient noise destroys voice | **Mitigated** | STT is external pipeline; typed-form fallback documented in failure modes |
| N1 — Compliance is acronym soup | **Fixed in repo plan** | `docs/compliance/eu_ai_act_article12_control_mapping.md` — per-obligation file:line mapping |
| N2 — No UX research signal | In plan | KAGGLE strategy includes outreach to ASHA-supporting NGOs day 1 |
| N3 — Cost story missing | **Fixed** | TECH_STACK.md Section 5 has per-case back-of-envelope; promise to publish measured cost with Vertex screenshot |
| N4 — No failure-day story | **Fixed** | `docs/operations/failure_modes.md` is committed scope |
| U1 — Lead with verifier reject | **Fixed** | Done in README + DEMO + KAGGLE + Excalidraw |
| U2 — Anchor on a specific district | **Fixed** | Saharsa, Bihar everywhere; `data/facilities/saharsa_facility_readiness.json` committed |
| U3 — Open diagnosis-dictionary PR template | Backlog | Post-hackathon |
| U4 — "Explain to a doctor" mode | Backlog | Post-hackathon |
| U5 — Audit log as feature | **Fixed** | Audit panel in demo step 8; DEMO_SCRIPT.md beat 2:45–3:00 |
| Diagram fix 1 — "seven-agent" mismatch | **Fixed** | Now explicitly "six Gemma-powered + deterministic safety rules" OR "seven agents (with Referral & Facility Agent)" — both consistent |
| Diagram fix 2 — "cloud-only" weakens offline story | **Fixed** | Now reads "Offline-first PWA + cloud Gemma inference" |
| Diagram fix 3 — Gemma E4B + TTS overclaim | **Fixed** | Formatter labelled "text only — TTS is external" |
| Diagram fix 4 — "OCR + audio" overclaim | **Fixed** | Intake labelled "photo/form + transcript* — STT external" |
| Diagram fix 5 — "Clinician within 24h" unsafe | **Fixed** | Replaced with "IMMEDIATE SAFE ESCALATION + parallel clinician review" everywhere |
| Diagram fix 6 — Missing deterministic safety rules | **Fixed** | Now a first-class node between Specialist and Verifier in Mermaid + Excalidraw + sequence diagram |
| Diagram fix 7 — Missing Referral & Facility Agent | **Fixed** | Real seventh agent added with its own section in ARCHITECTURE.md (3.7), node in flowchart, tool calls in sequence diagram |
| Diagram fix 8 — Reject loop not dramatic | **Fixed** | Verifier + Optimizer now bold-purple "HERO LOOP" in Excalidraw and Mermaid; demo script calls for half-second pause at the reject |

The remaining "Pending" / "In plan" / "Backlog" items are time-bound — clinician/advisor outreach starts day 1 of the build, post-hackathon items are documented as roadmap.
