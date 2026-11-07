# Ranking and exclusion (PROVISIONAL, skills/02)

Status: citation points missing for P04 and P09-P13 (data/citations.csv has no DOI-matched row for them). Compare papers on **Sum /90** (all criteria except citations). Final /100 is complete only for papers with citation data. User approves before Stage 3.

All sub-scores are [INFERENCE] using the skills/02 weights; every score cites the JSON evidence in the reason column. Edit weights in STATE.md decisions if you disagree.

| Rank | ID | Rel /40 | Rigor /20 | Artifacts /15 | Cites /10 | Venue+recency /10 | Threat model /5 | **Sum /90** | Total /100 | Decision (proposed) | One-line reason (page refs) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P03 | 30 | 16 | 14 | 8 (median 32 of [31, 88, 32]; 23.7/yr) | 8 | 4 | **72** | 80 | keep-core | Public detector benchmark+code (HF Apache-2.0, GitHub; fetched 31 Oct); TPR@FPR1% 94.80% vs DeBERTa 43.22% (p9) |
| 2 | P08 | 28 | 14 | 14 | 8 (median 17 of [17, 403, 10]; 48.6/yr) | 9 | 4 | **69** | 77 | keep-core | Only tool-agent defense with Apache-2.0 code; 77% vs 84% utility (p1), 2.82x input tokens (p11); closed models only |
| 3 | P04 | 36 | 16 | 0 | pending (no data fetched) | 9 | 5 | **66** | pending | keep-core | RAG carriers + sanitize/normalize/attribution stack; macro ASR 24.9 -> 4.7 with 95% CIs (p3); no repo found |
| 4 | P05 | 36 | 12 | 0 | 4 (median 2 of [2, 3, 2]; 5.7/yr) | 6 | 4 | **58** | 62 | keep-core | Closest prior work, same small open models (qwen3:1.7b 71.3% injection, p7); direct prompts only; denominators inconsistent |
| 5 | P13 | 36 | 13 | 0 | pending (no data fetched) | 4 | 5 | **58** | pending | keep-core | Hidden-text PDF vectors on 6 open 7-14B models, mean ASR 47.78% (p1,p5); single run, no CIs, no code |
| 6 | P01 | 22 | 14 | 3 | 8 (median 73 of [70, 253, 73]; 31.1/yr) | 9 | 4 | **52** | 60 | keep-related | Manual-attack taxonomy usable as direct-injection types (manual ASR 7.3-16.3%, p8); optimization attack needs white-box GPU (p4) |
| 7 | P06 | 28 | 10 | 2 | 2 (median 2 of [2, 1, 2]; 1.5/yr) | 5 | 3 | **48** | 50 | keep-related | AWS SageMaker/S3/CloudWatch blueprint (p4,5); repo URL 404 on 31 Oct; DistilBERT F1 mismatch |
| 8 | P09 | 14 | 12 | 6 | pending (no data fetched) | 10 | 4 | **46** | pending | keep-related | Public HF datasets+detectors (p8,12); scheduler needs GPU and is simulated; Static-mal F1 0.752 vs GMDRA 0.865 (p10) |
| 9 | P02 | 20 | 13 | 0 | 6 (median 30 of [26, 111, 30]; 12.8/yr) | 6 | 4 | **43** | 49 | keep-related | Learned triggers reach ~95% on Llama-3 (p2) but need white-box GPU optimization; cite as taxonomy only |
| 10 | P10 | 20 | 16 | 0 | pending (no data fetched) | 3 | 4 | **43** | pending | keep-related | Paired Wilson/McNemar method + attack classes (p2-4); persona-specific; n=80, reductions not significant (p4) |
| 11 | P12 | 24 | 4 | 0 | pending (no data fetched) | 4 | 3 | **35** | pending | exclude-proposed | Cloud-agent threat taxonomy (p2) but numbers inconsistent: AWS 8% vs "under 8%", 78->8 is 89.7% not 92% (p5) |
| 12 | P11 | 14 | 8 | 0 | pending (no data fetched) | 4 | 3 | **29** | pending | exclude-proposed | Hash+MiniLM near-match; only author-made variants as baselines, results in figures (p6); tests on same template pools |
| 13 | P07 | 12 | 6 | 0 | 0 (median 0 of [0, 0, 0]; 0.0/yr) | 4 | 2 | **24** | 24 | exclude-proposed | Simulation-only; no injection types; main results in figures, no numeric speedups (p3-4) |

## How scores were set

- **Citations /10:** median of the available OpenAlex / Semantic Scholar / Crossref counts in data/citations.csv (fetched 2026-10-31 11:34 UTC), divided by age = 2026.85 - (year + 0.5). Thresholds [INFERENCE]: >=50/yr 10, >=20 8, >=10 6, >=5 4, >=1 2, else 0. Sources disagree strongly (P08: 17 / 403 / 10; P01: 70 / 253 / 73), so the median is used and all raw values are kept in citations.csv. P08's Semantic Scholar count likely includes its 2025 arXiv version; its per-year figure is therefore generous.
- **Artifacts /15:** only what data/artifacts.csv verified on 2026-10-31: P03 (HF dataset apache-2.0 + GitHub, last push 2025-10-27) and P08 (GitHub Apache-2.0, last push 2025-06-20) score 14 (not run, so not 15). P06 repo returned 404 (2). P01 only an arXiv link (3). P09 names public HF datasets/detectors (p8, p12) whose stats were never fetched: provisional 6. All others have no artifact URL in the paper (0).
- **Venue+recency /10 and Threat model /5:** judgement only; no venue-ranking numbers were recalled.
- **Relevance /40** rewards: injection types we can run on CPU, measurable results, RAG/tool/cloud apps. **Rigor /20** rewards: named models, n, defined metrics, CIs, internal consistency.

## Screening result (skills/00 rule 11)

No paper meets a hard-exclude criterion (unrelated / duplicate / no extractable evidence). No duplicates: DOIs and titles checked across P01-P13 (P07 and P09 both edge-cloud detection but different papers, DOIs and authors).
Proposed to keep: 10 of 13 (core: P03, P04, P05, P08, P13; related-work: P01, P02, P06, P09, P10). Proposed soft-exclude: P07, P11, P12 for evidence quality, which is a judgement call rather than a hard-exclude rule. That leaves exactly 10, so there is no slack; I did not add papers to reach a count. If you want slack, keep P12 as a citation for its threat taxonomy only (do not cite its numbers).

## Not comparable (rule 4)

P05, P13 and P10 report ASR or jailbreak rates on different benchmarks, models and success definitions (instruction-override vs tracer keyword vs persona break), so their percentages must not be ranked against each other.

## Still needed for a final ranking

1. Re-run the `Fetch metrics` workflow after committing P09-P13 (their DOIs are new, per STATE rule). P04 also has no DOI, so OpenAlex found nothing and Semantic Scholar returned HTTP 429: supply its DOI or title match.
2. P03's DOI is 'derived from filename; verify' (ledger). Citation data was returned for it, but confirm the DOI on the paper page.
3. artifacts.csv has no rows for P09's HF datasets/detectors; the workflow will fetch them if the URLs are in the JSON (they are).
