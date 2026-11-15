# Defense results: Kaggle development environment

**Status:** complete, 15 Nov 2026. 4 models × each app's defense list (configs/experiment.yaml), 30 variants per cell, about 20,000 trials.
- Code commit 48cdf39. Two parallel Kaggle sessions on 14 Nov: (qwen3-1.7b, gemma3-1b) and (llama3.2-3b, qwen3-4b-instruct).
- Same Ollama digests as the baseline (`results/kaggle/environment_run_*.json`). The baseline rows (`none`) are the files from reports/baseline_kaggle.md, unchanged.
- Regenerate: `python -m llmsec.harness.report results/kaggle --defense-table` (per model), and `--compare-defense none <d>` (per cell, paired McNemar).

**Defenses** (design.md §5; details in STATE.md 13 Nov):
- **D1** ProtectAI DeBERTa-v3 prompt-injection detector, threshold 0.85 (P06 p4), on the user message, retrieved chunks and tool outputs.
- **D2** sanitize: normalization, then visible text only from HTML/PDF.
- **D3** spotlighting + prompt hardening: wraps untrusted data in tags; App A gets hardening only.
- **D4** tool policy, a simplified CaMeL rule (P08 p1, p4): send_email/delete_file arguments must appear in the user's request.
- **Layered** [OURS]: per channel, D2 → D1 on documents, D1 on the user message, D3 + D4 on tool outputs, plus an output guard (secret / allow-listed URLs).

Quality checks:
- 0 duplicate trials.
- 6 invalid trials out of about 20,000: qwen3-4b-instruct agent, Ollama's llama-server returned HTTP 500. They are left out of the denominators.
- 13 `max_steps` agent errors.
- Empty outputs only for qwen3-1.7b, at the same level as its baseline.
- **False positives: 0.** No clean (utility) trial was blocked by D1 or by the layered defense in any app.

## 1. Per model (attack cells pooled)

ASR = attack success over all attack trials of the app. Utility = clean tasks answered correctly. McNemar = exact test against `none`, paired on trial id (P10 p4).

