#!/usr/bin/env python3
"""Backward + forward citation chasing over OpenAlex for the 5 Phase-1 seed papers.

Writes NEW, de-duplicated, LLM-security-relevant works to research/candidates.csv
(query = "citation-chase:<seed>", status = unread). Never touches publisher sites.

Why not Semantic Scholar: its API returned HTTP 429 on every call in this project's
sessions, so the citation graph here comes from OpenAlex (referenced_works for
backward, filter=cites:W... for forward). Crossref is used only as a *supplement*
for backward references of ACM DOIs, because OpenAlex's reference lists for those
records are sparse.

Usage:
  python scripts/citation_chase.py                 # all seeds
  python scripts/citation_chase.py --seeds greshake,bipia
  python scripts/citation_chase.py --max-forward 200 --dry-run

Politeness: one HTTP request at a time, >= 1.1 s apart, 3 retries with backoff on
429/5xx, then give up on that seed and say so. Nothing is deleted or overwritten:
candidates.csv is opened in append mode only.
"""
import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

OUT = os.path.join("research", "candidates.csv")
UA = {"User-Agent": "cep-research-agent/1.0 (mailto:student@example.edu)"}
SLEEP = 1.1          # seconds between requests (OpenAlex polite pool allows far more)
MAX_FORWARD = 300    # cap citing works per seed, highest-cited first (noise control)
REQ_COUNT = 0

# Copied from scripts/search_papers.py (do not import: that module runs argparse at import
# time and we must not mutate its behaviour). One documented extension: arXiv DOIs
# (10.48550/arxiv.*) are treated as PREPRINT even though the DOI prefix is not 10.1145/10.1109.
TOP_VENUES = ["security and privacy", "usenix security", "ndss", "network and distributed system",
    "computer and communications security", "ccs", "aisec", "artificial intelligence and security", "neurips", "neural information processing",
    "iclr", "learning representations", "icml", "machine learning", "acl", "emnlp", "naacl",
    "empirical methods in natural language", "computational linguistics", "transactions on information forensics",
    "dependable and secure computing", "computing surveys", "transactions on privacy and security",
    "software engineering", "asia ccs", "raid", "acsac", "esorics"]


def tier(r):
    """Heuristic reputation tier. A hint to verify, NOT proof of quality."""
    doi = (r.get("doi") or "").lower()
    venue = (r.get("venue") or "").lower()
    if doi.startswith("10.48550/arxiv.") or "arxiv" in venue:
        return "PREPRINT"
    top = any(k in venue for k in TOP_VENUES)
    if doi.startswith("10.1145/"):
        return "ACM-TOP" if top else "ACM"
    if doi.startswith("10.1109/"):
        return "IEEE-TOP" if top else "IEEE"
    if top:
        return "TOP-VENUE"
    return "UNVERIFIED"


SEEDS = [
    dict(key="greshake", short="Greshake23-IPI", work="W4388886073",
         doi="10.1145/3605764.3623985", arxiv="2302.12173",
         title="Not What You've Signed Up For: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection"),
    dict(key="liu", short="Liu24-Formalizing", work=None,
         doi=None, arxiv="2310.12815",
         title="Formalizing and Benchmarking Prompt Injection Attacks and Defenses"),
    dict(key="agentdojo", short="AgentDojo24", work="W4415796822",
         doi="10.52202/079017-2636", arxiv="2406.13352",
         title="AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents"),
    dict(key="injecagent", short="InjecAgent24", work="W4402670146",
         doi="10.18653/v1/2024.findings-acl.624", arxiv="2403.02691",
         title="InjecAgent: Benchmarking Indirect Prompt Injections in Tool-Integrated Large Language Model Agents"),
    dict(key="bipia", short="BIPIA25", work="W4409150456",
         doi="10.1145/3690624.3709179", arxiv="2312.14197",
         title="Benchmarking and Defending Against Indirect Prompt Injection Attacks on Large Language Models"),
]

