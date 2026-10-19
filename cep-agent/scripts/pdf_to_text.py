#!/usr/bin/env python3
"""Convert a local PDF into research/text/<name>.txt. Requires: pip install pymupdf"""
import os, sys
import fitz  # pymupdf
if len(sys.argv) < 2:
    sys.exit("usage: python scripts/pdf_to_text.py paper.pdf")
src = sys.argv[1]
os.makedirs("research/text", exist_ok=True)
out = os.path.join("research", "text", os.path.splitext(os.path.basename(src))[0] + ".txt")
doc = fitz.open(src)
with open(out, "w", encoding="utf-8") as f:
    for i, page in enumerate(doc, 1):
        f.write(f"\n\n=== page {i} ===\n")
        f.write(page.get_text())
print("wrote", out, "pages:", len(doc))