| model | app | defense | ASR k/n | ASR % [95% CI] | utility % | invalid | mean s | McNemar p vs none |
|---|---|---|---|---|---|---|---|---|
| gemma3-1b | chatbot | d1_detector | 10/240 | 4.2 [2.3–7.5] | 86.7 | 0 | 0.18 | 8.4e-53 |
| gemma3-1b | chatbot | d3_spotlight | 192/240 | 80.0 [74.5–84.6] | 90.0 | 0 | 0.51 | 0.2 |
| gemma3-1b | chatbot | layered | 0/240 | 0.0 [0.0–1.6] | 90.0 | 0 | 0.18 | 8.2e-56 |
| gemma3-1b | chatbot | none | 184/240 | 76.7 [70.9–81.6] | 86.7 | 0 | 0.41 | – |
| gemma3-1b | rag | d1_detector | 28/480 | 5.8 [4.1–8.3] | 100.0 | 0 | 0.91 | 7.1e-15 |
| gemma3-1b | rag | d2_sanitize | 54/480 | 11.2 [8.7–14.4] | 100.0 | 0 | 0.25 | 0.0021 |
| gemma3-1b | rag | d3_spotlight | 37/480 | 7.7 [5.6–10.4] | 100.0 | 0 | 0.23 | 4e-08 |
| gemma3-1b | rag | layered | 14/480 | 2.9 [1.7–4.8] | 100.0 | 0 | 0.88 | 3.6e-16 |
| gemma3-1b | rag | none | 76/480 | 15.8 [12.8–19.4] | 100.0 | 0 | 0.26 | – |
| llama3.2-3b | agent | d1_detector | 13/270 | 4.8 [2.8–8.1] | 96.7 | 0 | 2.63 | 0.0034 |
| llama3.2-3b | agent | d3_spotlight | 2/270 | 0.7 [0.2–2.7] | 100.0 | 0 | 1.69 | 4.8e-07 |
| llama3.2-3b | agent | d4_toolpolicy | 0/270 | 0.0 [0.0–1.4] | 96.7 | 0 | 1.92 | 1.2e-07 |
| llama3.2-3b | agent | layered | 0/270 | 0.0 [0.0–1.4] | 100.0 | 0 | 1.84 | 1.2e-07 |
| llama3.2-3b | agent | none | 24/270 | 8.9 [6.0–12.9] | 96.7 | 0 | 1.62 | – |
| llama3.2-3b | chatbot | d1_detector | 0/240 | 0.0 [0.0–1.6] | 96.7 | 0 | 0.33 | 0.12 |
| llama3.2-3b | chatbot | d3_spotlight | 18/240 | 7.5 [4.8–11.5] | 96.7 | 0 | 0.34 | 0.00052 |
| llama3.2-3b | chatbot | layered | 0/240 | 0.0 [0.0–1.6] | 96.7 | 0 | 0.21 | 0.12 |
| llama3.2-3b | chatbot | none | 4/240 | 1.7 [0.6–4.2] | 96.7 | 0 | 0.29 | – |
| llama3.2-3b | rag | d1_detector | 83/480 | 17.3 [14.2–20.9] | 100.0 | 0 | 1.13 | 4.9e-48 |
| llama3.2-3b | rag | d2_sanitize | 152/480 | 31.7 [27.7–36.0] | 100.0 | 0 | 0.39 | 4.7e-16 |
| llama3.2-3b | rag | d3_spotlight | 180/480 | 37.5 [33.3–41.9] | 100.0 | 0 | 0.54 | 1.2e-12 |
| llama3.2-3b | rag | layered | 50/480 | 10.4 [8.0–13.5] | 100.0 | 0 | 1.15 | 7.9e-50 |
| llama3.2-3b | rag | none | 255/480 | 53.1 [48.7–57.5] | 100.0 | 0 | 0.38 | – |
| qwen3-1.7b | agent | d1_detector | 17/270 | 6.3 [4.0–9.9] | 90.0 | 0 | 5.30 | 3.6e-12 |
| qwen3-1.7b | agent | d3_spotlight | 29/270 | 10.7 [7.6–15.0] | 83.3 | 0 | 5.17 | 0.00014 |
| qwen3-1.7b | agent | d4_toolpolicy | 0/270 | 0.0 [0.0–1.4] | 90.0 | 0 | 5.40 | 2.8e-17 |
| qwen3-1.7b | agent | layered | 0/270 | 0.0 [0.0–1.4] | 83.3 | 0 | 5.34 | 2.8e-17 |
| qwen3-1.7b | agent | none | 56/270 | 20.7 [16.3–26.0] | 90.0 | 0 | 5.42 | – |
| qwen3-1.7b | chatbot | d1_detector | 7/240 | 2.9 [1.4–5.9] | 90.0 | 0 | 0.50 | 1.6e-58 |
| qwen3-1.7b | chatbot | d3_spotlight | 168/240 | 70.0 [63.9–75.4] | 93.3 | 0 | 1.71 | 1.4e-05 |
| qwen3-1.7b | chatbot | layered | 0/240 | 0.0 [0.0–1.6] | 90.0 | 0 | 0.37 | 1.2e-60 |
| qwen3-1.7b | chatbot | none | 200/240 | 83.3 [78.1–87.5] | 90.0 | 0 | 1.58 | – |
| qwen3-1.7b | rag | d1_detector | 48/480 | 10.0 [7.6–13.0] | 100.0 | 0 | 2.15 | 3.9e-38 |
| qwen3-1.7b | rag | d2_sanitize | 118/480 | 24.6 [20.9–28.6] | 100.0 | 0 | 1.46 | 2e-11 |
| qwen3-1.7b | rag | d3_spotlight | 119/480 | 24.8 [21.1–28.8] | 100.0 | 0 | 1.48 | 9.4e-18 |
| qwen3-1.7b | rag | layered | 14/480 | 2.9 [1.7–4.8] | 100.0 | 0 | 2.09 | 1.9e-52 |
| qwen3-1.7b | rag | none | 201/480 | 41.9 [37.5–46.3] | 100.0 | 0 | 1.54 | – |
| qwen3-4b-instruct | agent | d1_detector | 57/270 | 21.1 [16.7–26.4] | 100.0 | 0 | 3.32 | 3.1e-15 |
| qwen3-4b-instruct | agent | d3_spotlight | 14/267 | 5.2 [3.1–8.6] | 100.0 | 3 | 3.30 | 2.5e-27 |
| qwen3-4b-instruct | agent | d4_toolpolicy | 0/270 | 0.0 [0.0–1.4] | 100.0 | 0 | 3.07 | 6e-36 |
| qwen3-4b-instruct | agent | layered | 0/267 | 0.0 [0.0–1.4] | 100.0 | 3 | 3.53 | 4.8e-35 |
| qwen3-4b-instruct | agent | none | 118/270 | 43.7 [37.9–49.7] | 96.7 | 0 | 6.02 | – |
| qwen3-4b-instruct | chatbot | d1_detector | 0/240 | 0.0 [0.0–1.6] | 100.0 | 0 | 0.21 | 1 |
| qwen3-4b-instruct | chatbot | d3_spotlight | 0/240 | 0.0 [0.0–1.6] | 100.0 | 0 | 0.64 | 1 |
| qwen3-4b-instruct | chatbot | layered | 0/240 | 0.0 [0.0–1.6] | 100.0 | 0 | 0.22 | 1 |
| qwen3-4b-instruct | chatbot | none | 0/240 | 0.0 [0.0–1.6] | 100.0 | 0 | 0.92 | – |
| qwen3-4b-instruct | rag | d1_detector | 113/480 | 23.5 [20.0–27.5] | 100.0 | 0 | 1.07 | 3.5e-60 |
| qwen3-4b-instruct | rag | d2_sanitize | 198/480 | 41.2 [36.9–45.7] | 100.0 | 0 | 0.42 | 3.2e-19 |
| qwen3-4b-instruct | rag | d3_spotlight | 174/480 | 36.2 [32.1–40.6] | 100.0 | 0 | 0.49 | 5.3e-41 |
| qwen3-4b-instruct | rag | layered | 57/480 | 11.9 [9.3–15.1] | 100.0 | 0 | 1.05 | 4.2e-73 |
| qwen3-4b-instruct | rag | none | 322/480 | 67.1 [62.8–71.1] | 100.0 | 0 | 0.85 | – |

