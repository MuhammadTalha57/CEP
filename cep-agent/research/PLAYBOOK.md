# Playbook: how the VPN, search and download workflow works

1. Connect OpenVPN (university profile). Check you can open ieeexplore.ieee.org and dl.acm.org in your browser.
2. In opencode run `/find-papers indirect prompt injection LLM applications` (open metadata search, no publisher scraping).
3. The agent returns a shortlist and says which are open vs VPN-only.
4. You open each VPN-only DOI in your browser, click Download PDF, save into research/papers/ (name: year_author_topic.pdf).
5. Run `/analyze research/papers/2024_author_topic.pdf` (one at a time or a short list).
6. After ~10 papers run `/synthesize`.
7. Commit research/ to git so nothing is lost.

Tips: use Google Scholar "Cited by" and "Related articles" yourself on the 3 best papers; paste titles to the agent.
Look for "Code", "Artifacts" or GitHub links in each paper; those are the reusable assets.
