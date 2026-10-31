# STATE (single source of truth — keep under ~1 page)

**Project:** Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection (see CEP_BRIEF.md)
**Constraints:** Python · no GPU · open-source models only · no frontier-model access · repo public (master)
**Last updated:** (session 0) 

## Blocking questions (answer before Stage 4)
- [ ] Q1: Does the instructor expect ONLY attack evaluation, or also a proposed defense/solution? Is AWS deployment required or optional?
- [ ] A1: Both are expected. Yes AWS deployment is required.
- [ ] Q2: Deadline, group size, required deliverable format (report/slides/demo)?
- [ ] A2: Deadline: 9th November, I'm solo, Deliverable is proper required reseach paper. We'll write paper later after we've finished all the main work. It would be very nice to maintain files/assets that will help us in refering in the paper. 

## Stages
| # | Stage | Status | Notes |
|---|-------|--------|-------|
| 0 | Scaffold repo | DONE | files committed |
| 1 | Extract info from 13 papers (skills/01) | TODO | batches of 3–5 |
| 2 | Rank + exclude (skills/02) | TODO | needs citation counts (user fills) |
| 3 | Gap analysis, backed by numbers (skills/03) | TODO | |
| 4 | Experiment design: models, apps, attack types (skills/04) | TODO | |
| 5 | Local runs (Ollama/CPU or free hosted) — user runs, sends logs | TODO | |
| 6 | Results + report | TODO | |
| 7 | Optional: AWS deployment plan | TODO | only if Q1 says needed |

## Next actions (max 3)
1. User answers Q1/Q2 in this file.
2. Claude: extract P01–P04 → data/papers/P01.json … (skills/01).
3. User: commit JSON files, update ledger.

## Decisions log (date — decision — reason)
- 
## Session start prompt (paste at top of every new chat)
"Read STATE.md, skills/00-rules.md and the skill named in Next actions from github.com/MuhammadTalha57/CEP (branch master). Do only the Next actions. Update STATE.md at the end and tell me exactly which files to commit."