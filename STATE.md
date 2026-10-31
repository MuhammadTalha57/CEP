# STATE (single source of truth — keep under ~1 page)

**Project:** Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection (CEP_BRIEF.md)
**Constraints:** Python · no GPU · open-source models only · solo · repo public (master)
**Deadline:** 9 Nov 2026 (research paper). **Last updated:** 31 Oct 2026 (session 1)

## Confirmed requirements
- Attack evaluation (models x minimal apps x injection types) AND a proposed defense AND AWS deployment. Output = research paper.
- Keep paper-ready assets: `paper/facts.md` (page-referenced numbers), `results/` (raw logs), `data/papers/*.json`.

## Stages
| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Scaffold | DONE | |
| 1 | Extract 13 papers | IN PROGRESS | P01–P04 done; P05–P13 todo |
| 2 | Rank + exclude | TODO | citations optional (see decision D1) |
| 3 | Gap analysis | TODO | |
| 4 | Experiment design + harness | TODO | |
| 5 | Local runs (user) | TODO | |
| 6 | Defense + eval | TODO | |
| 7 | AWS deployment | TODO | |
| 8 | Paper draft | TODO | |

## Schedule (9 days — tight)
1–2 Nov: finish extraction + ranking · 2–3 Nov: gaps + experiment design + harness code · 3–6 Nov: runs, defense, results · 6–8 Nov: AWS deploy + paper · 9 Nov: submit. Cut scope before cutting experiments.

## Next actions (max 3)
1. User: commit `data/papers/P01–P04.json`, `data/ledger.csv`, `data/verified.json`, `paper/facts.md`, this file.
2. Claude: extract P05–P08 (skills/01), then P09–P13.
3. User: confirm decision D1.

## Decisions log
- 31 Oct — D1 (proposed, needs OK): skip citation-count fetching to save time; rank on relevance/rigor/artifacts/recency only.
- 31 Oct — P01, P02 are white-box optimization attacks (need GPU) → cite as related work/taxonomy, don't reproduce.
- 31 Oct — P03 (PromptShield, public detectors) and P04 (OpenRAG-Soc carriers + sanitize/normalize/attribution) are the strongest reuse candidates for defense and RAG app.

## Session start prompt
"Read STATE.md, skills/00-rules.md and the skill named in Next actions from github.com/MuhammadTalha57/CEP (branch master). Do only the Next actions. Update STATE.md at the end and tell me exactly which files to commit."