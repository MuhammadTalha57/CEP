# 00 Global rules (read every session)

## Evidence
1. Every factual claim about a paper = `{value, page, quote<=15 words}` or `NOT FOUND`. Never fill from memory.
2. External numbers (citations, stars) = `{value, source, date_fetched}`. Never recalled; user supplies or a script fetches.
3. Label anything that is my reasoning `[INFERENCE]`. Numbers in recommendations must trace to a paper page or to our own experiment logs.
4. Numbers from different papers are comparable only if benchmark, model, and metric definition match; otherwise say "not comparable".

## Token / effort discipline
5. Read STATE.md first. Do only "Next actions". Do not scan directories; use data/ledger.csv as the index.
6. Clone once per session: `git clone --depth 1 --filter=blob:none -b master <repo>`; fetch only needed PDFs (sparse checkout / `git show HEAD:path`). Use `git pull`, never re-clone.
7. Each PDF is read once -> data/papers/<id>.json. Later stages read JSON only.
8. Skip anything listed in data/verified.json for the same git_blob. Re-verify only if the blob changed.
9. Batches of 3–5 papers. Stop and report at batch end; do not start the next stage unprompted.
10. Ask the user only for things that block progress; state assumptions in one line otherwise.

## Honesty
11. Do not add papers to reach a count. If fewer than 10 pass screening, say so and propose how to find more.
12. Flag low-confidence extractions (tables/figures) instead of smoothing over them.
13. Ethics: attack only our own test apps/models in the lab setup. No attacks on third-party services.

## End of session
14. Update STATE.md (status, next 3 actions, decisions), list files to commit, one line each.

## Engineering (Stages 4–7; added 12 Nov)
15. Plan before code: every stage starts from an approved design (reports/design.md). Changes to apps, injection types, defenses or matrix size need user approval and a decisions-log line.
16. One step = one commit, message `stageN.M: <what>`. A step is committed only when its tests pass (`pytest`, using the mock LLM backend). No unrelated changes in a step.
17. Every design choice is tagged with its source: paper id + page, `[OURS]`, or `[INFERENCE]`.
18. No hard-coded model names, URLs or keys in code: models in configs/models.yaml, secrets in environment variables (never committed).
19. Same code locally and on AWS: only config/env changes between environments. Every trial is logged to results/ as JSONL; results are never edited by hand.
20. AWS: budget alert set before the first launch; stop instances at the end of every session; record the hours used in STATE.md.
21. Commits, pushes and PRs carry no AI attribution: no `Co-Authored-By: Claude` trailer, no "Generated with" line. The author is the user's git identity only.