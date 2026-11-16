# 9. Replication guide: every command, in order

Commands are given for **Windows PowerShell** (laptop), **bash** (Kaggle / EC2), as noted. Replace `<KEY>` with your API key and `<IP>` with the EC2 public IP.

## Step 0: Prerequisites

| Tool | Why | Check |
|---|---|---|
| Git | get the code | `git --version` |
| Python 3.12+ | harness, apps, tests | `python --version` |
| A Kaggle account with phone verification | free GPU, Internet in notebooks | kaggle.com → Settings |
| An AWS account (Free plan) | cloud deployment | console.aws.amazon.com |
| OpenSSH client (built into Windows) | connect to EC2 | `ssh -V` |
| LaTeX (MiKTeX/TeX Live) **or** Overleaf | compile the paper | `pdflatex --version` |
| Docker (optional on the laptop) | run the stack locally | `docker --version` |

## Step 1: Get the code and run the tests (laptop, about 5 min)

```powershell
git clone https://github.com/MuhammadTalha57/CEP.git
cd CEP
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m pytest -q
```

The expected output is `97 passed`. The tests use a **mock LLM**, so no model or GPU is needed.

Quick demo with the mock model (a few seconds; writes to a scratch folder):

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python -m llmsec.harness.run --models mock --apps chatbot --variants 1 --env demo --out demo_results
.\.venv\Scripts\python -m llmsec.harness.report demo_results
```

## Step 2: Literature stages (already done; how they were produced)

| Stage | What was done | Files |
|---|---|---|
| Extract | Each PDF in `my_papers/` read once, following `skills/01-extract.md` | `data/papers/Pxx.json`, `data/ledger.csv` |
| Citations / artifacts | GitHub Action "Fetch metrics" (Actions tab → Fetch metrics → Run workflow), or locally: `python scripts/fetch_metrics.py` | `data/citations.csv`, `data/artifacts.csv` |
| Rank | `skills/02-rank-exclude.md` scoring | `reports/ranking.md` |
| Gaps | `skills/03-gap-and-design.md` | `reports/gaps.md` |
| Design | approved design | `reports/design.md` |

## Step 3: Kaggle runs (development environment)

1. On kaggle.com: **Create → New Notebook → File → Import Notebook →** choose `deploy/kaggle_run.ipynb`.
2. In the right panel: **Accelerator: GPU T4 x2**, **Internet: On**.
3. Edit the **CONFIG** cell, then **Save Version → Save & Run All (Commit)**.
4. When it finishes, open the version's **Output** tab, download `results_kaggle.zip`, unzip it in the repo root and commit.

| Run | CONFIG values | Input to attach |
|---|---|---|
| Pilot (timing) | `MODE="pilot"`, `MODELS=[…]` | none |
| Baseline | `MODE="run"`, `MODELS=["qwen3-1.7b","llama3.2-3b","gemma3-1b","qwen3-4b-instruct"]`, `DEFENSE="none"` | none (or the previous zip to resume) |
| Defenses, session A | `MODELS=["qwen3-1.7b","gemma3-1b"]`, `DEFENSE="all"` | previous results as a Kaggle Dataset (Add Input) |
| Defenses, session B | `MODELS=["llama3.2-3b","qwen3-4b-instruct"]`, `DEFENSE="all"` | same Dataset |

The notebook itself runs these commands (for reference):

```bash
curl -fsSL https://ollama.com/install.sh | sh                      # install Ollama
OLLAMA_KEEP_ALIVE=24h OLLAMA_NUM_PARALLEL=1 ollama serve &
git clone --depth 1 -b master https://github.com/MuhammadTalha57/CEP.git /tmp/CEP
pip install -q -r /tmp/CEP/requirements.txt && pip install -q -e /tmp/CEP
cd /tmp/CEP && python -m pytest -q                                   # must pass
ollama pull qwen3:1.7b; ollama pull llama3.2:3b; ollama pull gemma3:1b; ollama pull qwen3:4b-instruct-2507-q4_K_M
python -m llmsec.harness.run --models qwen3-1.7b llama3.2-3b gemma3-1b qwen3-4b-instruct \
       --env kaggle --defense none --workers 1          # baseline; use --defense all for the defense runs