## 2. Per cell, pooled over models (which defense stops which attack)

### App chatbot: pooled over models, k/n (%)

| cell | none | d1_detector | d3_spotlight | layered |
|---|---|---|---|---|
| T1@C0 | 53/120 (44%) | 10/120 (8%) | 54/120 (45%) | 0/120 (0%) |
| T2@C0 | 51/120 (42%) | 0/120 (0%) | 59/120 (49%) | 0/120 (0%) |
| T3@C0 | 56/120 (47%) | 4/120 (3%) | 52/120 (43%) | 0/120 (0%) |
| T4@C0 | 53/120 (44%) | 1/120 (1%) | 49/120 (41%) | 0/120 (0%) |
| T5@C0 | 48/120 (40%) | 0/120 (0%) | 48/120 (40%) | 0/120 (0%) |
| T6@C0 | 54/120 (45%) | 0/120 (0%) | 46/120 (38%) | 0/120 (0%) |
| T7@C0 | 56/120 (47%) | 0/120 (0%) | 58/120 (48%) | 0/120 (0%) |
| H2@C0 | 17/120 (14%) | 2/120 (2%) | 12/120 (10%) | 0/120 (0%) |
| U (utility) | 112/120 (93%) | 112/120 (93%) | 114/120 (95%) | 113/120 (94%) |

### App rag: pooled over models, k/n (%)

