# Search log

Append-only. One row per query. "Source" = which open metadata APIs were hit (no publisher scraping).
Result counts are *unique records after de-duplication within a query*; the script searches
Semantic Scholar + OpenAlex + arXiv and appends all of them to `research/candidates.csv`.

| Date | Source | Query | Results | Notes |
|---|---|---|---|---|
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | indirect prompt injection LLM applications | 50 unique | Seed query. **Semantic Scholar returned HTTP 429 (rate limit) for every request in this session** — OpenAlex (25, sorted by citations) + arXiv (25, relevance) only. No citation counts for arXiv rows as a result. Surfaced Greshake'23, HouYi, Spotlighting, BIPIA, AgentVigil, Adaptive Attacks, WebInject, LogJack. |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | prompt injection attacks on LLM-integrated applications | 50 unique | S2 429. Mostly already seen; added PIShield, Attention Tracker, DataSentinel, ShadowCode, DeRAG, Multimodal PI. Lots of off-topic surveys (OpenAlex citation-sorted noise). |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | indirect prompt injection benchmark agent evaluation | 50 unique | S2 429. Best benchmark yield: InjecAgent, INFUSE, StepJack, LivePI, MUZZLE, AutoDojo, AgentDrift, NetInjectBench, LongPIBench, MELON. |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | RAG poisoning retrieval augmented generation attack | 50 unique | S2 429. RAG-poisoning cluster: Poison-RAG, Practical Poisoning, Benchmarking Poisoning Attacks, RAGPart/RAGMask, Traceback. Also the CSUR/EMNLP RAG surveys. |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | jailbreak benchmark prompt injection defense evaluation | 50 unique | S2 429. Jailbreak side (JailbreakBench, Latent Jailbreak, TeleAI-Safety) + guardrail side (PIGuard, InjecGuard, UniGuardian) + "A Critical Evaluation of Defenses". |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | agent tool-use injection goal hijacking prompt leaking | 50 unique | S2 429. Goal-hijacking prompt leaking cluster (Perez'22, Pseudo-Conversation Injection, Structural Template Injection, Silent Egress, personal-data leakage). |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | AgentDojo prompt injection benchmark tool-integrated agents | 50 unique | S2 429. Highest-precision query of the session. Yields AgentDojo, ASB, WASP, WAInjectBench, Task Shield, IPIGuard, NDSS'26 tool-selection attack, SecAlign (peer-reviewed record), MCPTox, Prompt Infection. |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | adaptive attacks break prompt injection defenses | 50 unique | S2 429. **Console crashed with UnicodeEncodeError (cp1252) *after* the CSV append — rows were written, only the console table was lost.** Re-ran later queries with `PYTHONIOENCODING=utf-8`. Surfaced "The Attacker Moves Second", COPA, Mixture of Encodings, "May I have your Attention?". |
| 2026-10-19 | Semantic Scholar + OpenAlex + arXiv | MCP tool poisoning LLM application security | 50 unique | S2 429. MCP/tool-poisoning cluster: MCPTox, MSB, Parasites in the Toolchain, MCP Safety Audit, MCP-ITP, ShareLock. TOSEM MCP survey (2026). |
| 2026-10-19 | OpenAlex (by DOI / title) | venue verification for shortlisted preprints | 12 lookups | Confirmed peer-reviewed versions: StruQ -> USENIX Security 2025; Liu et al. -> USENIX Security 2024; BIPIA -> KDD 2025 (10.1145/3690624.3709179); AgentDojo -> NeurIPS 2024 D&B (10.52202/079017-2636); InjecAgent -> Findings of ACL 2024; SecAlign -> ACM CCS 2025; Adaptive Attacks -> Findings of NAACL 2025. CaMeL, Instruction Hierarchy, MELON, Spotlighting remain preprint-only (no archival version found). |
| 2026-10-19 | Web (publisher/proceedings pages) | StruQ, Liu et al., CaMeL, Critical Evaluation, Attacker Moves Second venue check | 5 lookups | StruQ + Liu et al. -> USENIX'25 / USENIX'24 pages (open-access PDFs, code repos). "A Critical Evaluation of Defenses against Prompt Injection Attacks" -> also published as a dataset/tool paper at ACM SACMAT 2026 (10.1145/3750555.3811884), OA. "The Attacker Moves Second" -> USENIX Security 2026 (open-access PDF). CaMeL -> still arXiv only. |

