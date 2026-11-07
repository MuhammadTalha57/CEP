# Ranking and exclusion (final for Stage 2; skills/02)

Data: data/citations.csv and data/artifacts.csv fetched 2026-11-07 09:06 UTC. Shortlist approved by user (assumed as proposed in the provisional version: core + related-work kept, P07/P11/P12 excluded). All sub-scores are [INFERENCE] using the skills/02 weights.

| Rank | ID | Rel /40 | Rigor /20 | Artifacts /15 | Cites /10 (source counts) | Venue+recency /10 | Threat model /5 | Total /100 | Decision | One-line reason (page refs) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | P03 | 30 | 16 | 14 | 8 (median 35 of OA 35/S2 90/CR 33; 25.9/yr) | 8 | 4 | **80** | keep-core | Public detector benchmark+code (HF Apache-2.0, GitHub; fetched 7 Nov); TPR@FPR1% 94.80% vs DeBERTa 43.22% (p9) |
| 2 | P08 | 28 | 14 | 14 | 10 (median 104 of OA 104/S2 433/CR 15; 297.1/yr) | 9 | 4 | **79** | keep-core | Only tool-agent defense with Apache-2.0 code; 77% vs 84% utility (p1), 2.82x input tokens (p11); closed models only |
| 3 | P04 | 36 | 16 | 0 | 8 (median 14 of S2 14; 40.0/yr) | 9 | 5 | **74** | keep-core | RAG carriers + sanitize/normalize/attribution stack; macro ASR 24.9 -> 4.7 with 95% CIs (p3); no repo found |
| 4 | P05 | 36 | 12 | 0 | 4 (median 2 of OA 2/S2 3/CR 2; 5.7/yr) | 6 | 4 | **62** | keep-core | Closest prior work, same small open models (qwen3:1.7b 71.3% injection, p7); direct prompts only; denominators inconsistent |
| 5 | P01 | 22 | 14 | 3 | 8 (median 86 of OA 86/S2 258/CR 78; 36.6/yr) | 9 | 4 | **60** | keep-related | Manual-attack taxonomy usable as direct-injection types (manual ASR 7.3-16.3%, p8); optimization attack needs white-box GPU (p4) |
| 6 | P13 | 36 | 13 | 0 | 0 (median 0 of OA 0/CR 0; 0.0/yr) | 4 | 5 | **58** | keep-core | Hidden-text PDF vectors on 6 open 7-14B models, mean ASR 47.78% (p1,p5); single run, no CIs, no code |
| 7 | P06 | 28 | 10 | 2 | 2 (median 2 of OA 2/S2 1/CR 2; 1.5/yr) | 5 | 3 | **50** | keep-related | AWS SageMaker/S3/CloudWatch blueprint (p4,5); repo URL 404 on 7 Nov; DistilBERT F1 mismatch |
| 8 | P02 | 20 | 13 | 0 | 6 (median 34 of OA 34/S2 113/CR 31; 14.5/yr) | 6 | 4 | **49** | keep-related | Learned triggers reach ~95% on Llama-3 (p2) but need white-box GPU optimization; cite as taxonomy only |
| 9 | P09 | 14 | 12 | 8 | 0 (median 0 of OA 0/S2 0/CR 0; 0.0/yr) | 10 | 4 | **48** | keep-related | Public HF datasets (2 of 3 licensed, fetched 7 Nov) + detectors (p8,12); scheduler needs GPU, simulated; Static-mal F1 0.752 vs GMDRA 0.865 (p10) |
| 10 | P10 | 20 | 16 | 0 | 0 (median 0 of OA 0/S2 0/CR 0; 0.0/yr) | 3 | 4 | **43** | keep-related | Paired Wilson/McNemar method + attack classes (p2-4); persona-specific; n=80, reductions not significant (p4) |
| 11 | P12 | 24 | 4 | 0 | 2 (median 1 of OA 1/S2 2/CR 0; 2.9/yr) | 4 | 3 | **37** | exclude | Cloud-agent threat taxonomy (p2) but numbers inconsistent: AWS 8% vs "under 8%", 78->8 is 89.7% not 92% (p5) |
| 12 | P11 | 14 | 8 | 0 | 2 (median 3 of OA 2/S2 3/CR 3; 2.2/yr) | 4 | 3 | **31** | exclude | Hash+MiniLM near-match; only author-made variants as baselines, results in figures (p6); tests on same template pools |
| 13 | P07 | 12 | 6 | 0 | 0 (median 0 of OA 0/S2 0/CR 0; 0.0/yr) | 4 | 2 | **24** | exclude | Simulation-only; no injection types; main results in figures, no numeric speedups (p3-4) |

## Method and caveats

- **Citations /10:** median of available OpenAlex (OA) / Semantic Scholar (S2) / Crossref (CR) counts divided by age = 2026.85 - (year + 0.5); thresholds [INFERENCE]: >=50/yr 10, >=20 8, >=10 6, >=5 4, >=1 2, else 0.
- Sources disagree strongly (P08: OA 104 / S2 433 / CR 15; was OA 17 on 31 Oct), so counts are volatile and young-paper per-year rates are inflated. P04 has a single source (S2 14, matched by title; OpenAlex and Crossref have no record). P13 S2 returned HTTP 429, so its median uses OA and CR only. P09 and P10 are 0 everywhere (too new), which costs them points for age, not quality.
- **P04 DOI** supplied by user: 10.1145/3774904.3792853 (ACM page found; doi.org resolution error reported by user to ACM). Crossref having no record is consistent with the DOI not yet being registered [INFERENCE].
- **Artifacts /15:** P03 (HF dataset apache-2.0, 9 likes; GitHub 4 stars, last push 2025-10-27, no license shown) and P08 (GitHub Apache-2.0, 418 stars, last push 2025-06-20) score 14 (not run, so not 15). P09: jackhhao dataset apache-2.0 and ahsanayub mit verified, guychuk HTTP 401, protectai model not fetched: 8. P06 repo 404: 2. P01 arXiv link only: 3.
- Venue, threat-model and relevance sub-scores are judgement; no venue-ranking figures were recalled.

## Screening (skills/00 rule 11)

10 of 13 kept (core: P03, P04, P05, P08, P13; related-work: P01, P02, P06, P09, P10); P07, P11, P12 excluded for evidence quality. No hard-exclude criteria met; no duplicates (DOI + title check). Exactly 10 remain, so no slack; no papers were added to reach a count.

## Not comparable (rule 4)

Success rates in P05, P10 and P13 use different benchmarks, models and success definitions; see reports/gaps.md for the metric table.
