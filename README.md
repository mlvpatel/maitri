# Maitri

> Safety verified maternal referral co pilot built on Gemma 4.

Maitri is a seven agent decision support tool for community health workers in low connectivity districts. A worker submits a patient snapshot from an antenatal visit. Maitri returns a clinical risk tier, a clinic ready referral packet for the nearest open and capable facility, a warm message in the mother's language, a separate message for the household decision maker, and an immutable audit trail.

The defining feature is the verifier rejection recovery loop. The Specialist agent drafts a risk assessment with cited claims. An independently prompted Verifier agent checks every claim against the retrieved evidence. If any claim is unsupported the Optimizer agent writes a short rewrite directive and the Specialist runs again. Only the verified draft reaches the field. The same loop runs on every case, not only in the demo.

## Live links

- Public live demo: https://huggingface.co/spaces/mlvptl/maitri-demo
- Source code: https://github.com/mlvpatel/maitri

## What Gemma 4 does

Two Gemma 4 models cover six agent roles.

- `google/gemma-4-31B-it` for the Specialist, Verifier, Optimizer, and Referral and Facility agents. Heavyweight reasoning with native function calling.
- `google/gemma-4-26B-A4B-it` for the Intake and Formatter agents. Sparse MoE, cheaper, multilingual.

A seventh agent is intentionally not a language model. It is a deterministic Python rule block that promotes a risk tier upward toward red whenever a hard medical threshold is crossed. It cannot promote downward. It exists so the system fails safe under model error.

## Architecture in one diagram

```
[ free text + structured fields ]
            |
            v
        Intake  ────────────────► PatientSnapshot
            |
            v
        Retrieval  ────────────► EvidencePack
            |
            v
        Specialist  ───────────► RiskAssessment (claims, cites)
            |
            v
    Deterministic Safety Rules ─► promoted tier upward only
            |
            v
        Verifier  ─────────────► VerificationVerdict
            |  rejected                 |  accepted
            v                           |
        Optimizer  ───hint──► Specialist (one rewrite max)
                                          |
                                          v
                                      Verifier (final)
                                          |
                                          v
                              Referral and Facility ──► ReferralPacket
                                          |
                                          v
                                      Formatter ─────► CHW card, mother HI, family HI
                                          |
                                          v
                                   Deliverable + Audit
```

## Measured results

- Verifier evaluation on a six case adversarial set: precision 1.0, recall 1.0, F1 1.0.
- Deterministic safety rule block: nine unit tests covering severe hypertension, severe and moderate anemia, antepartum bleeding, pre eclampsia symptom cluster, age extremes, fever, reduced urine, and a regression test that the block cannot demote a tier.
- Hero case live run: eight audit calls, staged hallucination caught on first verifier pass, rewrite accepted on second pass, Saharsa District Hospital selected over the closer but incapable primary health centre, Hindi messages emitted with the JSY voucher named.

## Run locally against hosted Gemma 4

```
make install
make smoke
make test
make dev
```

Smoke makes one live call and confirms credentials. Test runs the unit suite. Dev opens the Gradio interface on a local URL.

Set `HF_TOKEN` in the `.env` file. Models default to the two listed above and can be overridden with `GEMMA_REASONING_MODEL_ID` and `GEMMA_LIGHT_MODEL_ID`.

## Run offline against Ollama

This is the low connectivity story. Same seven agent pipeline, locally hosted Gemma 4 weights, no network, no token, no cost.

```
make ollama-pull
export MAITRI_PROVIDER=ollama
make demo-offline
```

`make ollama-pull` downloads `gemma4:e4b`. For higher quality reasoning on a GPU machine, also pull `gemma4:26b` or `gemma4:31b` and set `OLLAMA_REASONING_MODEL` accordingly.

## Submission tracks

Main Track, Safety and Trust Impact Track, Ollama Special Technology Track.

## Repository layout

```
src/maitri/        seven agent implementations, orchestrator, shared client, audit log, schemas
src/maitri/tools/  six native function callable tools
src/maitri/rag/    evidence corpus and keyword retriever
src/maitri/safety/ deterministic safety rules
tests/             unit tests and adversarial set
eval/              eval harness and reports
examples/          five runnable reference cases
data/              committed facility and climate snapshots for the demo district
scripts/           one shot deploy and smoke scripts
app.py             gradio interface
```

## Project documents

- `ARCHITECTURE.md` — multi agent design and the risk each agent reduces
- `OVERVIEW.md` — long form project overview anchored on Saharsa district
- `FLOWCHART.md` — diagrams
- `TECH_STACK.md` — tech choices and trade offs
- `EVALUATION.md` — eval methodology
- `KAGGLE_WRITEUP.md` — submission writeup, kept under fifteen hundred words
- `VIDEO_SCRIPT.md` — three minute screen capture script
- `YOUTUBE_ASSETS.md` — title, description, tags, upload checklist

## License

Apache 2.0 on code. Models retain their original licenses.
