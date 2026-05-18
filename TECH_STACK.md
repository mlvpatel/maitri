# MAITRI-Gemma — Best Dev Option + Tech Stack

This document gives you the answer to "best dev option, choose the best tech stack" — explicitly, with the trade-offs named, and tuned for a 14-day hackathon submission that judges can clone, run, and trust.

---

## 1. The recommended dev option

**Build a lean working core that runs end-to-end on day 9, then polish for the demo.**

Concretely: ship the smallest version of the full pipeline that demonstrates the hero loop (verifier rejection → recovery → safe referral packet) in real time, on real Gemma 4 calls, against real (small) data. Mock everything that is not the hero. Document mocks as roadmap.

### Why this option, not the others

| Option | What it gives | Why it's wrong for this hackathon |
|---|---|---|
| A) Build full enterprise infra (Terraform, Postgres, Qdrant Cloud, Grafana, GitHub Actions matrix) | Looks production-ready | Judges clone the repo and find half-built infra. Trust drops. Time gone. |
| B) Build a pretty UI and fake the agents | Polished demo | Judges read the code, see prompt-prompt, and downgrade Technical Depth |
| **C) Lean working core, real Gemma calls, mocked external services (recommended)** | Hero loop on tape, real prompts, real eval | Best score across all three judging axes; shippable in 14 days |
| D) Push novelty (custom fine-tune, novel agent framework) | Stands out for technical judges | Risky — fine-tuning Gemma 4 in 14 days with no GPU budget is a disaster |

### What "lean" means in practice

- One CHW form (not five flows).
- One reference district (Saharsa, Bihar).
- Two languages (English + Hindi). Bahasa as bonus only if days 13–14 buffer holds.
- One reviewer dashboard (read-only).
- Five reference cases, all runnable in `examples/`.
- Mocks: SMS (console), TTS (pre-generated audio file), climate API (static JSON snapshot), facility readiness (committed JSON).
- *No* Terraform, *no* Postgres, *no* Redis, *no* k8s, *no* Grafana, *no* multi-region, *no* OAuth flow beyond a stub.

### What "working core" means

End-to-end: a CHW form submit → 7 agents run → real Gemma 4 calls → audit row written → CHW sees the verified result with the referral packet. The hero loop runs on real prompts against real Gemma. The verifier really catches the hallucination. The optimizer really rewrites. None of this is faked.

---

## 2. The tech stack — chosen, with the alternative considered

For each layer: my pick, what I considered and rejected, and why.

### 2.1 Frontend — CHW PWA

| Pick | **React 18 + Vite + Tailwind CSS + Workbox PWA** |
|---|---|
| Why | React is the lowest skill-ramp for a 14-day team; Vite gives instant HMR; Tailwind keeps CSS out of the way; Workbox is the most reliable offline-first toolkit for PWAs |
| Considered | Next.js (overkill, App Router slows dev), Svelte/Solid (smaller team familiarity), Flutter (mobile-first but adds a build target) |
| Risk | None significant — this is the most-traveled path |

### 2.2 Frontend — Reviewer dashboard

| Pick | **Same React app, separate route + role guard** |
|---|---|
| Why | One bundle, one auth boundary; no second deploy target |
| Considered | Standalone Next.js dashboard | Two stacks = two CI pipelines = wasted day |

### 2.3 Backend — API layer

| Pick | **FastAPI (Python 3.12) on Google Cloud Run** |
|---|---|
| Why | Async-native, Pydantic-native (matches the agent message contracts), OpenAPI 3 generated, fastest path from local to public URL |
| Considered | Node/Hono (smaller cold start but agents are Python); LiteLLM proxy (overkill) |
| Risk | Cloud Run cold starts on first call after idle — mitigated with min-instances = 1 during the demo window |

### 2.4 Agent framework

| Pick | **LangGraph** |
|---|---|
| Why | Deterministic state machine matches the safety-first design. Native streaming. LangSmith traces are free for the demo and they record every prompt + tool call (audit-grade for free). The orchestrator is *not* an LLM call — it's a real FSM. |
| Considered | CrewAI (too LLM-routed for safety-critical), AutoGen (powerful but heavier ceremony), Custom (would steal a week) |
| Risk | LangGraph version churn — pin a known-good version |

### 2.5 Gemma 4 inference

| Pick | **Vertex AI Model Garden** for Gemma 4 31B (reasoning + verifier) **+ Hugging Face Inference Endpoints** for Gemma 4 E4B (intake + formatter) |
|---|---|
| Why | Vertex gives region-pinned private endpoints with predictable pricing for the 31B reasoning agents; HF is faster to provision for the smaller E4B variant and cheaper at low QPS |
| Considered | Vertex-only (single-vendor risk + provisioning lag); HF-only (region pinning weaker for production story); Self-hosted via vLLM (requires GPU + serving infra — wrong scope) |
| Risk | Vertex quota approval can take days for new orgs — apply day 1; HF endpoint as fallback for the 31B if Vertex blocked |

### 2.6 Speech-to-text (STT) — for CHW voice

