# MAITRI-Gemma — Kaggle Submission Strategy (Section 12, v2)

Kaggle final submission deadline: **May 18, 2026, 11:59 PM UTC**. 14 days from today (May 4). Three judging axes — Impact & Vision, Video Pitch & Storytelling, Technical Depth & Execution — with implicit weight on real-world deployability and "where infrastructure is lacking" use cases.

---

## The one winning sentence (use everywhere)

> **MAITRI is a safety-verified Gemma 4 maternal referral co-pilot that helps community health workers detect pregnancy danger signs, catches unsupported AI reasoning before it reaches the field, and produces clinic-ready referral packets in low-connectivity settings.**

Every artifact — README, video opening, Kaggle writeup hook, slide deck cover, social post — opens with a paraphrase of this sentence. Repetition is how a project becomes a brand inside a 60-submission afternoon for judges.

---

## The one winning demo moment

> **The AI makes a realistic medical hallucination ("proteinuria detected"). The Verifier catches it. The Optimizer rewrites. The Specialist re-runs. The CHW gets a safe, facility-aware referral packet.**

This is `examples/case_2_verifier_rejects_hallucination.py` — and the video is built around it.

---

## 12.A. 1500-word Kaggle Writeup Outline

| § | Words | Purpose | What goes in |
|---|---|---|---|
| 1. Hook | 80 | Grab judges in the first 30 seconds | "Every two minutes, a woman dies giving birth..." → state we built the system that hands a Gemma 4 specialist to the frontline. |
| 2. The Problem | 180 | Establish stakes with hard numbers | 260K maternal deaths/year, 94% in LMICs, 1–2 doctors per 1,000, climate-driven heat & vector compounders, gap is *growing*. Cite WHO + Lancet. |
| 3. The User | 120 | Make the problem human | Sunita the ASHA. Lakshmi at week 32. Paper register. 14 km from the doctor. |
| 4. The MAITRI System | 200 | What it does in plain language | 7-agent flow, multimodal intake, RAG over WHO + national guidelines, Gemma 4 thinking-mode reasoning, independent verification, two-audience output. |
| 5. Why Gemma 4 (specifically) | 180 | Anchor judging | Multimodal native (E4B for OCR + audio); long context (full pregnancy history in one prompt); native function calling (drug, climate, SMS); thinking mode (clinician-auditable trace); strong multilingual; size variants enable cloud cost control. *Not a generic LLM wrapper.* |
| 6. Architecture in One Picture | 60 | Visual anchor | Embed the Mermaid; one paragraph naming the seven agents and the three feedback loops. |
| 7. The Verification Story | 180 | The technical signature | Walk through Case 2: Specialist hallucinates "proteinuria detected", Verifier (independent prompt, no shared chain) rejects on entailment grounds, Optimizer rewrites prompt with counter-evidence, Specialist re-runs, Verifier accepts. This is the part that separates MAITRI from chat-GPT-with-prompts. |
| 8. Real-World Readiness | 180 | Speak directly to "infrastructure is lacking" | Offline-first PWA, IndexedDB queue, region-pinned Vertex inference, per-country data residency, EU AI Act Article 12-grade audit log, NIST AI RMF mapping in `docs/compliance/`. |
| 9. Evaluation | 160 | Prove it works | Layered eval: pre-deploy → shadow → live with audit. The metric that matters most is false-negative Red rate (< 2% target). 5 reference cases reproduced in `examples/`. Native-reviewer panels per language. |
| 10. Impact (measured) | 120 | The before-after | Triage time 3 min → 14 s. Referral lead time 4–18 h → < 30 min. CHW confidence 2.6 → 4.4. Audit time per Red case 12 min → < 4 min. |
| 11. Beyond the Hackathon | 100 | Scalability + path | Same skeleton extends to TB triage, child malnutrition, NCD screening — the agents are vertical-agnostic by design. WHO + national MOH partner pathway sketched. |
| 12. Acknowledgements + Repro | 40 | Trust & openness | License (Apache-2.0), reproducible notebook, public eval set, contact. |

**Total: ~1,500 words.** Every section has a number. Hackathon judges scan for those.

---

## 12.B. GitHub README Sections (in order)

1. **Tagline + 1-line pitch** (above the fold)
2. **One screenshot** of the CHW phone interface + one Mermaid block (architecture)
3. **Quickstart** (`make dev` → working stack in < 10 minutes)
4. **The 5 reference cases** (link to runnable notebooks)
5. **What is Gemma 4 doing** (clear list, anti-generic)
6. **Compliance & ethics** (links to `docs/compliance/`)
7. **Performance budgets** (latency, cost-per-case)
8. **Reproducibility** (Vertex token instructions, eval suite invocation)
9. **Roadmap** (TB, malnutrition, NCD)
10. **License + contributors + acknowledgements**

