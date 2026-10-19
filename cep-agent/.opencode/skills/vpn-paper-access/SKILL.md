---
name: vpn-paper-access
description: Workflow for getting paywalled IEEE/ACM papers while the student is on the university OpenVPN, without automated scraping. Use whenever a shortlisted paper has no open copy.
compatibility: opencode
metadata:
  opencode/slash: "true"
---
## Facts
- The student runs OpenVPN on Windows 11 (university profile). Institutional access to IEEE Xplore and ACM DL works in the student's own browser while connected.
- Automated bulk downloading violates publisher terms and can get the university IP range blocked. Do not script it.

## What I do
1. Produce a numbered download list: `# | title | year | DOI link (https://doi.org/...)`.
2. Tell the student: open each DOI in the browser on the VPN, press Download PDF, save to `research/papers/<year>_<author>_<topic>.pdf`.
3. Before analysis, list research/papers/ and confirm the file exists. If not, say it is missing.
4. Check first for legal open copies: arXiv, author homepages, Semantic Scholar `openAccessPdf`.
5. If a PDF is image-only (no extractable text), tell the student; do not guess its contents.
6. If the VPN is down or a site shows a CAPTCHA, stop and tell the student rather than retrying.
