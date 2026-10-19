# Phase 1 step 4 — shortlist of the best NEW finds (citation chase + cloud queries)

Date: 2026-10-19. Source: OpenAlex citation graph (backward + forward) around 5 seed papers,
plus two `search_papers.py` cloud/deployment queries.
**Every row is `unread`.** Relevance below is judged from metadata (venue, year, citations) and the
OpenAlex **abstract only** — no full text has been read. Tier = `search_papers.py`/`citation_chase.py`
heuristic; venue names were individually confirmed via Crossref (container-title). OpenAlex often
leaves the venue field empty for ACM records, which is why the heuristic shows `ACM` instead of `ACM-TOP`.

| # | Title | Year | Venue (verified) | DOI / URL | Open copy | Tier | Why it looks relevant |
|---|---|---|---|---|---|---|---|
| 1 | PLeak: Prompt Leaking Attacks against Large Language Model Applications | 2024 | ACM CCS 2024 | 10.1145/3658644.3670370 | ⚠ OpenAlex says gold OA but only the DOI landing page is listed — verify, likely VPN | ACM (heuristic; venue is top-tier) | Optimisation-based **prompt leaking** against *deployed LLM applications* — matches two CEP attack types (prompt leaking, black-box app attack). `unread`. |
| 2 | Optimization-based Prompt Injection Attack to LLM-as-a-Judge (JudgeDeceiver) | 2024 | ACM CCS 2024 | 10.1145/3658644.3690291 | https://arxiv.org/pdf/2403.17710 | ACM (heuristic; top-tier venue) | Gradient-based indirect injection that hijacks an LLM judge/tool-selection step — attack technique we can reproduce. `unread`. |
| 3 | Prompt-to-SQL Injections in LLM-Integrated Web Applications: Risks and Defenses | 2025 | IEEE/ACM ICSE 2025 | 10.1109/icse55347.2025.00007 | https://doi.org/10.1109/icse55347.2025.00007 (hybrid OA) | IEEE-TOP | Prompt-driven injection through LangChain/LlamaIndex into SQL — a concrete **LLM-integrated web app** attack surface close to the CEP's app builds. `unread`. |
| 4 | Neural Exec: Learning (and Learning from) Execution Triggers for Prompt Injection Attacks | 2024 | ACM AISec 2024 | 10.1145/3689932.3694764 | https://arxiv.org/pdf/2403.03792 | ACM-TOP | Learnable (differentiable) injection triggers replacing hand-crafted strings; likely reusable attack tooling. `unread`. |
| 5 | PromptShield: Deployable Detection for Prompt Injection Attacks | 2024 | ACM CODASPY 2024 | 10.1145/3714393.3726501 | https://arxiv.org/pdf/2501.15145 (+ eScholarship PDF) | ACM | Detection **benchmark + detector built for deployment** (conversational + application-structured data) — directly usable as a defence baseline. `unread`. |
| 6 | MASTERKEY: Automated Jailbreaking of Large Language Model Chatbots | 2024 | NDSS 2024 | 10.14722/ndss.2024.24188 | https://doi.org/10.14722/ndss.2024.24188 (bronze OA) | TOP-VENUE | Automated, black-box jailbreak generation for production chatbot safeguards; 120+ citations. `unread`. |
| 7 | Human-Imperceptible Retrieval Poisoning Attacks in LLM-Powered Applications | 2024 | ACM FSE 2024 (companion) | 10.1145/3663529.3663786 | https://arxiv.org/pdf/2404.17196 | ACM-TOP | RAG/retrieval **poisoning via app frameworks**, i.e. an indirect-injection threat against real app stacks. `unread`. |
| 8 | Get My Drift? Catching LLM Task Drift with Activation Deltas | 2025 | IEEE SaTML 2025 | 10.1109/satml64287.2025.00011 | https://arxiv.org/pdf/2406.00799 | IEEE-TOP | Defines/measures **task drift** (goal hijacking) in retrieval-augmented apps with internal-state detection — gives us a metric idea. `unread`. |
| 9 | Securing RAG: A Risk Assessment and Mitigation Framework | 2025 | IEEE SDS 2025 | 10.1109/sds66131.2025.00024 | https://arxiv.org/pdf/2505.08728 | IEEE | End-to-end RAG attack-surface + mitigation framework; useful for the "RAG poisoning" CEP column. `unread`. |
| 10 | The Emerged Security and Privacy of LLM Agent: A Survey with Case Studies | 2025 | ACM Computing Surveys | 10.1145/3773080 | https://arxiv.org/pdf/2407.19354 | ACM-TOP | High-citation CSUR survey mapping agent threats/case studies — good related-work anchor. `unread`. |
| 11 | Defending Against Prompt Injection With a Few DefensiveTokens | 2025 | ACM AISec 2025 | 10.1145/3733799.3762982 | ⚠ hybrid per OpenAlex, only DOI landing listed — verify | ACM-TOP | Lightweight test-time defence (token-level robustness); cheap to add as a defence arm. `unread`. |
| 12 | When AI Meets the Web: Prompt Injection Risks in Third-Party AI Chatbot Plugins | 2026 | IEEE S&P 2026 | 10.1109/sp63933.2026.00062 | none (closed) — **VPN** | IEEE-TOP | Study of injection risk in **third-party plugins of deployed chatbot products** — the closest thing to a cloud-hosted-product security study. `unread`. |
| 13 | Security Debt in LLM Agent Applications: A Measurement Study of Vulnerabilities and Mitigation Trade-offs | 2025 | IEEE/ACM ASE 2025 | 10.1109/ase63991.2025.00053 | none (closed) — **VPN** | IEEE-TOP | Empirical measurement of vulnerabilities in **real, shipped LLM agent apps** — deployment evidence we can cite. `unread`. |
| 14 | AgentBreaker: Evaluating Context-Aware Indirect Prompt Injection Risks in Modern Web Agents | 2026 | Proc. ACM Softw. Eng. (FSE) | 10.1145/3832165 | https://dl.acm.org/doi/pdf/10.1145/3832165 (hybrid OA) | ACM-TOP | Context-aware IPI benchmark for multi-LLM web agents — benchmark we could extend. `unread`. |
| 15 | Securing MCP-based Agent Workflows (SAMOS) | 2025 | ACM workshop (Practical Adoption Challenges / SPLASH) | 10.1145/3766882.3767177 | https://doi.org/10.1145/3766882.3767177 (gold OA) | ACM | Information-flow-control **gateway** for MCP tool calls deployed by an administrator — deployment-architecture defence. `unread`. |

