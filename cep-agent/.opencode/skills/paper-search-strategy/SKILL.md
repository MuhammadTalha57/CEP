---
name: paper-search-strategy
description: How to find high-quality prompt-injection / LLM-security papers efficiently using open metadata APIs, citation chasing and venue filtering. Use before any literature search.
compatibility: opencode
metadata:
  opencode/slash: "true"
---
## What I do
1. Run `python scripts/search_papers.py "<query>" --limit 25 --only-vetted` first, then without the flag for recent preprints for 5-8 different queries (see seeds in AGENTS.md).
2. Log every query in research/search_log.md.
3. Rank candidates: strong venue (S&P, USENIX Security, CCS, NDSS, AISec, top ML/NLP security tracks, IEEE TIFS/TDSC, ACM CSUR) > citations per year > recency > has code.
4. Citation chasing: for each paper scored >= 7, list its most relevant references and papers that cite it (Semantic Scholar pages), and add them as candidates.
5. Hunt for reuse: look in the abstract/text for "github", "benchmark", "dataset", "artifact". Reusable code beats a new design.
6. Output a shortlist of <= 15, labelled OPEN (arXiv/open-access PDF) or VPN-ONLY (user downloads manually).

## Rules
No scraping of IEEE/ACM/Springer/Elsevier. If an API errors or rate-limits, wait and tell the user; do not hammer it.
Never judge a paper from the title alone; mark it `unread`.
