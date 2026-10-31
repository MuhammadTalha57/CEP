# 02 Rank and exclude

Inputs: data/papers/*.json, user-supplied citation counts in ledger (`citations`, `cit_source`, `cit_date`).
Score (0–100), weights editable in STATE.md decisions:
- Relevance to our project (attack types, measurable results, cloud LLM apps): 40
- Empirical rigor (named models, n, metrics defined, numbers reported): 20
- Reusable artifacts (code/data/benchmark that exists and is licensed): 15
- Citations per year since publication (source+date labelled): 10
- Venue/recency: 10
- Clarity of threat model: 5
Hard exclude: unrelated to prompt injection of LLM apps; duplicate; no extractable evidence.
Output: reports/ranking.md = table (id, score breakdown, decision, one-line reason with page refs). Update ledger decision/reason. User approves before Stage 3.
GitHub stats for artifacts: stars, forks, last commit, license, via `git`/API with date fetched; stars are weak evidence, so also record last-commit and whether it runs.