| Pick | **Faster-Whisper (open) running locally during dev; Google Cloud STT vendor for the deployment** |
|---|---|
| Why | We do **not** claim Gemma performs production STT. STT is an external pipeline. Faster-Whisper is small, free, and accurate enough for Hindi/Bahasa demos. |
| Considered | AssemblyAI (vendor lock + cost), Deepgram (good but adds another vendor), Gemma 4 audio (not production-grade for our languages) |

### 2.7 Text-to-speech (TTS) — for mother + family voice

| Pick | **Coqui XTTS-v2 (open) for Hindi and English; pre-generate audio in dev for the demo** |
|---|---|
| Why | Multilingual, free, runs on a single CPU. For the demo we pre-generate the Hindi family explanation so the playback is instant on stage. |
| Considered | Google Cloud TTS (good but adds vendor), Eleven Labs (best quality but expensive + license issues for clinical use) |

### 2.8 Vector / RAG

| Pick | **LanceDB (embedded, file-backed)** with `bge-m3` embeddings and BM25 hybrid |
|---|---|
| Why | Zero infra. Embedded inside the Python process. Hybrid search out of the box. Production migration to Qdrant is a one-config swap. |
| Considered | Qdrant Cloud (great but adds an external service for hackathon), pgvector (would force Postgres into the MVP), Chroma (less performant on hybrid), FAISS (no hybrid) |
| Risk | LanceDB is newer than Qdrant — small ecosystem risk, but for a 200-chunk corpus it is more than enough |

### 2.9 Reranker

| Pick | **Cohere Rerank v3 (vendor) OR `BAAI/bge-reranker-v2-m3` (open)** — choose Cohere for stable demo, open if budget is zero |
|---|---|
| Why | Reranking lifts retrieval recall by 10–15 points cheaply. Worth the API call. |
| Considered | None within budget |

### 2.10 Database

| Pick | **SQLite (single file) for MVP** |
|---|---|
| Why | Zero infra. Append-only audit table fits perfectly. Migration to Postgres is one DSN change post-hackathon. |
| Considered | Postgres (overkill for hackathon), DuckDB (analytics-flavored, not transactional) |

### 2.11 Audit log storage

| Pick | **SQLite append-only table for MVP** + JSONL file mirror as a "WORM-like" artifact for the demo |
|---|---|
| Why | The judges should *see* an immutable artifact. The JSONL file makes the WORM story tangible without needing actual S3 Object Lock for the hackathon. |
| Post-hackathon | Postgres + S3 Object Lock |

### 2.12 Function-calling tools

| Pick | **Native Gemma 4 function calling** wrapping plain Python functions |
|---|---|
| Tools shipped | `lookup_facility_readiness(gps, capability_required)`, `estimate_transport_cost(origin, dest, time)`, `check_voucher_eligibility(patient, scheme)`, `lookup_drug_safety_in_pregnancy(drug_name)`, `compute_gestational_age(lmp_date)`, `query_climate_risk(geo, week)` |
| Why | Native function calling is one of Gemma 4's signature features. Showcasing it is a Technical Depth signal. |

### 2.13 Climate / facility data

| Pick | **Static committed JSON snapshots in `data/`** |
|---|---|
| Why | Live API integrations add demo failure surface. JSON is reproducible. Anyone can clone and run. |
| Files | `data/facilities/saharsa_facility_readiness.json` (6 facilities), `data/climate/saharsa_may2026_snapshot.json` (heat index, dengue activity, malaria risk) |

### 2.14 Observability

| Pick | **LangSmith for traces** (free tier) + a single console-printed audit summary on every case |
|---|---|
| Why | LangSmith makes the agent trace browsable for judges; the console summary is a fallback if LangSmith account is unavailable |
| Considered | OpenTelemetry + Grafana — post-hackathon |

### 2.15 Deployment

| Pick | **`gcloud run deploy` for backend + `vercel deploy` (or Cloud Run) for frontend** |
|---|---|
| Why | Two commands, two URLs, public in 60 seconds. No Terraform. |
| Considered | Terraform-managed multi-region — post-hackathon |

### 2.16 CI/CD

| Pick | **One GitHub Actions workflow**: `lint → unit → eval-5-cases → build` |
|---|---|
| Why | Single file, single failure point. The eval-gate badge in README is a credibility signal. |
| Considered | Multi-workflow matrix — wasted complexity for hackathon |

### 2.17 Local dev experience

| Pick | **`docker compose up`** boots LanceDB seed + FastAPI + the React PWA + a tiny mock STT/TTS stub. **`make demo`** runs the 5 reference cases sequentially and prints the audit summary. |
|---|---|
| Why | Judges who clone the repo are productive in < 10 minutes. That alone moves the Technical Depth score. |

---

## 3. The full v2 stack at a glance

