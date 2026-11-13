# Run guide

All commands run from the repo root. Windows: use Git Bash or PowerShell (paths below are PowerShell-compatible).

## 1. One-time setup (laptop)

```bash
python -m venv .venv
.venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pip install -e .
.venv/Scripts/python -m pytest -q          # all tests must pass (mock model, no Ollama needed)
```

Install Ollama for Windows from ollama.com, then pull the candidate models (one at a time fits in 7.4 GB RAM):

```bash
ollama pull qwen3:1.7b
ollama pull llama3.2:3b
ollama pull gemma3:1b
ollama --version
```

Record the Ollama version in STATE.md. `OLLAMA_URL` defaults to `http://localhost:11434/v1`; to change it, copy `.env.example` to `.env` and set the variable in your shell.

## 1b. Model runs on Kaggle (chosen 13 Nov; the laptop only runs code and mock tests)

Notebook: `deploy/kaggle_run.ipynb`. It installs Ollama on Kaggle's free GPU, pulls the same models, clones
this repo (branch `master`, so push first), runs the pilot or the experiments in-process, and writes
`results_<env>.zip` to the Output tab.

1. kaggle.com → Create → New Notebook → File → Import Notebook → upload `deploy/kaggle_run.ipynb`.
2. Settings: Accelerator **GPU T4 x2** (or P100), Internet **On** (phone verification needed once).
3. Pilot: keep `MODE = "pilot"`, Run All (~minutes). Long runs: `MODE = "run"`, then *Save Version → Save & Run All*.
4. Download the zip, unzip it **in the repo root**, commit `results/` and `reports/pilot_*.md`.
5. Interrupted run: upload the last zip as a Kaggle Dataset, attach it, re-run; finished trials are skipped.

Results land in `results/kaggle/` (experiments) and `results/kaggle-pilot/` (pilot). The environment
(GPU, Ollama version, commit) is logged in `results/<env>/environment_*.json`.

## 2. Timing pilot on the laptop (optional; the pilot normally runs on Kaggle, see 1b)

```bash
.venv/Scripts/python -m llmsec.harness.pilot --models qwen3-1.7b llama3.2-3b gemma3-1b
```

Takes roughly 21 trials per model per app. It writes `reports/pilot_local-pilot.md` (seconds per trial, estimated full-matrix hours, tool-call support, thinking check) and logs in `results/local-pilot/`. Commit both. Claude sizes the final matrix from this file.

Close other heavy apps (browser tabs, Docker Desktop) while running: RAM is the bottleneck.

## 3. Local experiment runs (Stage 5)

In-process (fastest locally, no server):

```bash
.venv/Scripts/python -m llmsec.harness.run --models qwen3-1.7b --env local --defense none
```

Useful flags: `--apps chatbot rag`, `--variants 10` (reduced n), `--cells T2@C0 U`, `--limit 20`.
Runs resume automatically: re-run the same command after an interruption.
Logs: `results/local/<model>/<app>__<defense>.jsonl`. Never edit them by hand.

Summary table:

```bash
.venv/Scripts/python -m llmsec.harness.report results/local --out reports/results_local.md
```

Optional, the same path as the cloud (HTTP, black-box):

```bash
set APP_API_KEY=dev-key     # PowerShell: $env:APP_API_KEY="dev-key"
.venv/Scripts/python -m uvicorn llmsec.apps.server:app --port 8000
.venv/Scripts/python -m llmsec.harness.run --target http://localhost:8000 --env local-http --models qwen3-1.7b
```

## 4. Docker stack (used on AWS; optional locally)

```bash
docker compose up -d --build
docker compose exec ollama ollama pull qwen3:1.7b
curl http://localhost:8000/health
```

`APP_API_KEY` must be set in `.env`. GPU hosts add `-f deploy/docker-compose.gpu.yml`.

## 5. AWS (Stage 7) — outline, detailed commands come in Stage 7

1. Before launching anything: AWS Budgets alert (~$30) and check the EC2 GPU instance quota.
2. One EC2 instance (GPU class if the quota allows, otherwise CPU-optimized), security group: port 22 and 8000 open **only to your IP**.
3. Install Docker, copy the repo, `docker compose up -d --build`, pull the same models.
4. From the laptop: `python -m llmsec.harness.run --target http://<ec2-ip>:8000 --env aws ...`
5. **Stop the instance** at the end of every session; record hours in STATE.md.
