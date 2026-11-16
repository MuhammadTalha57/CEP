# 11. The paper (Elsevier els-cas template)

## 11.1 Files

| File | What it is |
|---|---|
| `paper/cas/main.tex` | **The paper**, Elsevier CAS double-column class (`cas-dc`), from `els-cas-templates` v2.4 |
| `paper/cas/refs.bib` | References (metadata from `data/papers/*.json`) |
| `paper/cas/cloud_table.tex`, `paper/cas/cloud_numbers.tex` | **Generated** by `scripts/cloud_compare.py`: the Kaggle-vs-AWS table and every cloud number used in the text. Never edit by hand |
| `paper/cas/figs/*.pdf` | **Generated** by `scripts/make_figures.py` from `results/` |
| `paper/cas/cas-dc.cls`, `cas-common.sty`, `cas-model2-names.bst` | Template files (LaTeX Project Public License) |
| `paper/cas/main.pdf` | Compiled paper |
| `paper/facts.md` | Every citable number from the papers, with its page |
| `paper/main.tex` | Older IEEE-format draft. **Superseded** by `paper/cas/main.tex` (it also has two wording errors about the success checks, fixed in the cas version) |

## 11.2 Structure and where each part comes from

| Section | Content | Source in the repo |
|---|---|---|
| Highlights (separate page) | 5 one-line findings | 08_results_and_findings.md |
| Abstract | Setting, matrix, main numbers | all reports |
| 1 Introduction | Problem, 3 gaps, 4 contributions | reports/gaps.md |
| 2 Background and related work | Literature selection method, 10 kept papers grouped by topic, with page-cited numbers | data/papers/*.json, reports/ranking.md, paper/facts.md |
| 3 Threat model | Attacker capabilities and goals per app | reports/design.md §3 |
| 4 System and methodology | Fig. 1 architecture; apps; models; attack matrix (Table 1); success checks; Wilson and McNemar formulas; deployments | reports/design.md, src/llmsec |
| 5 Defenses | D1–D4 and the layered defense | src/llmsec/defenses, configs/defenses.yaml |
| 6 Results: attacks without defense | Fig. 2, Tables 2–3 | reports/baseline_kaggle.md |
| 7 Results: defenses | Fig. 3–4, Table 4 | reports/defense_kaggle.md |
| 8 Results: development vs cloud | Table 5, Fig. 5 | reports/cloud_aws.md |
| 9 Discussion and limitations | Implications, 7 limitations, ethics | — |
| 10 Conclusion | | — |
| End matter | Data availability, competing interests, **generative-AI declaration** (Elsevier requires it), CRediT roles, references | — |

## 11.3 Compile

```powershell
cd paper\cas
pdflatex main
bibtex main
pdflatex main
pdflatex main
```

**MiKTeX users:** the class needs the `stix` and `inconsolata` font packages. If compilation stops after `fontenc`, install them once with:

```powershell
miktex packages install stix
miktex packages install inconsolata
```

**Overleaf:** upload the whole `paper/cas/` folder (keep `figs/`), set the compiler to pdfLaTeX, and set the main document to `main.tex`.

**Updating the numbers after new runs:**

```powershell
.\.venv\Scripts\python scripts\cloud_compare.py
.\.venv\Scripts\python scripts\make_figures.py
```

Then recompile. The text, table and figures update together, so they cannot disagree.

## 11.4 Things the authors must fill in (marked `TODO` in `main.tex`)

1. The group mate's name, in place of "Group member name".
2. The department in the affiliation (left out on purpose, so as not to guess it).
3. Optionally an email (`\ead{...}`) and ORCID iDs.
4. The CRediT roles (`\credit{...}`): adjust to who did what.

## 11.5 Template notes (cas-dc quirks we hit)

- In this class, `figure` takes key-value options: write `\begin{figure}[pos=!htbp]`. A plain `[!htbp]` is ignored, and the figures drift to the end.
- Citations use natbib author–year: `\citet{P05}` gives "Jaiswal et al. (2026)" and `\citep[p.~7]{P05}` gives "(Jaiswal et al., 2026, p. 7)".
- Wide tables and figures use `table*` / `figure*` (both columns).
