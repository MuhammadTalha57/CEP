#!/usr/bin/env python3
"""Search open scholarly metadata (Semantic Scholar, OpenAlex, arXiv). Does not touch paywalled publishers.
Usage: python scripts/search_papers.py "indirect prompt injection" --limit 25
"""
import argparse, csv, json, os, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET

OUT = os.path.join("research", "candidates.csv")
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
    if r.get("source") == "arxiv" or "arxiv" in venue:
        return "PREPRINT"            # check if later published at a real venue
    top = any(k in venue for k in TOP_VENUES)
    if doi.startswith("10.1145/"):
        return "ACM-TOP" if top else "ACM"
    if doi.startswith("10.1109/"):
        return "IEEE-TOP" if top else "IEEE"
    if top:
        return "TOP-VENUE"
    return "UNVERIFIED"

UA = {"User-Agent": "cep-research-agent/1.0 (student project)"}

def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def semantic_scholar(q, n):
    fields = "title,year,venue,citationCount,externalIds,openAccessPdf,url"
    url = ("https://api.semanticscholar.org/graph/v1/paper/search?query=" + urllib.parse.quote(q)
           + f"&limit={n}&fields={fields}")
    try:
        data = json.loads(get(url))
    except Exception as e:
        print("[semantic scholar] failed:", e, file=sys.stderr); return []
    rows = []
    for p in data.get("data", []):
        rows.append(dict(source="semanticscholar", year=p.get("year"), title=p.get("title"),
            venue=p.get("venue"), citations=p.get("citationCount"),
            doi=(p.get("externalIds") or {}).get("DOI", ""), url=p.get("url"),
            open_pdf=(p.get("openAccessPdf") or {}).get("url", "")))
    return rows

def openalex(q, n):
    url = ("https://api.openalex.org/works?search=" + urllib.parse.quote(q)
           + f"&per-page={n}&sort=cited_by_count:desc")
    try:
        data = json.loads(get(url))
    except Exception as e:
        print("[openalex] failed:", e, file=sys.stderr); return []
    rows = []
    for w in data.get("results", []):
        loc = w.get("primary_location") or {}
        src = (loc.get("source") or {}).get("display_name", "")
        rows.append(dict(source="openalex", year=w.get("publication_year"), title=w.get("title"),
            venue=src, citations=w.get("cited_by_count"), doi=(w.get("doi") or "").replace("https://doi.org/", ""),
            url=w.get("id"), open_pdf=(w.get("open_access") or {}).get("oa_url") or ""))
    return rows

def arxiv(q, n):
    url = ("http://export.arxiv.org/api/query?search_query=all:" + urllib.parse.quote(q)
           + f"&max_results={n}&sortBy=relevance")
    try:
        root = ET.fromstring(get(url))
    except Exception as e:
        print("[arxiv] failed:", e, file=sys.stderr); return []
    ns = {"a": "http://www.w3.org/2005/Atom"}
    rows = []
    for e in root.findall("a:entry", ns):
        link = e.find("a:id", ns).text
        rows.append(dict(source="arxiv", year=(e.find("a:published", ns).text or "")[:4],
            title=" ".join((e.find("a:title", ns).text or "").split()), venue="arXiv preprint",
            citations="", doi="", url=link, open_pdf=link.replace("/abs/", "/pdf/")))
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query"); ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--only-vetted", action="store_true", help="hide PREPRINT and UNVERIFIED results")
    a = ap.parse_args()
    rows = []
    for fn in (semantic_scholar, openalex, arxiv):
        rows += fn(a.query, a.limit); time.sleep(1.5)   # be polite
    seen, uniq = set(), []
    for r in rows:
        key = (r["doi"] or (r["title"] or "").lower().strip())
        if key and key not in seen:
            seen.add(key); uniq.append(r)
    for r in uniq:
        r["tier"] = tier(r)
    if a.only_vetted:
        uniq = [r for r in uniq if r["tier"] not in ("PREPRINT", "UNVERIFIED")]
    os.makedirs("research", exist_ok=True)
    new = not os.path.exists(OUT)
    with open(OUT, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if new: w.writerow("candidate_id,query,source,year,title,venue,citations,doi,url,open_pdf,tier,status".split(","))
        for i, r in enumerate(uniq, 1):
            w.writerow([f"{int(time.time())}-{i}", a.query, r["source"], r["year"], r["title"], r["venue"],
                        r["citations"], r["doi"], r["url"], r["open_pdf"], r["tier"], "unread"])
    order = {"ACM-TOP":0,"IEEE-TOP":0,"TOP-VENUE":1,"ACM":2,"IEEE":2,"PREPRINT":3,"UNVERIFIED":4}
    def cites(x): return int(x["citations"]) if str(x["citations"]).isdigit() else 0
    for r in sorted(uniq, key=lambda x: (order[x["tier"]], -cites(x))):
        print(f'[{r["tier"]:10}] {r["year"]} | {str(r["venue"])[:26]:26} | {str(r["citations"]):>5} | {str(r["title"])[:80]}\n      {r["doi"] or r["url"]}  {"[OPEN PDF]" if r["open_pdf"] else ""}')
    print(f"\n{len(uniq)} unique results appended to {OUT}")

if __name__ == "__main__":
    main()
