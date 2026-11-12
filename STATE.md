# STATE (single source of truth — keep under ~1 page)

**Project:** Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection (CEP_BRIEF.md)
**Constraints:** Python · laptop is CPU-only, 7.4 GB RAM · open-source models only · solo · AWS credit ~$190 · repo public (master)
**Deadline:** Sun 15 Nov 2026 (research paper; extended from 9 Nov). **Last updated:** 12 Nov 2026 (session 4)

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
| 4 | Experiment design + harness | IN PROGRESS | reports/design.md PROPOSED, waiting for user approval; then steps 4.1–4.7 |
| 5 | Local runs (user) | TODO | pilot first, reduced n |
| 6 | Defenses + eval | TODO | D1–D5 + layered (design.md §5) |
| 7 | AWS deployment + cloud runs | TODO | same Docker Compose on EC2 |
| 8 | Paper draft | TODO | |

## Schedule (deadline Sun 15 Nov)
Thu 12: approve design, install Ollama, AWS budget alarm + GPU limit check, steps 4.1–4.3 · Fri 13: steps 4.4–4.7, pilot, local runs, defenses · Sat 14: EC2 deploy, full cloud runs, analysis · Sun 15: paper + submit. Cut order: one model -> weakest injection types -> local-only runs. Never cut cloud runs, the deterministic checker or CIs.

## Next actions (max 3)
1. User: review reports/design.md and approve or change it (apps, injection types, defenses, matrix size).
2. User (in parallel): install Ollama; on AWS set a Budgets alert (~$30) and check the EC2 GPU instance limit (request an increase now if it is 0).
3. Claude: after approval, build steps 4.1–4.3, one commit per step (skills/00-rules.md rules 15–20).

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
- 12 Nov — Proposed (pending approval): 3 apps as HTTP API only (chatbot, RAG, tool agent), techniques T1–T7 x carriers C0–C9 + hybrids H1–H3, defenses D1–D5 + layered; temperature 0 with 30 payload variants per cell. Details: reports/design.md.

## Session start prompt
"Read STATE.md, skills/00-rules.md and the file named in Next actions from github.com/MuhammadTalha57/CEP (branch master). Do only the Next actions. Update STATE.md at the end and tell me exactly which files to commit."
