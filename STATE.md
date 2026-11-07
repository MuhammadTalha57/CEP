# STATE (single source of truth — keep under ~1 page)

**Project:** Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection (CEP_BRIEF.md)
**Constraints:** Python · no GPU · open-source models only · solo · repo public (master)
**Deadline:** 9 Nov 2026 (research paper). **Last updated:** 7 Nov 2026 (end of session 2)

## Confirmed requirements
- Attack evaluation (models x minimal apps x injection types) AND a proposed defense AND AWS deployment. Output = research paper.
- Keep paper-ready assets: `paper/facts.md` (page-referenced numbers), `results/` (raw logs), `data/papers/*.json`.

## Stages
| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Scaffold | DONE | |
| 1 | Extract 13 papers | DONE | P01–P13 in data/papers/ (quotes machine-checked vs PDF text) |
| 2 | Rank + exclude | IN PROGRESS | reports/ranking.md PROVISIONAL: citation points missing for P04, P09–P13 |
| 3 | Gap analysis | TODO | |
| 4 | Experiment design + harness | TODO | |
| 5 | Local runs (user) | TODO | |
| 6 | Defense + eval | TODO | |
| 7 | AWS deployment | TODO | |
| 8 | Paper draft | TODO | |

## Schedule (BEHIND: today 7 Nov, deadline 9 Nov = 2 days)
Original plan had extraction + ranking done by 2 Nov; it slipped 5 days (usage limit). Remaining: 7 Nov: approve shortlist, gaps + experiment design + harness · 8 Nov: runs, defense, AWS deploy · 9 Nov: paper + submit. Cut scope before cutting experiments; decide the cut line at Stage 3.

## Next actions (max 3)
1. User: commit the session-2 files, then run the "Fetch metrics" workflow once (P09–P13 DOIs are new; P04 has no DOI, send it if known). Then ask Claude to finish the citation column in reports/ranking.md.
2. User: approve or edit the shortlist in reports/ranking.md (core P03, P04, P05, P08, P13; related-work P01, P02, P06, P09, P10; proposed soft-exclude P07, P11, P12). Also verify P03's DOI (ledger says derived from filename).
3. Claude (after approval): Stage 3 gap analysis (skills/03); read data/papers/*.json only.

## Decisions log
- 31 Oct — D1 REVERSED by user: citation counts ARE required. Fetched by GitHub Action `Fetch metrics` (sources: OpenAlex, Semantic Scholar, Crossref; repo stars via GitHub API). Claude can't reach these APIs.
- 31 Oct — P01, P02 are white-box optimization attacks (need GPU) → cite as related work/taxonomy, don't reproduce.
- 31 Oct — P03 (PromptShield, public detectors) and P04 (OpenRAG-Soc carriers + sanitize/normalize/attribution) are the strongest reuse candidates for defense and RAG app.

- 31 Oct — P05 (LM-SHIELD '26) is the closest prior work: same small open models (Llama3.2, qwen3, gemma3, DeepSeek-R1, phi3, Mistral), direct prompts only. Our differentiators to test: RAG/tool apps, CIs, deterministic success checks, cloud deployment.
- 31 Oct — Source inconsistencies logged in JSON flags: P05 rate denominators (91 vs 94; 74 vs completed runs), P06 DistilBERT F1 (0.92 reported, ~0.94 from P/R) and augment-then-split leakage risk. Our harness must fix denominators and report CIs.
- 31 Oct — P06 gives a reusable AWS blueprint (SageMaker endpoint, S3, CloudWatch, gateway block at 0.85); P08 gives a design pattern for the tool app defense; P07 is simulation-only (low priority).

- 7 Nov — P13 is the strongest reuse for the RAG app: hidden PDF text (white, 0.1 pt, metadata) on 6 open 7–14B models, mean ASR 47.78% (p1,p5), deterministic tracer keywords. Gaps we fix: single run/no CIs, keyword-only success, no clean-task utility, no code.
- 7 Nov — P10 gives our stats template (paired agents, Wilson CI + McNemar; n=80 gives wide CIs, p4); P09 is GPU/simulated, reuse only its public HF datasets and detectors; P11 weak (author-made baselines only, p6); P12 numbers internally inconsistent (p5), cite for threat taxonomy only.
- 7 Nov — Ranking is PROVISIONAL: compare on Sum /90 until citation data exists for P04, P09–P13. No duplicates found (DOI + title check). Keeping 10 of 13 leaves no slack (rule 11).

## Session start prompt
"Read STATE.md, skills/00-rules.md and the skill named in Next actions from github.com/MuhammadTalha57/CEP (branch master). Do only the Next actions. Update STATE.md at the end and tell me exactly which files to commit."