# Plausible-topic gate. OpenAlex citation sets are noisy (a citing paper may mention
# prompt injection once in related work), so a title signal is required, or a repeated
# abstract signal *plus* an LLM/agent/RAG title.
STRONG_TITLE = re.compile(
    r"prompt[\s-]injection|indirect prompt|jailbreak|goal hijack|prompt leak|"
    r"instruction hierarchy|tool poison|mcp[^a-z]|rag poison|retrieval poison|"
    r"poisoning attack|agent security|llm security|language model security|"
    r"adversarial prompt|prompt attack|injection attack|agent attack|guardrail|"
    r"llm[- ]integrated|tool[- ]integrated|llm agent|llm[- ]based agent|ai agent|"
    r"agentic|retrieval[- ]augmented generation|\brag\b|red[- ]team|prompt defens",
    re.I)
TITLE_LLM = re.compile(r"\bllm|language model|agent|rag\b|retrieval|chatbot|\bmcp\b", re.I)
PROMPT_RE = re.compile(r"prompt[\s-]injection|jailbreak|goal hijack|prompt leak", re.I)
# Adjacent application domains: keep only if the title itself is about the attack.
OFF_DOMAIN = re.compile(
    r"intrusion detection|drug safety|curriculum|education|student|supercapacitor|"
    r"recommendation system|wellbore|medical imaging|federated learning", re.I)

# Foundational/irrelevant reference noise we never want from a backward pass.
STOP_TITLE = re.compile(
    r"^(gpt-4 technical report|language models are few-shot learners|"
    r"attention is all you need|adam: a method|bert:|training language models to follow|"
    r"stochastic parrots|stereoset|on the opportunities and risks)", re.I)


def log(msg):
    print(msg, file=sys.stderr)


def get_json(url, tries=3):
    """GET + JSON with backoff. Returns None on permanent failure (logged)."""
    global REQ_COUNT
    delay = 5
    for attempt in range(1, tries + 1):
        time.sleep(SLEEP)
        try:
            REQ_COUNT += 1
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=45) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and attempt < tries:
                log(f"[warn] HTTP {e.code} - backing off {delay}s ({attempt}/{tries})")
                time.sleep(delay)
                delay *= 2
                continue
            log(f"[error] HTTP {e.code} for {url}")
            return None
        except Exception as e:  # timeouts, DNS, JSON
            if attempt < tries:
                log(f"[warn] {e} - retry in {delay}s ({attempt}/{tries})")
                time.sleep(delay)
                delay *= 2
                continue
            log(f"[error] {e} for {url}")
            return None
    return None


def abstract_of(w):
    inv = w.get("abstract_inverted_index") or {}
    if not inv:
        return ""
    pos = []
    for word, idxs in inv.items():
        for i in idxs:
            pos.append((i, word))
    pos.sort()
    return " ".join(w for _, w in pos)


def norm_doi(d):
    return (d or "").strip().lower().replace("https://doi.org/", "").replace("http://doi.org/", "")


def norm_title(t):
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


def to_row(w):
    loc = w.get("primary_location") or {}
    venue = (loc.get("source") or {}).get("display_name") or ""
    return dict(
        source="openalex",
        year=w.get("publication_year"),
        title=" ".join((w.get("title") or "").split()),
        venue=venue,
        citations=w.get("cited_by_count", 0),
        doi=norm_doi(w.get("doi")),
        url=w.get("id"),
        open_pdf=(w.get("open_access") or {}).get("oa_url") or "",
        abstract=abstract_of(w),
    )


