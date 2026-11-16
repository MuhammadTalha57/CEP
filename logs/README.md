# Logs

Run logs for the instructor. Every trial's full record (payload, output, timing, verdict) is in `results/` and is the primary evidence. These files show how the runs were carried out.

| File | What it is | Where it came from |
|---|---|---|
| `aws/cloud_run.log` | Laptop-side log of the cloud runner on 16 Nov 2026 (06:30–08:31 UTC): blocks 4–6, progress every 10 trials, warm-up times | Copy of `results/aws/cloud_run.log`, written by `llmsec.harness.cloud` (the `_Tee` class). Blocks 1–3 ran on 15 Nov, before this log existed; their records are in `results/aws/*/*.jsonl` |
| `laptop/powershell_history.txt` | The project commands typed on the laptop (health checks, cloud runner) | Filtered from the PowerShell history. Unrelated commands were removed and the API key was redacted |

Other run metadata already in the repository:

- `results/kaggle/environment_*.json`: GPU, Ollama version and model digests for each Kaggle session.
- `results/aws/environment_aws.json`: the same information for the EC2 instance.
- `results/excluded/kaggle/qwen3-4b-thinking/README.md`: why the first qwen3:4b run was excluded.

## Timeline

| When (UTC) | What | Evidence |
|---|---|---|
| 13–15 Nov | Kaggle sessions: pilot, baseline (2 sessions), defense runs; 19,020 trials | `results/kaggle/` |
| 15 Nov 09:45 | AWS cloud run started (blocks 1–3 finished normally) | `results/aws/*/*.jsonl` timestamps |
| 15 Nov 12:15 – 16 Nov ~06:00 | Laptop-to-server network interruption; 341 trials logged as connection errors (339 `ConnectTimeout`, 2 `ConnectError`) (invalid, excluded) | error records in `results/aws`; an SSH check on 16 Nov showed the server up for 21 h, both containers running and no OOM events |
| 16 Nov 06:30 – 08:31 | Resumed with `--blocks 4 5 6 --retry-invalid`; all 6 blocks reached 1,350/1,350 valid trials | `aws/cloud_run.log` |

Server-side container logs and the Kaggle notebook logs were not kept; the per-trial records in `results/` are the evidence for every run.
