# Maitri

Safety verified maternal referral co pilot built on Gemma 4.

Maitri is a seven agent decision support tool for community health workers in low connectivity districts. A worker submits a patient snapshot from an antenatal visit and Maitri returns a risk tier, a clinic ready referral packet, and a warm explanation for the mother and family. Every claim the model produces is checked by an independent verifier before it leaves the system. Every call is logged to an append only audit trail.

The hero moment is the verifier rejection recovery loop. The system produces a realistic medical hallucination, the verifier catches it against retrieved evidence, the optimizer rewrites the prompt, the system recovers, and a safe referral packet is delivered. The same loop runs on every case, not only in the demo.

## What Gemma 4 does

Two models cover six agent roles.

The reasoning model handles the Specialist, Verifier, Optimizer, and Referral and Facility agents. It performs chain of reasoning with native function calling for facility lookup, gestational age calculation, voucher eligibility, and drug safety lookup.

The light multimodal model handles the Intake and Formatter agents. Intake reads an antenatal card image and normalizes a structured patient snapshot. Formatter produces three parallel outputs for the community health worker, the mother, and the household decision maker.

A seventh agent is a deterministic Python rule block. It cannot use a language model. It can only promote a risk tier upward. It exists so the system fails safe under model error.

## Why multi agent

Each agent reduces one named risk. Intake reduces missing field risk. Retrieval reduces unsupported knowledge risk. Specialist reduces contextual reasoning gap. Safety Rules reduces dangerous under triage. Verifier reduces hallucinated claim risk. Optimizer reduces a stuck reasoning path. Referral and Facility reduces wrong destination risk. Formatter reduces unsafe communication.

## Run locally

```
make install
make smoke
make test
make dev
```

The smoke target makes one live call to the reasoning model and confirms credentials and routing. The dev target opens the Gradio interface on a local URL.

## Project documents

Design rationale lives in OVERVIEW, ARCHITECTURE, FLOWCHART, EVALUATION, DEMO_SCRIPT, REPO_STRUCTURE, TECH_STACK, KAGGLE_STRATEGY, and JUDGE_CRITIQUE. The build stage stays in src.

## Submission tracks

Main Track, Safety and Trust Impact Track, Ollama Special Technology Track.

## License

Apache 2.0 on code. Models retain their original licenses.