def load_seen():
    """DOIs + normalized titles already in candidates.csv (plus candidate ids)."""
    dois, titles = set(), set()
    if not os.path.exists(OUT):
        return dois, titles
    with open(OUT, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            d = norm_doi(row.get("doi"))
            if d:
                dois.add(d)
            t = norm_title(row.get("title"))
            if t:
                titles.add(t)
    return dois, titles


def resolve_seed(seed):
    """Resolve a seed to an OpenAlex work id. Order: known id -> DOI -> arXiv DOI -> title."""
    if seed.get("work"):
        w = get_json(f"https://api.openalex.org/works/{seed['work']}"
                     "?select=id,doi,title,publication_year,cited_by_count,referenced_works")
        if w:
            return w
    if seed.get("doi"):
        d = get_json("https://api.openalex.org/works?filter=doi:"
                     + urllib.parse.quote(seed["doi"])
                     + "&select=id,doi,title,publication_year,cited_by_count,referenced_works")
        if d and d.get("results"):
            return d["results"][0]
    if seed.get("arxiv"):
        d = get_json("https://api.openalex.org/works?filter=doi:"
                     + urllib.parse.quote("10.48550/arxiv." + seed["arxiv"])
                     + "&select=id,doi,title,publication_year,cited_by_count,referenced_works")
        if d and d.get("results"):
            return d["results"][0]
    d = get_json("https://api.openalex.org/works?filter=title.search:"
                 + urllib.parse.quote(seed["title"])
                 + "&select=id,doi,title,publication_year,cited_by_count,referenced_works")
    if d and d.get("results"):
        return d["results"][0]
    return None


def fetch_by_ids(ids):
    """Batch-fetch works by OpenAlex id (50 per request)."""
    out = []
    ids = list(ids)
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        d = get_json("https://api.openalex.org/works?filter=openalex_id:"
                     + "|".join(chunk) + "&per-page=50&select=id,doi,title,publication_year,"
                     "cited_by_count,primary_location,open_access,abstract_inverted_index")
        if d:
            out += d.get("results", [])
    return out


def fetch_by_dois(dois):
    out = []
    for i in range(0, len(dois), 25):
        chunk = dois[i:i + 25]
        d = get_json("https://api.openalex.org/works?filter=doi:"
                     + "|".join(urllib.parse.quote(x, safe="") for x in chunk)
                     + "&per-page=25&select=id,doi,title,publication_year,cited_by_count,"
                     "primary_location,open_access,abstract_inverted_index")
        if d:
            out += d.get("results", [])
    return out


def crossref_backward(seed):
    """Supplement OpenAlex refs with DOIs from the Crossref reference list (ACM only)."""
    if not seed.get("doi"):
        return []
    d = get_json("https://api.crossref.org/works/" + urllib.parse.quote(seed["doi"]))
    if not d:
        return []
    refs = d.get("message", {}).get("reference", []) or []
    dois = []
    for r in refs:
        rd = norm_doi(r.get("DOI"))
        if rd and rd not in dois:
            dois.append(rd)
    log(f"[{seed['key']}] crossref: {len(refs)} refs, {len(dois)} with DOI")
    return fetch_by_dois(dois[:25])


def forward(seed, wid, cap):
    """Paginate citing works, highest-cited first, capped.

    NOTE: OpenAlex's cursor paging returned HTTP 401 for `cites:` filters in testing
    (the opaque cursor is rejected on page 2), so this uses the documented page= param
    instead. The citing set is small (<1000) so the 10k deep-paging limit is not a risk.
    """
    rows, page, fetched = [], 1, 0
    while fetched < cap:
        d = get_json("https://api.openalex.org/works?filter=cites:" + wid.split("/")[-1]
                     + "&sort=cited_by_count:desc&per-page=100&page=" + str(page)
                     + "&select=id,doi,title,publication_year,cited_by_count,primary_location,"
                     "open_access,abstract_inverted_index")
        if not d:
            break
        batch = d.get("results", [])
        rows += batch
        fetched += len(batch)
        if len(batch) < 100:
            break
        page += 1
    return rows[:cap], fetched


def keep(row):
    title = row["title"] or ""
    text = title + " " + (row.get("abstract") or "")
    if STOP_TITLE.search(title) or OFF_DOMAIN.search(title):
        return False
    if STRONG_TITLE.search(title):
        return True
    # Fallback: abstract mentions prompt injection explicitly at least twice and the
    # title is at least LLM/agent-adjacent (drops "prompt" in the UI sense).
    if TITLE_LLM.search(title) and len(PROMPT_RE.findall(text)) >= 2:
        return True
    return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="", help="comma list: greshake,liu,agentdojo,injecagent,bipia")
    ap.add_argument("--max-forward", type=int, default=MAX_FORWARD)
    ap.add_argument("--dry-run", action="store_true", help="print only, do not append")
    a = ap.parse_args()

    wanted = [s.strip() for s in a.seeds.split(",") if s.strip()]
    seeds = [s for s in SEEDS if not wanted or s["key"] in wanted]

    seen_doi, seen_title = load_seen()
    log(f"[init] {len(seen_doi)} DOIs / {len(seen_title)} titles already known")

    new_rows, stats = [], []
    for seed in seeds:
        log(f"\n=== {seed['key']} ({seed['short']}) ===")
        w = resolve_seed(seed)
        if not w:
            log(f"[{seed['key']}] could not resolve to an OpenAlex work - SKIPPED (logged)")
            stats.append((seed, None, 0, 0, 0))
            continue
        wid = w["id"].split("/")[-1]
        log(f"[{seed['key']}] resolved {wid} | {w.get('publication_year')} | cites={w.get('cited_by_count')} "
            f"| refs={len(w.get('referenced_works') or [])}")

        # ---- backward ----
        refs = list(w.get("referenced_works") or [])
        back = fetch_by_ids([r.split("/")[-1] for r in refs]) if refs else []
        back += crossref_backward(seed)
        log(f"[{seed['key']}] backward candidates: {len(back)}")

        # ---- forward ----
        fwd, fetched = forward(seed, wid, a.max_forward)
        log(f"[{seed['key']}] forward candidates: {len(fwd)} (fetched {fetched}, cap {a.max_forward})")

        added_here = 0
        for src_rows in (back, fwd):
            for raw in src_rows:
                r = to_row(raw)
                if not r["title"]:
                    continue
                d, t = r["doi"], norm_title(r["title"])
                if (d and d in seen_doi) or (t and t in seen_title):
                    continue
                if not keep(r):
                    continue
                seen_doi.add(d) if d else None
                seen_title.add(t)
                r["query"] = f"citation-chase:{seed['key']}"
                r["tier"] = tier(r)
                new_rows.append(r)
                added_here += 1
        stats.append((seed, wid, len(back), len(fwd), added_here))
        log(f"[{seed['key']}] NEW relevant rows: {added_here}")

    # ---- append (append-only, never rewrite) ----
    if new_rows and not a.dry_run:
        stamp = int(time.time())
        os.makedirs("research", exist_ok=True)
        with open(OUT, "a", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            for i, r in enumerate(new_rows, 1):
                wr.writerow([f"cite-{stamp}-{i}", r["query"], "openalex", r["year"], r["title"],
                             r["venue"], r["citations"], r["doi"], r["url"], r["open_pdf"],
                             r["tier"], "unread"])

    # ---- ranked table ----
    order = {"ACM-TOP": 0, "IEEE-TOP": 0, "TOP-VENUE": 1, "ACM": 2, "IEEE": 2,
             "PREPRINT": 3, "UNVERIFIED": 4}

    def cites(x):
        return int(x["citations"]) if str(x["citations"]).isdigit() else 0

    for r in sorted(new_rows, key=lambda x: (order[x["tier"]], -cites(x))):
        print(f'[{r["tier"]:10}] {r["year"]} | {str(r["venue"])[:30]:30} | {str(r["citations"]):>5} | '
              f'{r["title"][:85]}\n      {r["doi"] or r["url"]}  {"[OPEN PDF] " + r["open_pdf"] if r["open_pdf"] else ""}')

    print("\n--- per-seed ---")
    for seed, wid, nb, nf, na in stats:
        print(f'{seed["key"]:11} {wid or "UNRESOLVED":12} back={nb:4} fwd={nf:4} new={na:3}')
    print(f'\n{len(new_rows)} new unique candidates '
          f'{"(dry-run, NOT written)" if a.dry_run else "appended to " + OUT}')
    print(f'{REQ_COUNT} HTTP requests total (>= {SLEEP}s apart)')


if __name__ == "__main__":
    main()
