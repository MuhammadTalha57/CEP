# Excluded runs (kept for transparency, not used in any table)

`report.py` must be pointed at `results/<env>/`, never at `results/` as a whole, so these are never counted.

| Folder | Why excluded | Date |
|---|---|---|
| kaggle/qwen3-4b-thinking/ | Ollama tag `qwen3:4b` (ID 359d7dd4bcda) is Qwen3-4B-Thinking-2507, a thinking-only model that ignores `/no_think`. Its hidden reasoning used up `max_tokens` (300): 691/1020 outputs empty, so ASR was falsely near 0. Replaced by `qwen3-4b-instruct` (`qwen3:4b-instruct-2507-q4_K_M`). Files moved unchanged. | 14 Nov 2026 |
