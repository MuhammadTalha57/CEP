# STATE (single source of truth — keep under ~1 page)

**Project:** Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection (CEP_BRIEF.md)
**Constraints:** Python · laptop is CPU-only, 7.4 GB RAM · open-source models only · solo · AWS credit ~$190 · repo public (master)
**Deadline:** Sun 15 Nov 2026 (research paper; extended from 9 Nov). **Last updated:** 14 Nov 2026 (session 4)

## Confirmed requirements
- Attack evaluation (models x minimal apps x injection types) AND a proposed defense AND AWS deployment. Output = research paper.
- The final experiments run against the apps **hosted on AWS**; local runs are for development and the local-vs-cloud comparison.
- LLM calls go through one switchable interface (models/APIs chosen in config).
- Keep paper-ready assets: `paper/facts.md` (page-referenced numbers), `results/` (raw logs), `data/papers/*.json`.

## Stages
| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Scaffold | DONE | |
| 1 | Extract 13 papers | DONE | P01–P13 in data/papers/ |
| 2 | Rank + exclude | DONE | reports/ranking.md; keep 10, exclude P07, P11, P12 |
| 3 | Gap analysis | DONE | G1 + G2 + G3 chosen (12 Nov) |
| 4 | Experiment design + harness | DONE | steps 4.1–4.8 committed; Kaggle pilot run 13 Nov (reports/pilot_kaggle-pilot.md) |
| 5 | Dev runs on Kaggle (user) | IN PROGRESS | pilot DONE; baseline DONE 13 Nov for 3 models (reports/baseline_kaggle.md); qwen3-4b-instruct + H1 add-on next |
| 6 | Defenses + eval | IN PROGRESS | code DONE 13 Nov: D1 detector, D2 sanitize, D3 spotlight, D4 tool policy, layered (steps 6.1–6.5, 92 tests); D5 not built; Kaggle defense runs next |
| 7 | AWS deployment + cloud runs | TODO | same Docker Compose on EC2 |
| 8 | Paper draft | TODO | |

## Schedule (deadline Sun 15 Nov)
Thu 12: approve design, install Ollama, AWS budget alarm + GPU limit check, steps 4.1–4.3 · Fri 13: steps 4.4–4.7, pilot, local runs, defenses · Sat 14: EC2 deploy, full cloud runs, analysis · Sun 15: paper + submit. Cut order: one model -> weakest injection types -> local-only runs. Never cut cloud runs, the deterministic checker or CIs.

## Next actions (max 3)
1. User (Kaggle, one session): fresh notebook from master, attach the previous results zip, MODELS = all 4 (default), DEFENSE="none" -> runs only qwen3-4b-instruct (new, ~1 h est.) + the H1 cells (60 trials per model); then DEFENSE="all" in the same or next session (one or two models per session). Commit each zip. Also: AWS Budgets alert + GPU quota.
2. Claude: Stage 7 AWS deploy guide (EC2 + Docker Compose, cost per hour, stop rules) while the defense runs go.
3. Claude: once defense results are in, defense tables (ASR drop, utility cost, latency, McNemar) in reports/.

