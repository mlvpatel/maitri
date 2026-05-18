# MAITRI-Gemma — Repo Structure (Section 10, v2)

This is the **lean MVP repo layout** we will publish — scope-disciplined for a 14-day build. Each file/folder is justified, and we explicitly mark what is `MVP-build`, `mock`, or `roadmap-only`.

```
maitri-gemma/
├── README.md                       # Project overview, tagline, hero signature
├── ARCHITECTURE.md                 # Multi-agent design (this repo's design doc)
├── FLOWCHART.md                    # Mermaid + Excalidraw diagrams
├── DEMO_SCRIPT.md                  # Single-hero-case 3-min video script + live demo checklist
├── EVALUATION.md                   # Eval framework + 5 runnable reference cases
├── KAGGLE_STRATEGY.md              # Submission strategy + judging-score plan
├── JUDGE_CRITIQUE.md               # Self-critique + v2 resolutions
├── REPO_STRUCTURE.md               # This file
├── TECH_STACK.md                   # Chosen dev option + tech stack
├── LICENSE                         # Apache-2.0
├── pyproject.toml                  # Python deps (uv-managed)
├── docker-compose.yml              # Local dev: LanceDB seed + FastAPI + PWA + STT/TTS stubs
├── Makefile                        # `make dev`, `make eval`, `make demo`
├── .github/
│   └── workflows/
│       └── ci.yml                  # lint → unit → eval-5-cases → build (single workflow)
│
├── src/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── base.py                 # Agent interface, message contract
│   │   ├── intake.py               # 1. Vision + text parser (Gemma 4 E4B)
│   │   ├── retrieval.py            # 2. LanceDB hybrid + Gemma rerank
│   │   ├── specialist.py           # 3. Risk Triage Specialist (Gemma 4 31B)
│   │   ├── safety_rules.py         # 4. Deterministic safety rules (PURE PYTHON, no LLM)
│   │   ├── verifier.py             # 5. Independent verification (claim ↔ evidence)
│   │   ├── optimizer.py            # 6. Per-call prompt rewriter
│   │   ├── referral_facility.py    # 7. Referral & Facility Agent (Gemma 4 31B + tools)
│   │   ├── formatter.py            # CHW + Mother + Family outputs (Gemma 4 E4B)
│   │   └── orchestrator.py         # LangGraph FSM, NO Gemma calls
│   │
│   ├── tools/
│   │   ├── facility_lookup.py      # reads data/facilities/*.json
│   │   ├── transport_cost.py       # estimates km × rate, monsoon multiplier
│   │   ├── voucher_check.py        # JSY / PMMVY / MAA eligibility logic
│   │   ├── drug_safety.py          # pregnancy drug lookup (RxNorm + WHO Essential)
│   │   ├── climate_query.py        # reads data/climate/*.json snapshot
│   │   ├── gestational_age.py      # LMP / fundal height calculator
│   │   ├── sms_referral.py         # MOCK: prints to console (Twilio post-hackathon)
│   │   └── escalation.py           # writes to reviewer queue table
│   │
│   ├── rag/
│   │   ├── ingest.py               # Chunk + embed WHO + national guidelines
│   │   ├── lancedb_client.py       # Hybrid BM25 + dense (bge-m3 + Cohere Rerank)
│   │   └── corpus_metadata.csv     # Versioned chunk metadata (no PDFs committed)
│   │
│   ├── api/
│   │   ├── main.py                 # FastAPI app, OpenAPI 3
│   │   ├── routers/
│   │   │   ├── case.py             # POST /case, GET /case/:id
│   │   │   ├── audit.py            # GET /audit/:id (clinician-only, signed)
│   │   │   └── reviewer.py         # Clinician dashboard endpoints (read-only)
│   │   ├── auth.py                 # OAuth2 STUB for hackathon
│   │   ├── pii.py                  # Edge-side strip & hash to patient_pseudo_id
│   │   └── audit_log.py            # Append-only SQLite + JSONL mirror (WORM-style)
│   │
│   ├── ui/
│   │   ├── chw-pwa/                # React + Vite + Tailwind, Workbox offline
│   │   │   ├── src/
│   │   │   ├── public/manifest.webmanifest
│   │   │   └── service-worker.ts
│   │   └── reviewer-dashboard/     # Same React app, separate route + role guard
│   │
│   ├── prompts/
│   │   ├── intake_v1.md
│   │   ├── retrieval_query_rewrite_v1.md
│   │   ├── specialist_v1.md
│   │   ├── verifier_v1.md
│   │   ├── optimizer_v1.md
│   │   ├── referral_facility_v1.md
│   │   ├── formatter_chw_v1.md
│   │   ├── formatter_mother_hindi_v1.md
│   │   ├── formatter_mother_en_v1.md
│   │   └── formatter_family_hindi_v1.md   # NEW in v2 — household decision-maker script
│   │
│   ├── schemas/
│   │   ├── patient_snapshot.py
│   │   ├── evidence_pack.py
│   │   ├── risk_assessment.py
│   │   ├── verification_verdict.py
│   │   ├── referral_packet.py             # NEW in v2 — facility/cost/voucher
│   │   └── deliverable.py                 # CHW + Mother + Family + audit_id
│   │
│   └── safety/
│       ├── deterministic_rules.py  # BP ≥ 160/110 → Red, etc.
│       ├── refusal_classifier.py
│       └── pii_redactor.py
│
├── tests/
│   ├── unit/
│   │   ├── test_intake.py
│   │   ├── test_retrieval.py
│   │   ├── test_specialist.py
│   │   ├── test_safety_rules.py    # 100 textbook red-flag cases
│   │   ├── test_verifier.py
│   │   ├── test_optimizer.py
│   │   ├── test_referral_facility.py  # closed/incapable facility skip
│   │   ├── test_formatter.py
│   │   └── test_orchestrator_fsm.py
│   ├── integration/
│   │   ├── test_end_to_end.py
│   │   ├── test_offline_sync.py    # MVP: simulated, not real network
│   │   └── test_hindi_outputs.py
│   ├── adversarial/
│   │   ├── poisoned_outputs.json   # 100 deliberate hallucinations
│   │   ├── unsafe_queries.json     # 30 refusal cases
│   │   └── prompt_injection.json
│   └── fixtures/
│       ├── antenatal_cards/        # 50 photos (synthetic + anonymized)
│       └── reference_cases.json    # The 5 reference cases
│
├── eval/
│   ├── harness.py                  # Runs full suite locally and in CI
│   ├── metrics.py                  # Tier accuracy, false-neg Red, p95
│   ├── reports/                    # Auto-generated nightly + on-demand
│   └── notebooks/
│       └── reproduce_kaggle.ipynb  # The notebook judges run end-to-end
│
├── examples/                       # The 5 RUNNABLE reference cases (v2 naming)
│   ├── case_1_happy_path.py
│   ├── case_2_verifier_rejects_hallucination.py
│   ├── case_3_safe_refusal.py
│   ├── case_4_hindi_family_explanation.py
│   └── case_5_offline_queue_mock.py
│
├── data/
│   ├── facilities/
│   │   └── saharsa_facility_readiness.json   # 6 facilities, includes closed + incapable test cases
│   ├── climate/
│   │   └── saharsa_may2026_snapshot.json     # Heat / dengue / malaria / AQI snapshot
│   └── guidelines/
│       └── _README.md                        # No PDFs in repo; loader pulls from versioned URLs
│
├── docs/
│   ├── compliance/
│   │   ├── eu_ai_act_article12_control_mapping.md   # PER-OBLIGATION → file:line
│   │   ├── nist_ai_rmf.md
│   │   └── iso_42001_alignment.md
│   ├── ethics/
│   │   ├── bias_assessment.md
│   │   └── consent_model.md
│   ├── data/
│   │   ├── corpus_provenance.md     # Where each guideline came from + license
│   │   └── pii_handling.md
│   ├── operations/
│   │   ├── runbook.md
│   │   ├── failure_modes.md         # Failure-day catalog with screenshots
│   │   └── trial_design.md          # Designed-for-trial doc; trial out of scope for hackathon
│   └── roadmap.md                   # Postgres, Qdrant, Twilio, Terraform, multi-region — explicitly post-hackathon
│
└── (no infra/ folder — Terraform is post-hackathon roadmap; deployment is `gcloud run deploy`)
```