| cell | none | d1_detector | d2_sanitize | d3_spotlight | layered |
|---|---|---|---|---|---|
| T1@C1 | 60/120 (50%) | 57/120 (48%) | 67/120 (56%) | 41/120 (34%) | 43/120 (36%) |
| T2@C1 | 54/120 (45%) | 15/120 (12%) | 67/120 (56%) | 38/120 (32%) | 15/120 (12%) |
| T3@C1 | 60/120 (50%) | 53/120 (44%) | 69/120 (58%) | 28/120 (23%) | 26/120 (22%) |
| T4@C1 | 76/120 (63%) | 27/120 (22%) | 80/120 (67%) | 56/120 (47%) | 25/120 (21%) |
| T5@C1 | 59/120 (49%) | 18/120 (15%) | 64/120 (53%) | 28/120 (23%) | 12/120 (10%) |
| T6@C1 | 36/120 (30%) | 10/120 (8%) | 42/120 (35%) | 19/120 (16%) | 5/120 (4%) |
| T7@C1 | 66/120 (55%) | 5/120 (4%) | 67/120 (56%) | 38/120 (32%) | 4/120 (3%) |
| T7@C2 | 62/120 (52%) | 7/120 (6%) | 0/120 (0%) | 33/120 (28%) | 0/120 (0%) |
| T7@C3 | 65/120 (54%) | 6/120 (5%) | 0/120 (0%) | 35/120 (29%) | 0/120 (0%) |
| T7@C4 | 8/120 (7%) | 3/120 (2%) | 66/120 (55%) | 4/120 (3%) | 5/120 (4%) |
| T7@C5 | 47/120 (39%) | 2/120 (2%) | 0/120 (0%) | 25/120 (21%) | 0/120 (0%) |
| T7@C6 | 50/120 (42%) | 0/120 (0%) | 0/120 (0%) | 22/120 (18%) | 0/120 (0%) |
| T7@C7 | 57/120 (48%) | 9/120 (8%) | 0/120 (0%) | 36/120 (30%) | 0/120 (0%) |
| H1@C2 | 80/120 (67%) | 35/120 (29%) | 0/120 (0%) | 54/120 (45%) | 0/120 (0%) |
| H1@C5 | 68/120 (57%) | 24/120 (20%) | 0/120 (0%) | 51/120 (42%) | 0/120 (0%) |
| H3@C2+C4 | 6/120 (5%) | 1/120 (1%) | 0/120 (0%) | 2/120 (2%) | 0/120 (0%) |
| U (utility) | 120/120 (100%) | 120/120 (100%) | 120/120 (100%) | 120/120 (100%) | 120/120 (100%) |

### App agent: pooled over models, k/n (%)

| cell | none | d1_detector | d3_spotlight | d4_toolpolicy | layered |
|---|---|---|---|---|---|
| T1@C8 | 4/90 (4%) | 5/90 (6%) | 1/90 (1%) | 0/90 (0%) | 0/90 (0%) |
| T2@C8 | 23/90 (26%) | 8/90 (9%) | 3/90 (3%) | 0/90 (0%) | 0/90 (0%) |
| T3@C8 | 41/90 (46%) | 41/90 (46%) | 10/89 (11%) | 0/90 (0%) | 0/89 (0%) |
| T4@C8 | 15/90 (17%) | 12/90 (13%) | 3/88 (3%) | 0/90 (0%) | 0/88 (0%) |
| T5@C8 | 32/90 (36%) | 8/90 (9%) | 3/90 (3%) | 0/90 (0%) | 0/90 (0%) |
| T6@C8 | 2/90 (2%) | 1/90 (1%) | 0/90 (0%) | 0/90 (0%) | 0/90 (0%) |
| T7@C8 | 34/90 (38%) | 5/90 (6%) | 9/90 (10%) | 0/90 (0%) | 0/90 (0%) |
| T7@C9 | 41/90 (46%) | 3/90 (3%) | 14/90 (16%) | 0/90 (0%) | 0/90 (0%) |
| H2@C8 | 6/90 (7%) | 4/90 (4%) | 2/90 (2%) | 0/90 (0%) | 0/90 (0%) |
| U (utility) | 85/90 (94%) | 86/90 (96%) | 85/90 (94%) | 86/90 (96%) | 85/90 (94%) |

