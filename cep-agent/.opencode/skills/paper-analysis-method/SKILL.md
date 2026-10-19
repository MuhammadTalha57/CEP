---
name: paper-analysis-method
description: Step-by-step method to read one security paper and fill the research log template accurately, including relevance scoring and reusable-asset extraction.
compatibility: opencode
metadata:
  opencode/slash: "true"
---
## What I do
1. Convert the PDF: `python scripts/pdf_to_text.py research/papers/<file>.pdf`, then read research/text/<file>.txt.
2. Read in this order: abstract, contributions, threat model, method, evaluation setup, results, limitations, conclusion, appendix.
3. Fill every field of research/log/TEMPLATE.md. Use numbers from the paper (models, attack types, success rates); never invent any.
4. Set `evidence_level` honestly (full-text / abstract-only / snippet-only).
5. Score 1-10 with the rubric in AGENTS.md. Always explain why it is or is not relevant to cloud-hosted LLM apps and prompt injection.
6. Extract reusable assets (repos, datasets, prompts, metrics) into research/reusable_assets.md.
7. Add the CSV row to research/papers_index.csv.
8. Flag overstated claims, missing baselines, tiny sample sizes, or results on closed models we cannot reproduce.
Paraphrase; quote at most ~15 words.
