# Citable facts for the paper (auto-built from data/papers/*.json; every row has page ref)

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