### Clean trials with any defense block (false positives)

| app | defense | blocked/n |
|---|---|---|
| agent | d1_detector | 0/90 |
| agent | layered | 0/90 |
| chatbot | d1_detector | 0/120 |
| chatbot | layered | 0/120 |
| rag | d1_detector | 0/120 |
| rag | layered | 0/120 |

## Findings (defenses)

1. **The layered defense works best in every app, at no utility cost.** Pooled over models:
   - Chatbot ASR goes from 40% to **0%** (0/960).
   - RAG ASR goes from 44% to **7%** (135/1,920).
   - Agent ASR goes from 24% to **0%** (0/807).
   - Pooled utility stays at 94–100%, within ±2 trials of `none`, and no clean trial was blocked.
   - The largest per-model utility drop is qwen3-1.7b agent with D3/layered: 27/30 → 25/30.

   | pooled ASR | none | D1 | D2 | D3 | D4 | layered |
   |---|---|---|---|---|---|---|
   | chatbot | 40.4% | 1.8% | – | 39.4% | – | **0.0%** |
   | RAG | 44.5% | 14.2% | 27.2% | 26.6% | – | **7.0%** |
   | agent | 24.4% | 10.7% | – | 5.6% | 0.0% | **0.0%** |
   - Every per-model reduction is significant (McNemar p < 1e-7), except where the model was already near 0 (llama3.2-3b chatbot, qwen3-4b-instruct chatbot).
2. **D1 (detector) is the strongest single defense against direct injection** (App A: 2.9–4.2% left on qwen3-1.7b and gemma3-1b). It is weaker for documents.
   - T1@C1, T3@C1 and T4@C1 still succeed at 48%, 44% and 22% in RAG.
   - Yet T1 in the chatbot drops from 44% to 8%. [INFERENCE] T1 (naive instruction) and T3 (fake completion) contain no override wording, so inside a document chunk surrounded by normal text they score below the 0.85 threshold.
   - In the agent, D1 misses T3 (fake completion) completely (46% → 46%).
3. **D2 (sanitize) removes every hidden carrier and nothing else.**
   - C2, C3, C5, C6, C7 and H1/H3 drop to **0%**.
   - Visible-text attacks (C1) are unchanged (50–67%).
   - **D2 alone makes the zero-width carrier much stronger: T7@C4 rises from 7% to 55%.** Its Unicode normalization deletes the zero-width characters, which repairs the payload for the model.
   - This is why the layered defense runs normalization *before* the detector: with that order, C4 falls to 4%. [OURS] Sanitizers that normalize text must be followed by detection, never used last.
4. **D3 (spotlighting) helps with documents and tools but not with direct injection.**
   - RAG: 44% → 27%. Agent: 24% → 6%.
   - In the chatbot, hardening alone does not help (40% → 39%), and for llama3.2-3b it *raises* leaks (1.7% → 7.5%, p = 0.0005).
   - [INFERENCE] The extra security text in the system prompt draws attention to the secret.
5. **D4 (tool policy) blocks every data-exfiltration tool call** (agent ASR 0% for all 3 tool models, 0/810), with utility unchanged (94–96%). This matches P08's result that a data-flow rule beats detection for tool agents. Our rule is simplified and only covers recipient and path arguments (limitation).
6. **The residual risk is visible-text injection in RAG.** Even with the layered defense, T1@C1 (36%), T3@C1 (22%) and T4@C1 (21%) still work, because none of our layers removes visible instructions that the detector scores below the threshold. A lower threshold or a second detector are future work. Changing the threshold now would be tuning on the test set.
7. **Latency cost:**
   - D1 runs on CPU and adds about 0.6 s per RAG trial (about 4 chunks scored).
   - A blocked chatbot input skips the LLM, so the layered chatbot is *faster* than no defense.
   - D3 and D4 add < 0.1 s.
   - The cloud comparison is in Stage 7.