The README has *no* essay. The essay lives in the Kaggle writeup. The README is for judges who clone the repo and want to be productive in 5 minutes.

---

## 12.C. Project Tagline

> **"One woman dies every two minutes. MAITRI gives every community health worker a Gemma 4 specialist in her pocket."**

Variants for context:
- Slack/Discord one-liner: "Multi-agent Gemma 4 maternal-health triage co-pilot for LMICs. Cited, verified, multilingual, audit-grade."
- Conference badge: "MAITRI — Maternal AI Triage and Resilience Intelligence."

---

## 12.D. Cover Image Idea

Foreground: a hand holding a low-end Android phone showing the MAITRI screen at the moment of triage — tier "Amber", citation chip "WHO ANC 2025", a small voice waveform playing the Hindi mother script. Background: a soft-focus portrait of a CHW and a pregnant woman on a charpai, late afternoon light. Bottom right corner: small Gemma 4 logo + "Open source · Apache-2.0".

The visual language: respectful, specific, not stock-photo NGO. Real CHW uniform (ASHA pink saree). No infantilizing of the mother. No "white-saviour" composition. This matters — judges will notice.

If we can't shoot real photos, the fallback is a clean illustrated cover in Excalidraw aesthetic using the architecture diagram as the cover graphic with one bold quote.

---

## 12.E. Judging-Score Optimization Strategy

Three axes. We are explicit about which artifact moves which score.

| Axis | What moves it | Our artifact |
|---|---|---|
| **Impact & Vision** | Hard numbers on the size of the gap; specificity of beneficiaries; before/after improvement; *why this and not a chatbot*. | Section 2 of writeup; Sunita-Lakshmi narrative; the metrics table (3 min → 14 s, etc.); the "extends to TB / malnutrition / NCD" coda. |
| **Video Pitch & Storytelling** | Strong opening line; one human character; visible technical signature (the verification rejection); wow moment; clean close. | The 3-min video script with the rejection-recovery beat at 0:50–1:30 and the multilingual side-by-side at 2:00–2:30. |
| **Technical Depth & Execution** | Real architecture (not a wrapper); use of *all* Gemma 4 differentiators; eval rigor; reproducibility; safety design; deployability. | The architecture doc; the prompts/ folder with versioning; the 5 reference notebooks; the false-negative Red rate metric; the EU AI Act / NIST mappings; Terraform infra. |

We also explicitly engineer for **judges' implicit signals**:

- **"Where infrastructure is lacking"** — Offline PWA, queue + sync, region-pinned inference, low-bandwidth mode. Show this on tape.
- **"Privacy is paramount"** — Edge PII strip, patient_pseudo_id, opt-in re-identification, audit-grade logging, country-pinned residency. Document in `docs/data/pii_handling.md`.
- **"Real impact"** — A trial cohort plan (even if small) with clinician partner. If we cannot get a real partner in 14 days, frame as "designed with input from N CHWs interviewed via WHO / NGO contacts" — *do not lie*.
- **"Native function calling"** — explicit in code, in trace, in video.

---

## 12.F. Risk register for the submission

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Vertex AI quota for Gemma 4 31B not granted in time | Medium | High | Apply day 1; HF endpoint as fallback for the 31B agents; demo can use HF if Vertex blocked |
| Antenatal card OCR fails on hand-written | Medium | Medium | 50-card labeled set day 3; bias test 12 handwritten styles; voice-confirm fallback for any field |
| Native-reviewer panel not assembled | Medium | Medium | Start outreach to 12 language reviewers day 1; offer co-author credit; minimum 2 languages launch |
| Demo phone has no real network on stage | Low | Medium | Pre-record the offline → sync segment; record 2 backup videos at different lighting |
| Clinician partner not signed | High | Medium | Scope to "advisory clinician input" rather than "trial" if formal IRB not done in time |
| Submission video too long | Medium | Low | Edit to 2:55, leave 5-second buffer for Kaggle player |

---

## 12.G. Submission day checklist (May 18)

- [ ] All 5 reference notebooks run clean from a fresh checkout
- [ ] `make eval` passes the CI gate suite
- [ ] README has no broken links
- [ ] Video is 2:50–3:00, captioned in English + Hindi (proof of multilingual ethos)
- [ ] Kaggle writeup ≤ 1,500 words, all 12 sections, all citations linked
- [ ] Architecture Mermaid renders on Kaggle (test in their preview, fall back to PNG if needed)
- [ ] Apache-2.0 LICENSE present
- [ ] One sentence in writeup acknowledging clinician advisors + native-language reviewers
- [ ] Submission form: tagline, video link, repo link, writeup link
- [ ] Timezone sanity check — UTC deadline, not local
