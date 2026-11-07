# Citable facts for the paper (built from data/papers/*.json; every row has a PDF page ref)

| Paper | Fact | Number | PDF page |
|---|---|---|---|
| P01 (ACM CCS 2024) | Average ASR / PAC on MT-Bench with Mistral-7B | 90.8% / 83.4% | 3 |
| P01 (ACM CCS 2024) | Manual attacks on Mistral-7B MT-Bench (ASR): naive 7.3, escape 12.8, content-ignore 7.8, fake-completion 7.7, combined 12.8, fake-reasoning 16.3 | 7.3%-16.3% vs 90.8% | 8 |
| P01 (ACM CCS 2024) | Known-answer detection fails to flag the attack | FNR 100% (MT-Bench), 90% (LLMBar) | 13 |
| P01 (ACM CCS 2024) | Perplexity (PPL/PPL-W) detection misses many attacks | FNR 40-80% MT-Bench; 60-90% LLMBar | 13 |
| P02 (ACM AISec 2024) | Triggers for Llama-3 reach ~95% attack success | ~95% | 2 |
| P02 (ACM AISec 2024) | Neural Exec at least 2x best handcrafted baseline; mean accuracy 91% across models | 91% | 8 |
| P02 (ACM AISec 2024) | RAG chunk size 500 chars: trigger persistence | 80% average | 9 |
| P03 (ACM CODASPY 2025) | PromptShield Llama-3.1-8B vs DeBERTa-184M vs PromptGuard (TPR@FPR1%) | 94.80% / 43.22% / 12.78% | 9 |
| P03 (ACM CODASPY 2025) | TPR@FPR0.1%: Llama-3.1-8B 65.33%, DeBERTa-184M 31.45%, PromptGuard 9.39%; AUC 0.998 / 0.976 / 0.874 | see claim | 9 |
| P03 (ACM CODASPY 2025) | Bigger base models detect better | see Table 5 | 9 |
| P04 (ACM Web Conference (WWW) 2026) | Macro-avg ASR by defense: Vanilla 24.9, Sanitized 13.1, Normalized 21.3, All defenses 4.7 (95% CIs reported) | 24.9 -> 4.7 | 3 |
| P04 (ACM Web Conference (WWW) 2026) | Real-web static ASR: Vanilla 22.7, Normalized 19.1, Sanitized 12.0, All 4.3; adaptive: 28.9, 22.2, 15.8, 5.4 | 22.7->4.3 / 28.9->5.4 | 4 |
| P04 (ACM Web Conference (WWW) 2026) | ASR detector validated on 1200 generations | P=0.92 R=0.89 F1=0.90 kappa=0.84 | 3 |
| P04 (ACM Web Conference (WWW) 2026) | Utility cost of Sanitized+Normalized | answerability -1.8pp / -2.2pp | 3 |
| P05 (LM-SHIELD '26 workshop (ACM), Bangalore) | Prompt-injection vulnerability: qwen3:1.7b 71.3%, gemma3:1b 62.8%, DeepSeek-R1:1.5b 34.0%, Llama3.2:1b 30.9%; six larger models 0% | 71.3/62.8/34.0/30.9/0 | 7 |
| P05 (LM-SHIELD '26 workshop (ACM), Bangalore) | Jailbreak (74 prompts) vulnerable counts: gemma3:1b 49, Llama3.2:3b 36, qwen3:1.7b 8, Llama3.2:1b 7, DeepSeek-R1:1.5b 1, qwen3:4b 0 | 49/36/8/7/1/0 | 9 |
| P05 (LM-SHIELD '26 workshop (ACM), Bangalore) | 0% injection vulnerability does not imply jailbreak robustness | Llama3.2:3B 0% injection vs 69.2% jailbreak | 11 |
| P05 (LM-SHIELD '26 workshop (ACM), Bangalore) | Defence ranking: Self-Defence best; Input Filtering weakest (Llama3.2 3B ~42% vulnerable); System Prompt inconsistent (~39% for Llama3.2 3B); Vector 25-30%; Voting 13-15% on small models | best 1.2% (self-defence) | 10 |
| P05 (LM-SHIELD '26 workshop (ACM), Bangalore) | Weak judge models weaken Self-Defence | up to 49.7% unsafe outputs approved | 11 |
| P06 (IEEE FLLM 2025) | Precision/Recall/F1: DistilBERT 0.96/0.92/0.92; DeBERTa-v3 0.95/0.91/0.93; RoBERTa-large 0.93/0.89/0.91; BERT-base 0.91/0.88/0.89; RF 0.89/0.86/0.87; SVM 0.87/0.83/0.85; LR 0.84/0.80/0.82; rule-based 0.75/0.70/0.72 | see claim | 5 |
| P06 (IEEE FLLM 2025) | Per attack type F1: leakage 0.95, privilege escalation 0.92, output manipulation 0.93, jailbreak 0.89 | 0.89-0.95 | 6 |
| P06 (IEEE FLLM 2025) | Chosen for latency and cost | ~220 ms inference; ~60% cost reduction (text claim, no table) | 5 |
| P07 (IEEE SCECS 2026) | Edge detector accuracy RF: MiniLM 0.9533, OpenAI embeddings 0.9723 | 0.9533 / 0.9723 | 3 |
| P07 (IEEE SCECS 2026) | Risk split MiniLM: low 56.69%, mid 30.49%, high 12.82% | 56.69/30.49/12.82 | 3 |
| P07 (IEEE SCECS 2026) | Q-TRiG keeps cloud waiting and p99 low across load 5-45 req/s while COR, EBG, S-TRiG diverge (shown in figures; no numeric speedups in text) | qualitative | 4 |
| P08 (IEEE SaTML 2026) | Solves 77% of AgentDojo tasks with security guarantees vs 84% undefended | 77% vs 84% | 1 |
| P08 (IEEE SaTML 2026) | Token overhead for median task | 2.82x input, 2.73x output | 11 |
| P08 (IEEE SaTML 2026) | Utility drop examples (native -> CaMeL): Claude 4 Sonnet 83.5% -> 70.1%; Gemini 2.5 Flash 55.7% -> 35.1% | -13.4 / -20.6 pts | 16 |
| P09 (IEEE TDSC 2026) | Throughput cloud-only -> BUUAS (tokens/s): Qwen-4B 86.97->108.73; Qwen-7B 69.49->88.44; Qwen-14B 50.32->53.13 | see claim | 9 |
| P09 (IEEE TDSC 2026) | Static-mal, balanced set: GMDRA Acc 0.860 / F1 0.865 vs BUUAS Acc 0.705 / F1 0.752 / Recall 0.941; no-detection Acc 0.500 | see claim | 10 |
| P09 (IEEE TDSC 2026) | Alt(2B-2M): BUUAS Acc 0.686, Recall 0.882, F1 0.722 vs GMDRA 0.677 / 0.523 / 0.616 | see claim | 10 |
| P10 (IEEE ICTIIA 2026) | NPC jailbreak rate, 80 prompts: GPT-4o-mini 28.75% -> 26.25% (McNemar p=0.75); Llama-3.1-8B 26.25% -> 18.75% (p=0.26); 0/20 false positives | not significant | 4-5 |
| P10 (IEEE ICTIIA 2026) | Ablation (10 seeds): enforcement blocks 17.6 -> 3.1 (82%); profile fit 3.80 -> 4.10; PCS 0.675 -> 0.735 | 82% | 5 |
| P10 (IEEE ICTIIA 2026) | Mean latency delta: GPT-4o-mini +61.1 ms; Llama-3.1-8B -19.2 ms | +61.1 / -19.2 ms | 4 |
| P11 (IEEE SmartCloud 2025) | Hash+embedding chunk detector: F1 > 0.94 on TEMPLATE and NONE (W=10, theta 0.62-0.70); up to 0.96+ on BOTH/NONE (theta 0.66, W 8-10); 2000 generated prompts; no external baseline | F1 0.94-0.96 (figure-read) | 5-6 |
| P11 (IEEE SmartCloud 2025) | Blockchain log on Sepolia: sign&publish 1.375 s, confirmation 8.670 s, gas 22280 | see claim | 4 |
| P12 (IEEE ICAIC 2026) [self-reported; internally inconsistent, cite as claim only] | Full SPEP ASR: AWS 8%, GCP 6%, Azure 7% (baseline 78% stated only in conclusion); +42 ms per inference | 78% -> <8% | 5 |
| P13 (IEEE ICHORA 2026) | Mean ASR over 6 local models x 3 PDF vectors; 400 PDFs, 2,400 trials | 47.78% | 1, 5 |
| P13 (IEEE ICHORA 2026) | ASR by model (white/tiny/metadata mean): Gemma-3 96.33, Llama-3 61.00, Phi-4 56.00, MedLlama-2 35.33, Qwen-3 29.33, Meditron 8.67 | 8.67-96.33% | 5 |
| P13 (IEEE ICHORA 2026) | ASR by vector (mean of 6 models): white-text 50.83, tiny-font 49.33, metadata 43.17; 0.00% tracer hits on benign documents | 43.17-50.83% | 5 |
