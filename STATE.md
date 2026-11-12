# STATE (single source of truth — keep under ~1 page)

**Project:** Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection (CEP_BRIEF.md)
**Constraints:** Python · laptop is CPU-only, 7.4 GB RAM · open-source models only · solo · AWS credit ~$190 · repo public (master)
**Deadline:** Sun 15 Nov 2026 (research paper; extended from 9 Nov). **Last updated:** 13 Nov 2026 (session 4)

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
| 4 | Experiment design + harness | DONE (code) | design.md approved 13 Nov; steps 4.1–4.7 committed, 62 tests pass with the mock model; Docker image built and smoke-tested. Real-model pilot not run yet |
| 5 | Local runs (user) | TODO | pilot first (deploy/README.md §2), then reduced-n runs |
| 6 | Defenses + eval | TODO | D1–D5 + layered (design.md §5) |
| 7 | AWS deployment + cloud runs | TODO | same Docker Compose on EC2 |
| 8 | Paper draft | TODO | |

## Schedule (deadline Sun 15 Nov)
Thu 12: approve design, install Ollama, AWS budget alarm + GPU limit check, steps 4.1–4.3 · Fri 13: steps 4.4–4.7, pilot, local runs, defenses · Sat 14: EC2 deploy, full cloud runs, analysis · Sun 15: paper + submit. Cut order: one model -> weakest injection types -> local-only runs. Never cut cloud runs, the deterministic checker or CIs.

## Next actions (max 3)
1. User: install Ollama, pull qwen3:1.7b, llama3.2:3b, gemma3:1b, run the pilot (deploy/README.md §1–2), commit reports/pilot_local-pilot.md + results/local-pilot/.
2. User (in parallel): AWS Budgets alert (~$30); check the EC2 GPU instance quota (request an increase now if it is 0).
3. Claude: read the pilot report -> pick models, set n and h1_technique, then Stage 6 defenses D1–D4 + layered (one commit each).

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
- 13 Nov — Local runs use native Ollama on Windows (Docker's VM costs RAM on a 7.4 GB laptop); AWS uses the Docker stack. This serving-stack difference is part of what G3 measures and is reported.
- 13 Nov — No AI attribution in commits/pushes/PRs (user rule; skills/00-rules.md rule 21).
- 13 Nov — App B naive loader keeps hidden HTML, alt/ARIA, PDF white/tiny text and PDF metadata in the indexed text [OURS, follows P04 p3 / P13 p3 settings]; BM25 top-3; all 10 attack targets retrieve their poisoned doc for all 7 carriers, and all 30 clean questions retrieve their doc (tests).
- 12 Nov — Approved 13 Nov: 3 apps as HTTP API only (chatbot, RAG, tool agent), techniques T1–T7 x carriers C0–C9 + hybrids H1–H3, defenses D1–D5 + layered; temperature 0 with 30 payload variants per cell. Details: reports/design.md.

## Session start prompt
"Read STATE.md, skills/00-rules.md and the file named in Next actions from github.com/MuhammadTalha57/CEP (branch master). Do only the Next actions. Update STATE.md at the end and tell me exactly which files to commit."