## Decisions log
- 31 Oct — Citation counts required; fetched by GitHub Action `Fetch metrics` (OpenAlex, Semantic Scholar, Crossref; GitHub API).
- 31 Oct — P01, P02 are white-box GPU attacks -> related work/taxonomy only.
- 31 Oct — P05 is the closest prior work (same small open models, direct prompts only). Fix its denominator issues; report CIs.
- 31 Oct — P06 gives the AWS blueprint (SageMaker/EC2 endpoint, S3, CloudWatch, gateway block at 0.85); P08 gives the tool-app defense pattern.
- 7 Nov — P13 is the strongest reuse for the RAG app (hidden PDF text, tracer keywords); P10 gives the stats template (Wilson CI + McNemar).
- 7 Nov — Final ranking: P03 80, P08 79, P04 74, P05 62, P01 60, P13 58, P06 50, P02 49, P09 48, P10 43.
- 12 Nov — Scope: G1 + G2 + G3. Cloud-hosted apps are the system under test (user decision, matches the brief's title).
- 12 Nov — OpenCode CLI not used in the harness: its free models only work inside the OpenCode client (OpenCode docs, read 12 Nov), it adds its own agent prompt/tools, and it gives no control over temperature/seed. Ollama is used locally and on EC2 (same model files both places).
- 12 Nov — Laptop: Ryzen 5 7430U, 7.4 GB RAM, no usable GPU -> local models <= 4B quantized, one at a time.
- 13 Nov — Matrix as built: 8 + 14 + 9 attack cells x 30 variants + 90 clean = 1,020 trials per model per defense setting (H1 skipped until the pilot sets h1_technique; if the best technique is T7, H1 stays skipped as a duplicate).
- 13 Nov — Deviations from design.md [OURS]: H2 in App A = payload splitting inside one message (App A has only the user channel); H2 in App C = trigger in the user request + note in the email. App B H2 not used (design listed H1, H3 for B).
- 13 Nov — Defense design details [OURS unless cited]: D1 threshold 0.85 (P06 p4), CPU on Kaggle and AWS, score always logged (threshold analysis offline); D3 does not wrap the user's own message (trusted victim in B/C; App A = system-prompt hardening only); D4 = simplified CaMeL rule (P08 p1, p4): side-effect tool arguments must appear in the user request; layered output guard is deliberately weaker than the scorer (no base64/rot13/reversal) so the scorer is not reused as the defense. Per-app defense lists in configs/experiment.yaml (A: 4 settings, B: 5, C: 5).
- 13 Nov — D5 (self-check) NOT built: needs a second LLM call inside the defense layer and P05 p11 shows weak judges approve up to 49.7% unsafe outputs; dropped for time, reported as a limitation.
- 13 Nov — Pilot (Kaggle, 2x T4, Ollama 0.40.16, Python 3.13, commit f64291d): all 63 trials valid except gemma3-1b App C (no tool support in Ollama -> gemma3-1b is used for Apps A and B only, as planned in models.yaml). The first trial per model included 40–112 s model load, so the pilot's hour estimates were inflated; without it: qwen3-1.7b 0.66 h, llama3.2-3b 0.14 h, gemma3-1b 0.04 h per defense setting. Fix: unlogged warm-up per model (stage5.0).
- 13 Nov — Pilot observation (not a result): llama3.2-3b wrote the attacker's email as text without calling send_email in 3/4 agent attacks -> new flag `target_in_output` (text-only compliance), reported separately; ASR still counts executed tool calls only (design.md §0.2).
- 13 Nov — n stays 30 per cell: GPU time is cheap (~0.9 h per defense setting for 3 models). Proposed: add qwen3-4b (supports tools; same family as qwen3-1.7b, P05 p7 reports 71.3% vs 0% for qwen3:1.7b vs larger models) so App C has 3 models — APPROVED by user 13 Nov.
- 13 Nov — H1 technique cannot be chosen from the pilot (it tested only T2/T7); it is set from the baseline (best of T1–T6@C1 in App B), then H1 cells run as an add-on.
- 13 Nov — Model runs move from the laptop to **Kaggle Notebooks** (free GPU, ~30 GPU h/week reported, 12 h sessions; user decision). Nothing else changes: same Ollama models, trials, temperature 0 and logs. The "local" side of G3 is now the Kaggle notebook (in-process, Ollama native) vs the AWS-hosted app (Docker, HTTP); reported as development vs production deployment. Laptop = code + mock tests only. Free LLM APIs rejected for main runs (rate limits, model versions differ from the Ollama files, seed control).
- 13 Nov — No AI attribution in commits/pushes/PRs (user rule; skills/00-rules.md rule 21).
- 13 Nov — App B naive loader keeps hidden HTML, alt/ARIA, PDF white/tiny text and PDF metadata in the indexed text [OURS, follows P04 p3 / P13 p3 settings]; BM25 top-3; all 10 attack targets retrieve their poisoned doc for all 7 carriers, and all 30 clean questions retrieve their doc (tests).
- 14 Nov — Baseline (Kaggle, commit 772f302): 3,060 valid trials for qwen3-1.7b, llama3.2-3b, gemma3-1b; 0 invalid, 3 errors. Results and findings: reports/baseline_kaggle.md.
- 14 Nov — qwen3-4b runs EXCLUDED: Ollama tag `qwen3:4b` = Qwen3-4B-Thinking-2507 (thinking-only, ignores /no_think, same ID 359d7dd4bcda as `qwen3:4b-thinking-2507-q4_K_M`); 691/1020 outputs empty because hidden reasoning used up max_tokens=300 -> ASR falsely ~0. Files moved unchanged to results/excluded/. Replacement: `qwen3-4b-instruct` = `qwen3:4b-instruct-2507-q4_K_M` (pinned tag, non-thinking). Note: a later checkpoint than P05's qwen3:4b, so not comparable to P05 p7. Guard added: run.py warns when >20% of outputs are empty; notebook records `ollama list` digests.
- 14 Nov — qwen3-1.7b (hybrid model, /no_think works) still gave ~4% empty single-call answers that stop at ~2.5 s (likely occasional thinking runoff). Kept as is (counted as failed attack / failed utility), reported as a limitation; changing its settings now would break comparability with the finished baseline.
- 14 Nov — h1_technique = T4 (best of T1–T6@C1 pooled over 3 models, 47/90 = 52%; T7@C1 49%). H1@C2 and H1@C5 run as an add-on (resume skips finished trials).
- 14 Nov — C4 zero-width carrier ~0% ASR (1/90; H3 0/90) with the poison retrieved every time: a finding (invisible characters break tokens for small models), not a bug.
- 12 Nov — Approved 13 Nov: 3 apps as HTTP API only (chatbot, RAG, tool agent), techniques T1–T7 x carriers C0–C9 + hybrids H1–H3, defenses D1–D5 + layered; temperature 0 with 30 payload variants per cell. Details: reports/design.md.

## Session start prompt
"Read STATE.md, skills/00-rules.md and the file named in Next actions from github.com/MuhammadTalha57/CEP (branch master). Do only the Next actions. Update STATE.md at the end and tell me exactly which files to commit."