## Housekeeping
- Totals after all 9 searches: 450 search rows + 9 manually added rows (published versions / verified items) = 459 rows in `research/candidates.csv`; 333 unique titles; 15 marked `shortlist`.
- Two corrections were made to record fields (not deletions): the venue label of the InjecAgent ACL record was empty in the API response and was filled in; duplicate titles from different sources were kept, with `status=shortlist` set on the single canonical row per paper.
- Nothing was downloaded from a publisher. No mass requests: 1 query per source per run, ~1.5 s sleep between sources, plus ~1.2 s between the OpenAlex verification calls.

## Retrieval queries to run next (not yet run)
- "prompt injection benchmark" + "cloud" / "SaaS deployment" (the CEP's cloud angle is under-covered so far)
- backward/forward citation chasing from the 15 shortlist items (Phase 1 step 4)
- MCP / agent tool-poisoning deep dive (seed #6 was thin before the MCP query)

---

# Phase 1 step 4 — citation chasing (2026-10-19) + cloud/deployment queries

Script: `scripts/citation_chase.py` (new; `search_papers.py` untouched). Source: OpenAlex
citation graph only — `referenced_works` for backward, `filter=cites:<W-id>` for forward.
Crossref used *only* to supplement backward references of ACM DOIs (OpenAlex reference
lists for those records are incomplete). Semantic Scholar is NOT used: it again returned
**HTTP 429 on every request** this session (the plain `search_papers.py` runs hit the same 429).

| Date | Source | Query | Results | Notes |
|---|---|---|---|---|
| 2026-10-19 | OpenAlex (backward + forward) | citation-chase:greshake (Greshake'23, W4388886073) | 117 new unique | Backward: 10 OpenAlex refs + 10 Crossref DOIs = 20 candidates. Forward: 604 citing works, top 300 fetched. Highest yield of the chase (PLeak, LLM-as-a-Judge, PromptShield, Neural Exec, MASTERKEY, Prompt-to-SQL, DefensiveTokens). |
| 2026-10-19 | OpenAlex (backward + forward) | citation-chase:liu (Liu'24 arXiv 2310.12815, W4387839052) | 2 new unique | Thin: OpenAlex has **no reference list for the arXiv record** (0 refs) and **no separate record for the USENIX Security 2024 version** (title.search finds only the arXiv DOI; USENIX proceedings appear largely unindexed in OpenAlex). Forward = 13 citing works only, so this seed's citation graph is **incomplete — do not treat as exhaustive**. |
| 2026-10-19 | OpenAlex (backward + forward) | citation-chase:agentdojo (NeurIPS'24 D&B, W4415796822) | 70 new unique | Backward empty (OpenAlex record has 0 `referenced_works`; Crossref has none either). Forward = 120 citing works. |
| 2026-10-19 | OpenAlex (backward + forward) | citation-chase:injecagent (Findings ACL'24, W4402670146) | 30 new unique | Backward empty (same reference-indexing gap). Forward = 132 citing works. |
| 2026-10-19 | OpenAlex (backward + forward) | citation-chase:bipia (KDD'25, W4409150456) | 25 new unique | Backward: 10 OpenAlex refs + 5 Crossref DOIs = 15. Forward = 80 citing works. |
| 2026-10-19 | Semantic Scholar (429) + OpenAlex + arXiv | prompt injection benchmark cloud SaaS deployment | 50 unique (mostly off-topic) | S2 429 (script-level; logged). OpenAlex citation-sorted hits generic cloud-computing/PaaS/IoT security; arXiv matched literal "cloud" (atmospheric-physics papers). Genuinely relevant rows were mainly **already-known** items (SecAlign, StruQ, WebInject, PromptShield, Automatic & Universal PI). |
| 2026-10-19 | Semantic Scholar (429) + OpenAlex + arXiv | LLM application security cloud hosted deployment | 50 unique (mostly off-topic) | S2 429. Best NEW find: **ACE: A Security Architecture for LLM-Integrated App Systems** (arXiv 2504.20984, preprint). Rest is off-topic (medical/agriculture/Nature-comms LLM papers) or duplicates (CAMEL, multimodal surveys). |

## Citation chase result
- **New unique candidates added: 244** by `citation_chase.py` (seeds: greshake 117, agentdojo 70,
  injecagent 30, bipia 25, liu 2), then **+100 rows** from the two cloud queries — `candidates.csv`
  went 459 -> 703 -> 803 data rows (704 / 804 lines incl. header). NOTE: `search_papers.py` de-dupes only *within a run*, so the cloud
  rows include duplicates of earlier titles; `citation_chase.py` de-dupes against the whole file
  (DOI, else normalized title), so its 244 are all new.
- **Strongest new finds** (metadata + abstract only, all `unread`): PLeak (ACM CCS'24, 10.1145/3658644.3670370),
  Optimization-based Prompt Injection Attack to LLM-as-a-Judge (ACM CCS'24, 10.1145/3658644.3690291),
  Prompt-to-SQL Injections in LLM-Integrated Web Applications (ICSE'25, 10.1109/icse55347.2025.00007),
  Neural Exec (AISec'24, 10.1145/3689932.3694764), MASTERKEY (NDSS'24, 10.14722/ndss.2024.24188),
  Human-Imperceptible Retrieval Poisoning (FSE'24 companion, 10.1145/3663529.3663786),
  Get My Drift? (SaTML'25, 10.1109/satml64287.2025.00011), Securing RAG (IEEE SDS'25, 10.1109/sds66131.2025.00024),
  "The Emerged Security and Privacy of LLM Agent" survey (CSUR'25, 10.1145/3773080).
- **Cloud / deployment gap: only PARTLY closed.** No peer-reviewed paper was found that *evaluates
  prompt injection against a cloud-hosted LLM application as its subject*. What we now have toward that
  angle: PromptShield ("Deployable Detection", CODASPY'24), "When AI Meets the Web: Prompt Injection Risks
  in Third-Party AI Chatbot Plugins" (IEEE S&P'26), "Security Debt in LLM Agent Applications" (ASE'25),
  "Privacy-Preserving Prompt Injection Detection for Smart Cloud-Deployed LLMs" (IEEE SmartCloud'25),
  and ACE (arXiv preprint, LLM-integrated app security architecture). The two cloud *queries* themselves
  were low-precision; the better cloud/deployment signal came from the citation chase, not the queries.
- Backward chasing is **weak** for the three 2024 seeds because OpenAlex lacks `referenced_works` for
  their records and the USENIX/NeurIPS/ACL DOIs deposit no Crossref reference lists. Recommended
  follow-up (manual, Phase 2): open the open-access PDFs of Liu'24 / AgentDojo / InjecAgent and read
  their reference sections by hand.
- Politeness: 22 OpenAlex requests for the whole chase (~1.1 s apart, 3-try backoff), 18 Crossref
  DOI-verification calls (~1.2 s apart), 2 search_papers.py runs (1 query/source, ~1.5 s apart).
  No publisher was scraped; nothing bulk-downloaded. One known API quirk: OpenAlex cursor paging
  returns HTTP 401 on page 2 for `cites:` filters, so the script uses `page=` paging instead.