## Why each top-level folder exists

| Folder | Purpose | What a judge will check |
|---|---|---|
| `src/agents/` | One file per agent. Mirrors the architecture doc 1:1. | Naming consistency between doc + code |
| `src/tools/` | All function-call targets, isolated for easy mocking | Whether tools really fire (real Gemma function calling) |
| `src/rag/` | Ingest + retrieval. No PDFs in repo (license + size). | Provenance documentation |
| `src/api/` | FastAPI surface + audit log + PII edge strip | OpenAPI spec + the audit row format |
| `src/ui/` | The PWA + clinician dashboard | Whether it actually runs offline |
| `src/prompts/` | Versioned prompts. Promotion gated by eval. | Versioning discipline; family explanation prompt present |
| `src/schemas/` | Pydantic message contracts | Schema-first design |
| `src/safety/` | Deterministic safety + refusal | Whether safety is bolted on or designed in |
| `tests/` | Unit + integration + adversarial | Coverage + adversarial set |
| `eval/` | The reproducibility story | The notebook runs end-to-end on a Vertex token |
| `data/` | Committed JSON for facility + climate; guideline metadata only | Provenance + license |
| `examples/` | The 5 runnable reference cases | Easiest path for judges to validate the demo |
| `docs/compliance/` | EU AI Act *control mapping* — file:line per obligation | Whether compliance is real or theater |
| `docs/operations/failure_modes.md` | Failure-day catalog | Honesty signal — wins safety axis |

## Naming discipline

- Every prompt is suffixed with a version (`specialist_v1.md`).
- Every Pydantic schema lives next to the agent that produces it.
- Every test file mirrors the source path.
- No prompt is referenced by string-literal in code — only `prompts.load("specialist", "v1")`.
- The five reference cases have *runnable* file names (no spaces, lowercase, snake_case) so a judge can `python examples/case_2_verifier_rejects_hallucination.py` immediately.

## What we explicitly do NOT have in this repo (and why)

| Missing | Why |
|---|---|
| `infra/terraform/` | Post-hackathon roadmap. Documented in `docs/roadmap.md`. |
| Postgres migration | SQLite is sufficient for MVP audit log. |
| Qdrant Cloud client | LanceDB embedded is sufficient for 200 chunks. |
| Real Twilio integration | Console mock for hackathon; real integration in roadmap. |
| Real climate API client | Static snapshot is reproducible; live API post-hackathon. |
| OAuth full provider | Stub for hackathon; production identity post-hackathon. |
| K8s manifests | Cloud Run is one command. K8s post-hackathon. |
| Grafana dashboards | LangSmith trace + console summary suffices for MVP. |

This list is the *roadmap* document, not a missing-feature catalog. Documenting what is intentionally out-of-scope is itself a credibility signal.
