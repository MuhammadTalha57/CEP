# STATE (single source of truth — keep under ~1 page)

**Project:** Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection (CEP_BRIEF.md)
**Constraints:** Python · no GPU · open-source models only · solo · repo public (master)
**Deadline:** 9 Nov 2026 (research paper). **Last updated:** 31 Oct 2026 (end of session 1; usage limit reached)

## Confirmed requirements
- Attack evaluation (models x minimal apps x injection types) AND a proposed defense AND AWS deployment. Output = research paper.
- Keep paper-ready assets: `paper/facts.md` (page-referenced numbers), `results/` (raw logs), `data/papers/*.json`.

## Stages
| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Scaffold | DONE | |
| 1 | Extract 13 papers | IN PROGRESS | P01–P08 done; P09–P13 todo |
| 2 | Rank + exclude | TODO | needs data/citations.csv + artifacts.csv (GitHub Action) |
| 3 | Gap analysis | TODO | |
| 4 | Experiment design + harness | TODO | |
| 5 | Local runs (user) | TODO | |
| 6 | Defense + eval | TODO | |
| 7 | AWS deployment | TODO | |
| 8 | Paper draft | TODO | |

## Schedule (9 days — tight)
1–2 Nov: finish extraction + ranking · 2–3 Nov: gaps + experiment design + harness code · 3–6 Nov: runs, defense, results · 6–8 Nov: AWS deploy + paper · 9 Nov: submit. Cut scope before cutting experiments.

## Next actions (max 3)
1. Claude: extract P09–P13 (skills/01) in two batches (P09–P11, P12–P13); write JSON + update ledger/verified/facts.
2. Claude: read data/citations.csv and data/artifacts.csv (already in repo; do NOT re-run the workflow unless P09–P13 DOIs are new), then rank + exclude (skills/02) -> reports/ranking.md.
3. User: commit outputs, re-run "Fetch metrics" workflow once after P09–P13 are committed, approve shortlist.

## Decisions log
- 31 Oct — D1 REVERSED by user: citation counts ARE required. Fetched by GitHub Action `Fetch metrics` (sources: OpenAlex, Semantic Scholar, Crossref; repo stars via GitHub API). Claude can't reach these APIs.
- 31 Oct — P01, P02 are white-box optimization attacks (need GPU) → cite as related work/taxonomy, don't reproduce.
- 31 Oct — P03 (PromptShield, public detectors) and P04 (OpenRAG-Soc carriers + sanitize/normalize/attribution) are the strongest reuse candidates for defense and RAG app.

- 31 Oct — P05 (LM-SHIELD '26) is the closest prior work: same small open models (Llama3.2, qwen3, gemma3, DeepSeek-R1, phi3, Mistral), direct prompts only. Our differentiators to test: RAG/tool apps, CIs, deterministic success checks, cloud deployment.
- 31 Oct — Source inconsistencies logged in JSON flags: P05 rate denominators (91 vs 94; 74 vs completed runs), P06 DistilBERT F1 (0.92 reported, ~0.94 from P/R) and augment-then-split leakage risk. Our harness must fix denominators and report CIs.
- 31 Oct — P06 gives a reusable AWS blueprint (SageMaker endpoint, S3, CloudWatch, gateway block at 0.85); P08 gives a design pattern for the tool app defense; P07 is simulation-only (low priority).

## Session start prompt
"Read STATE.md, skills/00-rules.md and the skill named in Next actions from github.com/MuhammadTalha57/CEP (branch master). Do only the Next actions. Update STATE.md at the end and tell me exactly which files to commit."