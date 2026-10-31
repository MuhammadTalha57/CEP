#!/usr/bin/env python3
"""Fetch citation counts (OpenAlex, Semantic Scholar, Crossref) and artifact stats (GitHub, HuggingFace).
Reads data/ledger.csv + data/papers/*.json. Writes data/citations.csv and data/artifacts.csv.
Standard library only. Every value carries source + fetched_at. Missing -> empty + note, never guessed."""
import csv, json, re, sys, time, glob, os, difflib, urllib.request, urllib.parse
from datetime import datetime, timezone

NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
UA = {"User-Agent": "cep-metrics/1.0 (student project)"}
GH_TOKEN = os.environ.get("GH_TOKEN", "")

def get(url, headers=None, tries=3):
    h = dict(UA); h.update(headers or {})
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=25) as r:
                return json.loads(r.read().decode("utf8", "replace")), ""
        except urllib.error.HTTPError as e:
            if e.code == 404: return None, "404 not found"
            if e.code in (429, 503): time.sleep(3 * (i + 1)); continue
            return None, f"HTTP {e.code}"
        except Exception as e:
            err = type(e).__name__
            time.sleep(1)
    return None, err

def sim(a, b):
    n = lambda s: re.sub(r"[^a-z0-9 ]", "", (s or "").lower())
    return round(difflib.SequenceMatcher(None, n(a), n(b)).ratio(), 2)

def clean_doi(s):
    m = re.search(r"10\.\d{4,9}/[^\s()]+", s or "")
    return m.group(0).rstrip(".,;") if m else ""

def openalex(doi, title):
    note = ""
    if doi:
        d, e = get("https://api.openalex.org/works/doi:" + urllib.parse.quote(doi, safe="/"))
    else: d, e = None, "no doi"
    if d is None and title:
        q = urllib.parse.quote(title.replace(",", " "))
        s, e2 = get(f"https://api.openalex.org/works?filter=title.search:{q}&per-page=1")
        if s and s.get("results"): d, note = s["results"][0], "matched by title"; e = ""
        else: e = e2 or e
    if not d: return "", "", f"openalex: {e}"
    return d.get("cited_by_count", ""), d.get("title", ""), note

def s2(doi, title):
    f = "title,year,venue,citationCount,influentialCitationCount"
    if doi: d, e = get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{urllib.parse.quote(doi, safe='/')}?fields={f}")
    else: d, e = None, "no doi"
    note = ""
    if d is None and title:
        s, e2 = get("https://api.semanticscholar.org/graph/v1/paper/search?limit=1&fields=" + f + "&query=" + urllib.parse.quote(title))
        if s and s.get("data"): d, note = s["data"][0], "matched by title"
        else: e = e2 or e
    if not d: return "", "", "", f"s2: {e}"
    return d.get("citationCount", ""), d.get("influentialCitationCount", ""), d.get("title", ""), note

def crossref(doi):
    if not doi: return ""
    d, e = get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))
    return d["message"].get("is-referenced-by-count", "") if d else ""

def citations():
    rows = list(csv.DictReader(open("data/ledger.csv", encoding="utf8")))
    out = []
    for r in rows:
        doi, title = clean_doi(r.get("doi")), r.get("title", "")
        oa, oa_t, oa_n = openalex(doi, title); time.sleep(0.3)
        sc, si, s_t, s_n = s2(doi, title); time.sleep(1.0)
        cr = crossref(doi); time.sleep(0.3)
        notes = "; ".join(x for x in (oa_n, s_n) if x)
        mism = [n for n, t in (("openalex", oa_t), ("s2", s_t)) if t and title and sim(t, title) < 0.85]
        if mism: notes += f"; TITLE MISMATCH in {','.join(mism)} - verify manually"
        out.append({"id": r["id"], "title": title, "doi_used": doi, "openalex_cited_by": oa,
                    "semanticscholar_citations": sc, "semanticscholar_influential": si,
                    "crossref_cited_by": cr, "fetched_at": NOW, "notes": notes.strip("; ")})
        print(r["id"], oa, sc, cr, notes, flush=True)
    write("data/citations.csv", out)

def gh_repo(owner, repo):
    h = {"Accept": "application/vnd.github+json"}
    if GH_TOKEN: h["Authorization"] = "Bearer " + GH_TOKEN
    d, e = get(f"https://api.github.com/repos/{owner}/{repo}", h)
    if not d: return {"error": e}
    return {"stars": d["stargazers_count"], "forks": d["forks_count"], "open_issues": d["open_issues_count"],
            "last_push": d["pushed_at"], "license": (d.get("license") or {}).get("spdx_id", ""),
            "archived": d["archived"], "language": d.get("language", "")}

def artifacts():
    out, seen = [], set()
    for fn in sorted(glob.glob("data/papers/P*.json")):
        p = json.load(open(fn, encoding="utf8"))
        urls = [a.get("url", "") for a in p.get("artifacts", [])] + [x.get("url", "") for x in p.get("datasets_benchmarks", [])]
        for u in urls:
            if not u or u in seen or not u.startswith("http"): continue
            seen.add(u)
            row = {"paper": p["id"], "url": u, "kind": "", "stars_or_likes": "", "forks_or_downloads": "",
                   "last_push": "", "license": "", "archived": "", "fetched_at": NOW, "notes": ""}
            m = re.match(r"https?://github\.com/([^/]+)/([^/#?]+)", u)
            hf = re.match(r"https?://huggingface\.co/datasets/([^/]+/[^/#?]+)", u)
            if m:
                row["kind"] = "github"; r = gh_repo(m.group(1), m.group(2).removesuffix(".git"))
                if "error" in r: row["notes"] = r["error"]
                else: row.update(stars_or_likes=r["stars"], forks_or_downloads=r["forks"], last_push=r["last_push"],
                                 license=r["license"], archived=r["archived"], notes=f"issues={r['open_issues']}; lang={r['language']}")
            elif hf:
                row["kind"] = "huggingface-dataset"; d, e = get("https://huggingface.co/api/datasets/" + hf.group(1))
                if d: row.update(stars_or_likes=d.get("likes", ""), forks_or_downloads=d.get("downloads", ""),
                                 last_push=d.get("lastModified", ""), license=str((d.get("cardData") or {}).get("license", "")))
                else: row["notes"] = e
            else:
                row["kind"] = "other"; row["notes"] = "not fetched (not GitHub/HF)"
            out.append(row); print(row["paper"], u, row["stars_or_likes"], row["notes"], flush=True); time.sleep(0.5)
    write("data/artifacts.csv", out)

def write(path, rows):
    if not rows: return
    with open(path, "w", newline="", encoding="utf8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

if __name__ == "__main__":
    citations(); artifacts()