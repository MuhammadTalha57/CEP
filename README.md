# Security Evaluation of Cloud-Hosted LLM Applications Against Prompt Injection

Code, data, raw results and paper for our Cloud Computing complex engineering project (CEP) at the Department of Software Engineering, NED University of Engineering and Technology, Karachi.

**Authors:** Muhammad Talha, Shah Iman Ali

**Paper:** [`paper/main.pdf`](paper/main.pdf), in the Elsevier CAS double-column template.

## What we did

We built three minimal LLM applications behind one HTTP API and attacked each one through its own untrusted channel:

| App | What it does | Attack channel | Attack succeeds when |
|---|---|---|---|
| A, support chatbot | Help-desk assistant with a secret discount code in its system prompt | The user message (direct injection) | The secret appears in the answer (also reversed, ROT13 or base64) |
| B, RAG Q&A | Answers HR/IT questions from 20 HTML and PDF documents (BM25, top 3) | A poisoned document in the knowledge base (indirect) | The attacker's random marker appears in the answer |
| C, tool agent | Email and file assistant with mock tools | An email or web page returned by a tool (indirect) | The agent executes `send_email` to the attacker's address |

The attack matrix crosses 7 paper-defined techniques (T1–T7) with 10 carriers (C0–C9, including hidden HTML, zero-width characters and invisible PDF text), plus 3 hybrids (H1–H3). We use 30 wordings per cell and 30 clean tasks per app. Success is decided by deterministic checks with a random canary per trial; no LLM judge is used. We report attack success rate (ASR) with Wilson 95% intervals, and paired comparisons use the exact McNemar test.

Models (Ollama 0.40.16, temperature 0, fixed seed per trial): `qwen3-1.7b`, `llama3.2-3b`, `gemma3-1b`, `qwen3-4b-instruct`.

## Main results

| Finding | Evidence |
|---|---|
| Robustness to direct injection did not carry over to indirect injection | llama3.2-3b: 1.7% chatbot vs 53.1% RAG; qwen3-4b-instruct: 0% chatbot vs 67.1% RAG and 43.7% agent |
| Our channel-aware layered defense gave the lowest ASR in every app, with no clean task blocked | Pooled ASR 40% to 0% (chatbot), 44% to 7% (RAG), 24% to 0% (agent) |
| Unicode normalization alone repaired zero-width payloads, so it must come before detection | T7 in zero-width carrier: 7% without defense, 55% with D2 alone, 4% with the layered defense |
| Moving the same stack to AWS changed wording and latency, not the attack outcome | Same outcome in 1,335 of 1,350 paired trials (98.9%, McNemar p = 1); 22–41x slower on the CPU-only host |

![Baseline ASR per model](reports/figs/fig_baseline_asr.png)

![ASR per defense](reports/figs/fig_defense_asr.png)

Full tables: [`reports/baseline_kaggle.md`](reports/baseline_kaggle.md), [`reports/defense_kaggle.md`](reports/defense_kaggle.md), [`reports/cloud_aws.md`](reports/cloud_aws.md).

## Repository layout

| Path | Contents |
|---|---|
| `src/llmsec/apps/` | The three applications, the FastAPI server and the shared executor |
| `src/llmsec/attacks/` | Techniques (T1–T7), carriers (C0–C9) and the trial generator |
| `src/llmsec/defenses/` | D1 detector, D2 sanitize, D3 spotlighting, D4 tool policy, layered defense |
| `src/llmsec/harness/` | Experiment runner, cloud runner, success checks, Wilson/McNemar statistics, report tables |
| `src/llmsec/llm/` | OpenAI-compatible client for Ollama, plus a mock model for tests |
| `configs/` | Models, attack matrix, defense settings and the cloud run plan |
| `data/kb/`, `data/agent/`, `data/tasks/` | Knowledge-base documents (rendered to HTML/PDF at run time), the agent's mailbox and web pages, attack targets, and the 30 clean tasks per app |
| `results/kaggle/` | Raw JSONL logs of all 19,020 development trials (one line per trial) |
| `results/aws/` | Raw JSONL logs of the 1,350 cloud trials, the run log and the EC2 environment record |
| `results/kaggle-pilot/` | The timing pilot |
| `results/excluded/` | The excluded thinking-only `qwen3:4b` run, with the reason |
| `reports/` | Result tables generated from `results/`, figures, and the experiment design |
| `literature/` | The 13 extracted papers (`papers/P01–P13.json`, every value with its PDF page), ranking, gap analysis, page-cited facts and citation metrics |
| `deploy/` | Kaggle notebook, AWS setup script and step-by-step guides |
| `paper/` | LaTeX source of the paper (`main.tex`, `refs.bib`), generated tables and figures, compiled PDF |
| `tests/` | 97 unit tests (mock model, no GPU or Ollama needed) |

## Reproduce

### 1. Set up and run the tests

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt   # on Linux/macOS: .venv/bin/python
.venv/Scripts/python -m pip install -e .
.venv/Scripts/python -m pytest -q
```

### 2. Development runs (Kaggle, 2x T4 GPU)

Import [`deploy/kaggle_run.ipynb`](deploy/kaggle_run.ipynb) into Kaggle, set the accelerator to GPU T4 x2 and Internet on, and run it. It installs Ollama 0.40.16, pulls the models, runs the matrix in process and writes a results zip. Details: [`deploy/README.md`](deploy/README.md).

Any machine with Ollama can run the same matrix:

```bash
python -m llmsec.harness.run --models qwen3-1.7b --env local --defense none
python -m llmsec.harness.run --models qwen3-1.7b --env local --defense all
```

### 3. Cloud runs (AWS EC2)

[`deploy/AWS_GUIDE.md`](deploy/AWS_GUIDE.md) gives every click and command. In short:

1. Launch an `m7i-flex.large` instance on the AWS Free plan.
2. Run [`deploy/aws_setup.sh`](deploy/aws_setup.sh). It starts the same Docker Compose stack (app server + Ollama), protected by an API key and a security group.
3. Attack it from another machine over HTTP with the same trial ids:

```bash
python -m llmsec.harness.cloud --target http://<instance-ip>:8000 --status
python -m llmsec.harness.cloud --target http://<instance-ip>:8000
```

The run plan (6 blocks) is in [`configs/cloud.yaml`](configs/cloud.yaml).

### 4. Regenerate tables, figures and the paper

```bash
python -m llmsec.harness.report results/kaggle --defense-table
python scripts/cloud_compare.py      # reports/cloud_aws.md, paper/cloud_table.tex, paper/cloud_numbers.tex
python scripts/make_figures.py       # reports/figs/*.png, paper/figs/*.pdf
cd paper && pdflatex main && bibtex main && pdflatex main && pdflatex main
```

Every number in the paper's cloud section is a macro written by `cloud_compare.py`, so the text, the table and the data always agree.

## Ethics

All attacks targeted only our own applications, mock tools and locally served open models. No third-party service was attacked.

## Licenses

The Elsevier CAS class files in `paper/` (`cas-dc.cls`, `cas-common.sty`) and `elsarticle-num-names.bst` are distributed under the LaTeX Project Public License (see `paper/ELS-CAS-README.txt` and `paper/manifest.txt`). The reviewed papers themselves are not included; `literature/` holds only our extracted records and page references.

## Project history

The full working history (study notes for the authors, run logs, planning files and the earlier IEEE-format draft) is kept on the [`archive/full-project`](https://github.com/MuhammadTalha57/CEP/tree/archive/full-project) branch.
