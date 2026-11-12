"""Document rendering (HTML/PDF) and the deliberately naive loader used by App B (design.md §3).

Naive loader = what a quick-built RAG app typically does [OURS, modelled on P04 p3 and P13 p3]:
- HTML: all text nodes (CSS is not rendered, so hidden/off-screen text is kept) plus alt/ARIA/title
  attribute text; <script>/<style> removed.
- PDF: all extracted page text (white and tiny text included) plus metadata fields (P13 p3 metadata vector).
"""
from __future__ import annotations

import html as html_lib
import io
import textwrap
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml
from bs4 import BeautifulSoup
from pypdf import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

REPO_ROOT = Path(__file__).resolve().parents[3]
KB_FILE = REPO_ROOT / "data" / "kb" / "docs.yaml"
ATTR_TEXT = ("alt", "aria-label", "title")
META_FIELDS = ("/Title", "/Author", "/Subject", "/Keywords")


@dataclass
class Document:
    id: str
    title: str
    format: str  # "html" | "pdf"
    raw: str | bytes
    text: str  # naive extraction
    poisoned: bool = False


# ---------------------------------------------------------------- rendering
def render_html(title: str, paras: list[str], inject_html: str = "") -> str:
    body = "\n".join(f"<p>{html_lib.escape(p)}</p>" for p in paras)
    return (f"<!doctype html><html><head><meta charset='utf-8'><title>{html_lib.escape(title)}</title>"
            f"<style>body{{font-family:sans-serif}}</style></head><body><h1>{html_lib.escape(title)}</h1>\n"
            f"{body}\n{inject_html}\n</body></html>")


def render_pdf(title: str, paras: list[str], white_text: str = "", tiny_text: str = "",
               metadata: dict[str, str] | None = None) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4, invariant=1)  # invariant=1: byte-identical output for same input
    c.setTitle(title)
    for key, value in (metadata or {}).items():
        getattr(c, f"set{key}")(value)  # setSubject / setAuthor / setKeywords
    w, h = A4
    y = h - 60
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, y, title)
    y -= 30
    c.setFont("Helvetica", 11)
    for p in paras:
        for line in textwrap.wrap(p, 90):
            c.drawString(50, y, line)
            y -= 15
        y -= 6
    if white_text:  # P13 p3: white text on white background
        c.setFillColorRGB(1, 1, 1)
        for line in textwrap.wrap(white_text, 90):
            c.drawString(50, y, line)
            y -= 15
        c.setFillColorRGB(0, 0, 0)
    if tiny_text:  # P13 p3: 0.1 pt font in the footer
        c.setFont("Helvetica", 0.1)
        c.drawString(50, 30, tiny_text)
    c.showPage()
    c.save()
    return buf.getvalue()


# ---------------------------------------------------------------- naive loader
def html_to_text(raw: str) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    for t in soup(["script", "style", "head"]):
        t.decompose()
    for tag in soup.find_all(True):
        attrs = [tag.get(a) for a in ATTR_TEXT if tag.get(a)]
        if attrs:
            tag.insert_after(" " + " ".join(attrs) + " ")
    lines = [ln.strip() for ln in soup.get_text("\n").splitlines()]
    return "\n".join(ln for ln in lines if ln)


def pdf_to_text(raw: bytes) -> str:
    reader = PdfReader(io.BytesIO(raw))
    parts = [(p.extract_text() or "").strip() for p in reader.pages]
    meta = reader.metadata or {}
    for f in META_FIELDS:
        v = meta.get(f)
        if v:
            parts.append(f"{f.strip('/')}: {v}")
    return "\n".join(p for p in parts if p)


def extract(raw: str | bytes, fmt: str) -> str:
    return html_to_text(raw) if fmt == "html" else pdf_to_text(raw)


def make_document(doc_id: str, title: str, fmt: str, raw: str | bytes, poisoned: bool = False) -> Document:
    return Document(doc_id, title, fmt, raw, extract(raw, fmt), poisoned)


@lru_cache(maxsize=1)
def load_kb(path: str = str(KB_FILE)) -> tuple[Document, ...]:
    """Clean KB: even-indexed docs as HTML, odd-indexed as PDF (both loaders exercised by clean tasks)."""
    docs = yaml.safe_load(Path(path).read_text(encoding="utf-8"))["docs"]
    out = []
    for i, d in enumerate(docs):
        if i % 2 == 0:
            out.append(make_document(d["id"], d["title"], "html", render_html(d["title"], d["paras"])))
        else:
            out.append(make_document(d["id"], d["title"], "pdf", render_pdf(d["title"], d["paras"])))
    return tuple(out)