Honourable mentions (also new, `unread`): Log-To-Leak (MCP tool-poisoning attack, 10.1145/3847320.3847399, gold OA);
PromptFuzz (fuzzing PI robustness, IEEE TIFS, 10.1109/tifs.2026.3666893, **closed → VPN**);
RAG Security and Privacy: Formalizing the Threat Model and Attack Surface (10.1109/icdmw69685.2025.00165, arXiv 2509.20324);
Navigating the Risks: A Survey of Security and Privacy Threats in LLM-Based Agents (ACM TOSEM 2026, 10.1145/3807666, **closed → VPN**);
LLM Safeguard is a Double-Edged Sword (10.1145/3733800.3763264).

## Cloud / SaaS-deployment angle
No new peer-reviewed paper takes *cloud-hosted prompt-injection evaluation* as its subject.
The angle is **partially** closed by: #5 PromptShield (deployability), #12 Third-Party AI Chatbot Plugins
(S&P'26, deployed products), #13 Security Debt (real shipped apps), #15 SAMOS (deployed MCP gateway),
plus *Privacy-Preserving Prompt Injection Detection for Smart Cloud-Deployed Large Language Models*
(IEEE SmartCloud 2025, 10.1109/smartcloud66068.2025.00009, **closed → VPN**) and the arXiv preprint
*ACE: A Security Architecture for LLM-Integrated App Systems* (arXiv 2504.20984, PREPRINT, open).
The two cloud **queries** themselves were low-precision; the deployment signal came from the chase.

## Manual VPN downloads needed
1. 10.1109/sp63933.2026.00062 — When AI Meets the Web: Prompt Injection Risks in Third-Party AI Chatbot Plugins (IEEE S&P 2026)
2. 10.1109/ase63991.2025.00053 — Security Debt in LLM Agent Applications (ASE 2025)
3. 10.1109/smartcloud66068.2025.00009 — Privacy-Preserving Prompt Injection Detection for Smart Cloud-Deployed LLMs (IEEE SmartCloud 2025)
4. 10.1109/tifs.2026.3666893 — PromptFuzz (IEEE TIFS)
5. 10.1145/3807666 — Navigating the Risks: Survey of Security and Privacy Threats in LLM-Based Agents (ACM TOSEM 2026)
Verify (OpenAlex claims hybrid/gold OA but only the DOI landing page is listed):
10.1145/3658644.3670370 (PLeak), 10.1145/3733799.3762982 (DefensiveTokens).