```

Runner options worth knowing:

| Option | Meaning |
|---|---|
| `--apps chatbot rag agent` | Only these apps |
| `--cells T2@C0 U` | Only these cells (`U` = clean tasks) |
| `--variants 10` | Fewer variants per cell |
| `--defense all` | Every defense listed for each app in `configs/experiment.yaml` |
| `--retry-invalid` | Redo trials that ended in an error |
| `--target http://<IP>:8000` | Attack a running server instead of calling in process |

## Step 4: Reports from the Kaggle logs (laptop)

```powershell
$env:PYTHONPATH = "src"
.\.venv\Scripts\python -m llmsec.harness.report results/kaggle                                  # every cell: ASR, CI, latency
.\.venv\Scripts\python -m llmsec.harness.report results/kaggle --defense-table                  # per model x app x defense
.\.venv\Scripts\python -m llmsec.harness.report results/kaggle --compare-defense none layered   # paired McNemar per cell
```

## Step 5: AWS deployment (cloud environment)

Full click-by-click guide: `deploy/AWS_GUIDE.md`. The commands:

```powershell
# laptop: API key, key-file permission, connect
-join ((48..57)+(97..122) | Get-Random -Count 32 | ForEach-Object {[char]$_})
icacls "$HOME\Downloads\cep-key.pem" /inheritance:r /grant:r "$($env:USERNAME):R"
ssh -i "$HOME\Downloads\cep-key.pem" ubuntu@<IP>
```

```bash
# on the EC2 server: one-time setup (about 10 min)
curl -fsSL https://raw.githubusercontent.com/MuhammadTalha57/CEP/master/deploy/aws_setup.sh -o aws_setup.sh
bash aws_setup.sh <KEY>
# health and diagnostics at any time
cd ~/CEP && sudo docker compose ps && curl -s localhost:8000/health; echo
uptime; free -h; df -h /
sudo dmesg | grep -i -E "out of memory|oom|killed process" | tail -5
```

```powershell
# laptop: run the cloud plan against the server (same trial ids as Kaggle)
cd "<repo folder>"
mkdir results\aws -Force
scp -i "$HOME\Downloads\cep-key.pem" ubuntu@<IP>:environment_aws.json results\aws\environment_aws.json
$env:APP_API_KEY = "<KEY>"; $env:PYTHONPATH = "src"
curl.exe --max-time 10 http://<IP>:8000/health
.\.venv\Scripts\python -m llmsec.harness.cloud --dry-run                       # list blocks and trial counts
.\.venv\Scripts\python -m llmsec.harness.cloud --status                        # progress per block
.\.venv\Scripts\python -m llmsec.harness.cloud --target http://<IP>:8000       # run all blocks (resumes)
.\.venv\Scripts\python -m llmsec.harness.cloud --target http://<IP>:8000 --blocks 4 5 6 --retry-invalid
```

## Step 6: Comparison, figures and logs (laptop)

```powershell
.\.venv\Scripts\python scripts\cloud_compare.py      # -> reports/cloud_aws.md, paper/cloud_table.tex
.\.venv\Scripts\python scripts\make_figures.py       # -> docs/figs/*.png, paper/cas/figs/*.pdf
```

Collecting logs before shutting down AWS:

```bash
# on the server
cd ~/CEP && sudo docker compose logs --no-color --timestamps > ~/server_logs.txt
```

```powershell
# laptop
scp -i "$HOME\Downloads\cep-key.pem" ubuntu@<IP>:server_logs.txt logs\aws\server_logs.txt
Copy-Item (Get-PSReadLineOption).HistorySavePath logs\laptop\powershell_history.txt
```

Then in the AWS console: **EC2 → Instances → select → Instance state → Terminate**, and check that *Volumes* and *Elastic IPs* are empty.

## Step 7: Compile the paper

```powershell
cd paper\cas
pdflatex main ; bibtex main ; pdflatex main ; pdflatex main
```

On Overleaf: upload the whole `paper/cas/` folder (it includes the els-cas class files and `figs/`), set the main document to `main.tex`, and compile with pdfLaTeX.