```
┌────────────────────────────────────────────────────────────────────────┐
│  CHW PWA (React + Vite + Tailwind + Workbox)                           │
│   IndexedDB queue · offline-first · 360x640 + 2GB RAM target           │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼  HTTPS / OAuth2 stub
┌────────────────────────────────────────────────────────────────────────┐
│  FastAPI (Python 3.12) on Google Cloud Run                             │
│   Pydantic schemas · OpenAPI 3 · LangSmith tracer · per-tenant rate    │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  LangGraph deterministic FSM orchestrator                              │
│   ├── 1. Intake Agent      →  Gemma 4 E4B (HF Inference)               │
│   ├── 2. Retrieval Agent   →  LanceDB hybrid + bge-m3 + Cohere Rerank  │
│   ├── 3. Risk Specialist   →  Gemma 4 31B (Vertex)  + native fn-calls  │
│   ├── 4. Safety Rules      →  Pure Python deterministic                │
│   ├── 5. Verifier Agent    →  Gemma 4 31B (Vertex, independent prompt) │
│   ├── 6. Optimizer Agent   →  Gemma 4 31B (Vertex)                     │
│   ├── 7. Referral & Fac.   →  Gemma 4 31B (Vertex) + native fn-calls   │
│   └──    Formatter Agent   →  Gemma 4 E4B (HF Inference)               │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  External pipelines (honestly labeled)                                 │
│   STT: Faster-Whisper / Google Cloud STT  (NOT Gemma)                  │
│   TTS: Coqui XTTS-v2                       (NOT Gemma)                 │
│   SMS: console mock for hackathon          (Twilio post-hackathon)     │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│  Audit & Storage                                                        │
│   SQLite append-only audit table + JSONL mirror (WORM-style)           │
│   data/facilities/saharsa_facility_readiness.json (committed mock)     │
│   data/guidelines/  (200 chunks, WHO + RMNCH+A)                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 4. What we explicitly do NOT build for the hackathon

| Skipped | Why | Where it lives in roadmap |
|---|---|---|
| Postgres + Redis | Audit fits in SQLite; Redis adds infra | `docs/roadmap.md` — production migration |
| Qdrant Cloud | LanceDB sufficient for 200 chunks | Same — one-config swap |
| Twilio SMS | Console mock proves the agent's tool call | Post-hackathon partner integration |
| Live climate API | Static snapshot is reproducible | NASA POWER + OpenDengue post-hackathon |
| Multi-region Vertex | Single region for demo | Region-pinned per-LMIC for production |
| Terraform | `gcloud run deploy` is two commands | IaC for production |
| Grafana | LangSmith trace + console summary suffices | OpenTelemetry pipeline post-hackathon |
| OAuth full flow | Stub is enough for demo CHW + reviewer | Production identity (Auth0 / Workforce Identity) post-hackathon |
| Live trial | IRB out of scope in 14 days | Trial design documented in `docs/operations/trial_design.md` |

This list is not weakness — it is *scope discipline*. We document each one as roadmap, not as a missing feature.

---

## 5. The cost ceiling for the demo

Rough back-of-envelope per case at 1M cases/month with caching:

| Component | Per-case |
|---|---|
| Gemma 4 31B (Specialist + Verifier + Optimizer + Referral) — ~3K tokens prompt + ~1K tokens output × 3-4 calls | $0.012 |
| Gemma 4 E4B (Intake + Formatter) — ~2K + ~1K × 3 generations | $0.005 |
| LanceDB + bge-m3 embed (cached) | $0.000 |
| Cohere rerank | $0.001 |
| STT (Faster-Whisper on CPU) | $0.000 |
| TTS (Coqui XTTS-v2 on CPU) | $0.000 |
| Cloud Run + SQLite | $0.001 |
| **Total** | **~$0.019** |

We will publish the actual measured cost from the demo period in the writeup with a Vertex pricing screenshot. *That* is what makes the cost claim trustworthy.

---

## 6. The one paragraph for the writeup

If you only have one paragraph for the tech-stack section of the Kaggle writeup, use this:

> MAITRI-Gemma is built as a lean, end-to-end working system. The CHW interface is an offline-first React PWA. The orchestrator is a deterministic LangGraph state machine — not an LLM router — so safety paths are statically verifiable. The seven agents are Python modules with Pydantic-typed I/O. Six of them call Gemma 4 (Vertex AI for the 31B reasoning + verification + referral agents; HF Inference Endpoints for the E4B intake + formatter); the seventh is a pure-Python deterministic Safety Rules block. Retrieval uses an embedded LanceDB hybrid index over a 200-chunk WHO + India RMNCH+A corpus. Speech-to-text and text-to-speech are external pipeline components — we do not claim Gemma performs production audio. The audit log is an append-only SQLite table mirrored to a JSONL artifact (WORM-style for the hackathon, S3 Object Lock for production). The five reference cases are runnable from a single `make demo` against a real Vertex deployment.

---

## 7. The "if you only build five things" priority list

1. **The verifier rejection-recovery loop** working on Case 2, on real Gemma calls, on tape. (This is the demo.)
2. **The deterministic safety rules block** unit-tested on textbook red flags.
3. **The Referral & Facility Agent** with the committed `saharsa_facility_readiness.json` and a signed packet output.
4. **The Hindi family explanation** generated by the Formatter and rendered with pre-generated TTS audio.
5. **The audit log panel** showing one row with prompt version + evidence chunk ids + model version + tool call args.

If days 13–14 are tight, drop *everything else* before you drop these five.
