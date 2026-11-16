# 3. Ranking, screening and gap analysis (Stages 2–3)

## 3.1 Scoring formula (`skills/02-rank-exclude.md`)

Every paper got a score out of 100 from six parts:

$$
\text{Score} = \underbrace{R}_{\le 40} + \underbrace{Q}_{\le 20} + \underbrace{A}_{\le 15} + \underbrace{C}_{\le 10} + \underbrace{V}_{\le 10} + \underbrace{T}_{\le 5}
$$

| Part | Meaning | How it was set |
|---|---|---|
| R, relevance (40) | How directly the paper helps our brief (attacks on LLM apps, injection types, defenses, cloud) | Judgement [INFERENCE] |
| Q, rigor (20) | Sample sizes, CIs, baselines, internal consistency | Judgement, with the flags from extraction |
| A, artifacts (15) | Public code or data that we could check | GitHub / Hugging Face pages fetched by script on 7 Nov |
| C, citations (10) | Citations per year (see below) | Fetched automatically (`scripts/fetch_metrics.py`) |
| V, venue + recency (10) | Peer-reviewed venue, how recent | Judgement |
| T, threat model (5) | Whether the attacker model is clear and realistic | Judgement |

**Citations per year.** Three databases (OpenAlex, Semantic Scholar, Crossref) disagree, so the **median** of the available counts is used, divided by the paper's age:

$$
\text{cites/yr} = \frac{\operatorname{median}(\text{OA}, \text{S2}, \text{CR})}{2026.85 - (\text{year} + 0.5)}
$$

Mapping to points: ≥ 50/yr → 10, ≥ 20 → 8, ≥ 10 → 6, ≥ 5 → 4, ≥ 1 → 2, otherwise 0. Very new papers (P09, P10, P13) get 0 here because they are new, not because they are weak.

## 3.2 Result

| Rank | ID | R | Q | A | C | V | T | **Total** | Decision |
|---|---|---|---|---|---|---|---|---|---|
| 1 | P03 | 30 | 16 | 14 | 8 | 8 | 4 | **80** | keep, core |
| 2 | P08 | 28 | 14 | 14 | 10 | 9 | 4 | **79** | keep, core |
| 3 | P04 | 36 | 16 | 0 | 8 | 9 | 5 | **74** | keep, core |
| 4 | P05 | 36 | 12 | 0 | 4 | 6 | 4 | **62** | keep, core |
| 5 | P01 | 22 | 14 | 3 | 8 | 9 | 4 | **60** | keep, related |
| 6 | P13 | 36 | 13 | 0 | 0 | 4 | 5 | **58** | keep, core |
| 7 | P06 | 28 | 10 | 2 | 2 | 5 | 3 | **50** | keep, related |
| 8 | P02 | 20 | 13 | 0 | 6 | 6 | 4 | **49** | keep, related |
| 9 | P09 | 14 | 12 | 8 | 0 | 10 | 4 | **48** | keep, related |
| 10 | P10 | 20 | 16 | 0 | 0 | 3 | 4 | **43** | keep, related |
| 11 | P12 | 24 | 4 | 0 | 2 | 4 | 3 | **37** | excluded: inconsistent numbers (p5) |
| 12 | P11 | 14 | 8 | 0 | 2 | 4 | 3 | **31** | excluded: weak baselines, results from figures only |
| 13 | P07 | 12 | 6 | 0 | 0 | 4 | 2 | **24** | excluded: simulation only, no injection types |

**Screening rule** (`skills/00-rules.md`, rule 11): papers are never added just to reach a count. Exactly 10 passed, so there was no slack.

## 3.3 Gap analysis (`reports/gaps.md`)

The 10 kept papers were compared in four coverage tables:
- injection type × paper;
- model × paper;
- metric definitions;
- reported numbers.

### Who covers which channel

| Injection channel | Papers | What is missing |
|---|---|---|
| Direct (user message) | P01 p8, P05 p8, P10 p3 | Different models and success definitions |
| HTML / Unicode carriers in RAG | P04 p3 | Generator model not named |
| PDF hidden text | P13 p3 | One payload, no CIs, no defense |
| Tool output (agents) | P08 p1 | Closed models only |

### Who measured attack success on small open models

Only **P05** (direct prompts only) and **P13** (PDF only). They never share an application type, so nothing tells us whether a model that resists one channel resists the others.

### The three gaps

| Gap | Statement | Evidence | Became |
|---|---|---|---|
| **G1** | No paper tests the **same small open models** across **direct, document and tool-output** injection, with **one success checker** and **confidence intervals** | P05 direct only, no CIs (p1, p7); P13 PDF only (p1, p5); P04 model unnamed (p3); P08 closed models (p1, p7) | Our attack matrix: 4 models × 3 apps × 33 cells |
| **G2** | No defense is evaluated **end-to-end** on small open models in RAG and tool apps, with **utility and latency** cost | P13 tests no defense (p6); P04 unnamed model (p3); P08 closed models (p1, p11); P03 detector-level metrics only (p9) | D1–D4 + our layered defense, with ASR, utility, false positives and latency |
| **G3** | No paper measures whether **cloud hosting** changes the result **for the same model** | P06 reports detector F1 only (p4–6); P09 emulates on one machine (p8); P10 compares two **different** models (p4) | The same trials run on Kaggle (in process) and on AWS (Docker + HTTP), paired trial by trial |

**Decision (12 Nov): G1 + G2 + G3.** G1 is the core and answers the brief. G2 is the defense part. G3 is what makes the project about *cloud-hosted* applications.
