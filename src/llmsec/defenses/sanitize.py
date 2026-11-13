"""D2: sanitize + normalize documents before indexing (design.md §5.1).

Follows P04 p3 (sanitize hidden markup; Unicode-normalize) and the sanitization P13 p6 names as future
work (drop white / tiny PDF text and metadata). Replaces the naive loader of App B with a
"what a human would see" loader:
- HTML: drop hidden elements (display:none, visibility:hidden, off-screen, font-size:0, opacity:0,
  `hidden`, aria-hidden) and do NOT index alt / ARIA / title attribute text.
- PDF: keep only characters that are not white and at least 1 pt; ignore metadata.
- Both: NFKC normalization and removal of invisible format characters (zero-width, bidi controls).
Visible injected text (C1, and C4 once its zero-width characters are removed) is NOT removed by D2.
"""
from __future__ import annotations

import io
import re
import unicodedata

import pdfplumber
from bs4 import BeautifulSoup

from .base import Defense, Verdict

_HIDDEN_STYLE = re.compile(
    r"display\s*:\s*none|visibility\s*:\s*hidden|font-size\s*:\s*0(?:\.0+)?(?:px|pt|em|rem|%)?\s*(?:;|$)|"
    r"opacity\s*:\s*0(?:\.0+)?\s*(?:;|$)|(?:left|top|right|bottom)\s*:\s*-\d{3,}px",
    re.I,
)
MIN_FONT_PT = 1.0


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    return "".join(ch for ch in text if unicodedata.category(ch) != "Cf")  # zero-width, bidi controls, BOM


def _is_hidden(tag) -> bool:
    if tag.has_attr("hidden") or str(tag.get("aria-hidden", "")).lower() == "true":
        return True
    return bool(_HIDDEN_STYLE.search(tag.get("style", "") or ""))


def html_visible_text(raw: str) -> str:
    soup = BeautifulSoup(raw, "html.parser")
    for t in soup(["script", "style", "head", "noscript", "template"]):
        t.decompose()
    for t in [t for t in soup.find_all(True) if _is_hidden(t)]:
        if not t.decomposed:
            t.decompose()
    lines = [ln.strip() for ln in soup.get_text("\n").splitlines()]
    return normalize("\n".join(ln for ln in lines if ln))


def _is_white(color) -> bool:
    if color is None:
        return False
    vals = list(color) if isinstance(color, (list, tuple)) else [color]
    try:
        vals = [float(v) for v in vals]
    except (TypeError, ValueError):
        return False
    if len(vals) in (1, 3):  # gray or RGB: 1 = white
        return all(v >= 0.95 for v in vals)
    if len(vals) == 4:  # CMYK: all 0 = white
        return all(v <= 0.05 for v in vals)
    return False


def pdf_visible_text(raw: bytes) -> str:
    parts = []
    with pdfplumber.open(io.BytesIO(raw)) as pdf:
        for page in pdf.pages:
            visible = page.filter(lambda o: o.get("object_type") != "char" or (
                o.get("size", 0) >= MIN_FONT_PT and not _is_white(o.get("non_stroking_color"))))
            parts.append(visible.extract_text() or "")
    return normalize("\n".join(p.strip() for p in parts if p.strip()))


class SanitizeMixin:
    def _sanitize(self, raw: str | bytes, fmt: str) -> str:
        return html_visible_text(raw) if fmt == "html" else pdf_visible_text(raw)


class D2Sanitize(SanitizeMixin, Defense):
    name = "d2_sanitize"

    def sanitize_document(self, raw, fmt, extracted):
        return self._sanitize(raw, fmt)

    def check_input(self, text: str, channel: str) -> Verdict:
        # normalize retrieved text too (already clean for sanitized docs; cheap)
        return Verdict(text=normalize(text)) if channel == "document" else Verdict()
