# Maitri, a safety verified maternal referral co pilot on Gemma 4

## The one sentence the judges should remember

Maitri is a seven agent maternal triage system in which an independent Gemma 4 verifier rejects unsupported medical claims before they ever reach the community health worker.

## The problem

In 2023 roughly two hundred and sixty thousand women died from causes related to pregnancy and childbirth. One woman every two minutes. Ninety four percent of those deaths were in low and middle income countries. In Saharsa district of Bihar, India, the district we anchor this submission on, a frontline accredited social health activist carries a paper antenatal card and a low end Android phone. There is one functioning maternal care facility within reach, often ten to twenty kilometres away. The worker has no decision support, no facility readiness data, no audit trail, and no way to communicate triage urgency to the household decision maker.

A naive language model assistant would help, but it would also hallucinate. A hallucinated drug dose in a pre eclampsia case is not a typo. It is a path to harm.

## What Maitri does

A community health worker submits a patient snapshot. Within roughly thirty seconds Maitri returns a clinical card in English with a tier of green, amber, or red, a warm message in Hindi for the mother and a separate one for the household decision maker, a facility specific referral packet with phone and capability, and an immutable audit trail with the prompt versions, the evidence chunk identifiers, the model versions, and every tool call argument.

The defining moment of the system is the verifier rejection recovery loop. The Specialist agent produces an initial draft. An independently prompted Verifier agent checks every cited claim against the retrieved evidence. If any claim is unsupported, the Optimizer agent writes a short rewrite directive and the Specialist runs again. Only the verified draft moves on to the Referral and Facility agent and the Formatter. The same loop runs on every case, not only in the demo.

## Where Gemma 4 lives in the pipeline

Two Gemma 4 models cover six agent roles. The reasoning model handles the Specialist, the Verifier, the Optimizer, and the Referral and Facility agents. It is a heavyweight model used for chain of reasoning with native function calling. The light multimodal model handles the Intake and Formatter agents. It is faster and cheaper and is the right tool for the structured extraction and the multilingual generation work.

A seventh agent is intentionally not a language model. It is a deterministic Python rule block that promotes a risk tier upward toward red whenever a hard medical threshold is crossed. Severe hypertension at or above one hundred and sixty over one hundred and ten, antepartum bleeding, severe anemia below seven grams per decilitre, the pre eclampsia symptom cluster, and reduced fetal movement after twenty eight weeks all trigger a deterministic promotion. The rule block cannot promote downward. It exists so that the system fails safe in the case of model error.

Native function calling is used in two agents. The Specialist agent can call a gestational age calculator, a drug safety lookup, and a climate risk query. The Referral and Facility agent can call a facility readiness lookup, a transport cost estimator, and a voucher eligibility check. Each function is a plain Python function wrapped in a JSON schema. The orchestrator dispatches the calls and feeds the results back to the model so the next turn can act on them.

## Technical execution

The orchestrator is a deterministic state machine. It contains no language model calls. The agent order is intake, retrieval, specialist, deterministic safety rules, verifier, optionally optimizer and specialist rerun once, post optimizer safety re evaluation, referral and facility, formatter. This shape lets a reader of the code verify the safety properties of the system without running it.

Retrieval is over a small evidence corpus drawn from the World Health Organization recommendations on antenatal care, the FIGO position on pre eclampsia, and the Indian Ministry of Health RMNCH plus A guidelines. Each evidence chunk has a stable identifier and the Specialist must cite chunk identifiers in every medically substantive claim. The Verifier checks that the cited chunks actually entail the claim, with special attention to numerical specifics like doses and thresholds.

The audit log is append only. Every agent call is written to a SQLite table that exposes no update or delete entry point, and mirrored to a JSON Lines file so a judge can read the immutable artifact directly without a SQLite client.

The interface is a Gradio application deployed to Hugging Face Spaces. The verifier rejection moment is rendered as a red banner that names the unsupported claim identifier and shows the optimizer hint that was used for the rewrite. The audit summary panel exposes the run identifiers for inspection.

## Measured results

The verifier was evaluated on a hand crafted adversarial set of six assessments. Five contained one deliberately unsupported claim mirroring realistic hallucination patterns. One contained only supported claims. The verifier achieved precision one, recall one, and an F1 of one on this set. Median latency was about fourteen and a half seconds, ninety fifth percentile about sixteen and a half seconds. The deterministic safety rule block passes nine unit tests covering severe hypertension, severe and moderate anemia, antepartum bleeding, the pre eclampsia symptom cluster, age extremes, fever, reduced urine, and a regression test that the block cannot demote a tier.

A live end to end run on the demo hero case produced eight audit calls, caught the staged hallucination on the first verifier pass, accepted the rewrite on the second pass, picked Saharsa District Hospital over a closer but incapable primary health centre, and emitted a Hindi family message that named the Janani Suraksha Yojana voucher.

## What is honestly not in scope

We did not run a live clinical trial. We did not commit any patient data, real or synthetic, that contains identifiers. Speech to text and text to speech are external pipeline components and the writeup does not claim that Gemma 4 performs production grade audio. The Hindi outputs were reviewed for register and tone but were not audited by a clinician for this submission. The roadmap documents the path from these honest limits to a deployable pilot in partnership with an accredited frontline programme.

## Tracks and submission assets

This submission is entered for the Main Track, the Safety and Trust Impact Track, and the Ollama Special Technology Track. The Ollama path is a fallback for the Intake and Formatter agents using a locally hosted Gemma 4 instance, which addresses the low connectivity story directly.

The public code repository is at github.com slash mlvpatel slash maitri. The public live demo is at huggingface.co slash spaces slash mlvptl slash maitri-demo. The three minute video is linked in the media gallery. A cover image and supporting screenshots are attached.

## Why this can save a life

The verifier is the difference between a confident wrong answer and a verified one. The deterministic safety rules are the floor that holds when both the Specialist and the Verifier err. The audit log is what makes the system reviewable after the fact. The facility readiness lookup is what makes the referral physically possible. The Hindi family message is what makes the transport decision happen in the household, not only in the clinic. These are not features. They are the components of a system that can be trusted by a worker who is far from a doctor.
