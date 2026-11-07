# Gap analysis (Stage 3, skills/03)

Input: data/papers/*.json of the 10 kept papers only: P01, P02, P03, P04, P05, P06, P08, P09, P10, P13 (P07, P11, P12 excluded). Every number carries paper id and PDF page. `[INFERENCE]` marks my reasoning. Page refs come from the JSONs, whose quotes were machine-checked for P09-P13 only; P01-P08 pages were not re-verified this session.

## A. Injection type x paper coverage

| Injection type | Papers covering it (page) | Notes |
|---|---|---|
| Direct override (ignore-previous, escape chars, fake completion, combined, command override) | P01 (p8), P05 (p8), P10 (p3) | P09 and P06 only use labelled prompt datasets/detectors, no model ASR |
| Persona / jailbreak | P05 (p8, 74 prompts), P10 (p3), P06 (p6, detector labels) | |
| Indirect: web/HTML markup carriers in RAG | P04 (p3) | generator LLM unnamed |
| Indirect: PDF hidden text and metadata | P13 (p3) only | one fixed payload |
| Indirect: RAG-persisting learned trigger | P02 (p9) | simulated, white-box |
| Tool-output / agent injection | P08 (p1) only | closed models only |
| White-box optimized | P01 (p8), P02 (p1) | needs GPU, out of our scope |
| Multi-turn | none; P10 states single-turn limit (p5) | [INFERENCE] not checked in the P01-P04, P08 PDFs |

## B. Model x paper (ASR actually measured on a model)

| Paper | Models | Open and small (<=14B)? | Attack setting |
|---|---|---|---|
| P05 | phi3 3.8b, Mistral 7b, DeepSeek-R1 1.5b/7b, Llama3.2 1b/3b, qwen3 1.7b/4b, gemma3 1b/4b (p1) | yes | direct prompts, 165 prompts, no CIs |
| P13 | Llama-3 8B, Gemma-3 (size NOT FOUND), Qwen-3 8B, Meditron 7B, MedLlama-2 7B, Phi-4 14B (p4-5) | yes | PDF hidden text, one payload, 100 docs per cell |
| P01 / P02 | Mistral-7B, OpenChat-3.5, Llama-2/3 (p6 / p2) | yes | white-box optimization |
| P10 | GPT-4o-mini, Llama-3.1-8B (p4) | one of two | persona attacks, n=80 |
| P04 | generator NOT FOUND | unknown | RAG web carriers |
| P08 | six closed models (p7) | no | AgentDojo tools |
| P09 | Qwen-4B/7B/14B (p8) | yes | throughput only, no ASR |

[INFERENCE] Only P05 and P13 measure ASR on small open models, and they never share an app type. Family overlap exists (Gemma, Qwen, Llama, Phi), but sizes and attacks differ, so their numbers are not comparable. Ordering still flips: in P05 qwen3:1.7b (71.3%) is above gemma3:1b (62.8%) on direct prompts (p7); in P13 Gemma-3 (96.33%) is far above Qwen-3 (29.33%) on PDF injection (p5). Sizes differ, so this only motivates the question.

## C. Metric definitions (what "success" means)

| Paper | Success / metric | Uncertainty reported? |
|---|---|---|
| P01 | ASR, PAC (judge picks attacker target; definition not extracted, Sec 4.1.4) | not found in JSON |
| P02 | ExeAcc, binary execution success | not found |
| P03 | AUC, TPR at fixed FPR (p7) | threshold tuned on test data (stated limitation) |
| P04 | IPI ASR via automatic detector, P 0.92 / R 0.89 / F1 0.90 / kappa 0.84 on 1200 generations (p3) | 95% CIs (p3) |
| P05 | human-judged vulnerability rate (p7, p12); denominators inconsistent (91 vs 94; 74 vs completed runs) | none |
| P06 | precision / recall / F1, DistilBERT F1 does not match its P and R | none |
| P08 | task utility, successful attacks, token overhead (p7) | not found |
| P09 | Acc / P / R / F1 at detector level (p10) | mean +/- std over five seeds (p10) |
| P10 | pre-specified failure signals, same rule for both agents (p3) | Wilson CIs, McNemar (p4) |
| P13 | tracer keywords "septic shock" / "meropenem" (p5) | none; one trial per document |

## D. Reported numbers (setting-labelled). All cross-paper comparisons are NOT COMPARABLE (rule 4)

| Paper | Number | Setting (p) |
|---|---|---|
| P05 | injection vulnerability 71.3 / 62.8 / 34.0 / 30.9 / 0% (qwen3:1.7b, gemma3:1b, DeepSeek-R1:1.5b, Llama3.2:1b, six larger) | 91 direct prompts, no defence (p7) |
| P05 | best defence 1.2% (Self-Defence); Input Filtering weakest, Llama3.2 3B ~42% | 165 prompts x 6 models x 5 defences (p10) |
| P13 | mean ASR 47.78%; Gemma-3 96.33, Llama-3 61.00, Phi-4 56.00, MedLlama-2 35.33, Qwen-3 29.33, Meditron 8.67 | PDF vectors, 2,400 trials (p1, p5) |
| P04 | macro ASR Vanilla 24.9 -> All defenses 4.7; utility -1.8 / -2.2 pp for Sanitized / Normalized | benchmark, 95% CIs (p3) |
| P10 | GPT-4o-mini 28.75 -> 26.25% (p=0.75); Llama-3.1-8B 26.25 -> 18.75% (p=0.26) | 80 prompts, persona attacks (p4) |
| P08 | 77% vs 84% task success; 2.82x input tokens | AgentDojo, closed models (p1, p11) |
| P03 | TPR@FPR1%: 94.80 / 43.22 / 12.78% (Llama-3.1-8B, DeBERTa-184M, PromptGuard) | detector benchmark (p9) |
| P01 | manual attacks ASR 7.3-16.3% vs 90.8% optimized | MT-Bench, Mistral-7B (p8, p3) |

## E. Candidate gaps (<=3 proposed; ranked by evidence strength, feasibility, value)

### G1. No paper tests the same small open models across direct, RAG-document and tool-output injection with one success checker and CIs (RECOMMENDED)
- **Evidence:** P05 covers six small open models but direct prompts only, no CIs, inconsistent denominators (p1, p7; flags). P13 covers six open models but only PDF hidden text, one payload, one run per document (p1, p5). P04 covers RAG carriers but the generator is unnamed (p3). P08 covers tools but only closed models (p1, p7). Absent across the 10 kept papers: any evaluation of one model set over all three app types.
- **Why it matters:** this is exactly the brief: models x minimal apps x injection types, with success reported. It also fixes the denominator and CI problems listed in STATE.
- **Testable here (no GPU, open small models)?** Yes: Python harness, deterministic checks (P13 tracer style, P10 failure signals), Wilson CIs (P10 p4). Size the model count and trials after a timing pilot on our machine; I do not yet have our own timing logs. [INFERENCE] P10 shows n=80 gives intervals about 18-20 points wide (28.75%: 20.0-39.5, p4), so per-cell n must be larger than that to separate models.
- **Risk:** the matrix grows fast; cut models or injection types before trials per cell.

### G2. No defense is evaluated end-to-end on small open models in RAG and tool apps with utility and latency cost
- **Evidence:** P13 evaluates no defense, only names visual sanitization as future work (p6). P04's defenses cost -1.8 / -2.2 pp answerability (p3) but on an unnamed generator. P08's 77% vs 84% and 2.82x tokens are on closed models (p1, p11). P03 reports detector TPR@FPR (94.80% for the 8B detector, 43.22% for DeBERTa-184M, p9), not in-app ASR; P05 tests only direct prompts, where Input Filtering was weakest (~42%, p10).
- **Why it matters:** the brief requires a proposed defense and evaluating its effect.
- **Testable?** Yes on CPU for pieces we can afford: hidden-text/metadata sanitizer (P04 + P13 vectors), the public 184M DeBERTa detector family (P03 p8-9; heavier 8B detector is not CPU-feasible [INFERENCE]), and a tool-policy / instruction-data separation pattern (P08 design). Report ASR before/after, clean-task utility, latency, with CIs.

### G3. No paper measures whether cloud hosting (serving stack, gateway, sampling settings) changes ASR for the same model
- **Evidence:** P06 deploys a detector on AWS but reports only classification F1 (p4-6). P09 emulates edge-cloud on one workstation (p8). P10 compares a cloud API and a local model but they are different models (GPT-4o-mini vs Llama-3.1-8B, p4), so deployment is confounded with model. Absent across the other kept papers: same model, different deployment.
- **Why it matters:** the brief title says cloud-hosted; AWS deployment is Stage 7.
- **Testable?** Partly. [INFERENCE] Needs an AWS CPU instance and quantized 1-4B models; this is the riskiest item with 2 days left. Cheaper form: run the G1 harness locally and on the AWS instance for one model and compare, instead of a full second matrix.

### Considered, not proposed
- White-box optimized attacks (P01, P02): need GPU; cite as related work.
- Multi-turn attacks: absent in the kept papers' JSONs (P10 p5 states the limit), feasible, but adds a dimension we cannot afford now.
- Adaptive detection scheduling (P09) and privacy-preserving audit: GPU/simulation or excluded paper; off the brief.

## F. Recommendation for the scope cut [INFERENCE]
Take G1 as the core contribution, G2 as the defense required by the brief, and treat G3 as a single-model AWS check (reuse P06's blueprint: S3, SageMaker, CloudWatch, p4-5). If time runs short, cut G3 to a deployment note, then reduce models, never the CIs or the success checker.

**User picks:** which of G1/G2/G3 to commit to, and the cut line.
