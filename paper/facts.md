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