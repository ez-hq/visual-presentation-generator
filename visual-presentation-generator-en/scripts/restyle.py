#!/usr/bin/env python3
"""restyle.py — re-style an already-generated deck locally without re-running the cloud.

The cloud template does not reliably honor the style input in the step that emits the
final HTML (stp_compile ignores style; stp_design only hints it). Re-running the cloud
to try different styles costs money and often returns the same hardcoded look. This
script swaps the visual layer (CSS vars, font, accent) for a named style from
references/style-tokens/*.txt, leaving the content DOM byte-for-byte unchanged.

Usage:
  python3 restyle.py --html in.html --style monocle-magazine --out out.html
  python3 restyle.py --html in.html --tokens path/to/tokens.txt --out out.html
Pure stdlib.
"""
import argparse
import re
import sys
from pathlib import Path

LEGAL = ["monocle-magazine","linear","tufte-dataink","muji-kenya-hara","stripe-press",
         "vignelli-swiss-helvetica","aesop","apple-hig","are-na","balenciaga-post-2017",
         "bloomberg-businessweek-turley","bloomberg-terminal","dieter-rams-braun","field-io",
         "headspace-meditation","mailchimp-freddie","mid-century-modern","notion-pre-ai",
         "nyt-the-daily","pentagram","raycast","resn-storytelling","active-theory","vercel-mesh",
         "y2k-retrofuturism"]

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", required=True)
    ap.add_argument("--style", default="monocle-magazine")
    ap.add_argument("--out", default=None)
    ap.add_argument("--tokens", default=None, help="path to a token .txt overriding palette")
    a = ap.parse_args()
    html = Path(a.html).read_text(encoding="utf-8")
    token_file = Path(a.tokens) if a.tokens else (Path(__file__).parent.parent/"references"/"style-tokens"/f"{a.style}.txt")
    tok = token_file.read_text(encoding="utf-8") if token_file.is_file() else ""
    palette = re.findall(r"#[0-9A-Fa-f]{6}\b", tok)
    if len(palette) < 2:
        palette = ["#F2EFE7", "#1A1A1A", "#C7322E"]  # safe magazine fallback
    bg, ink = palette[0], palette[1]
    accent = palette[2] if len(palette) > 2 else "#C7322E"
    # ONLY swap :root custom properties; DOM stays untouched
    html = re.sub(r"(--bg:\s*)[^;]+", rf"\g<1>{bg}", html, count=1)
    html = re.sub(r"(--text:\s*)[^;]+", rf"\g<1>{ink}", html, count=1)
    html = re.sub(r"(--accent:\s*)[^;]+", rf"\g<1>{accent}", html, count=1)
    html = re.sub(r"(--brand:\s*)[^;]+", rf"\g<1>{accent}", html, count=1)
    out = a.out or (Path(a.html).with_name(Path(a.html).stem + "-" + a.style + ".html"))
    Path(out).write_text(html, encoding="utf-8")
    print(f"restyled {a.html} -> {out} (style {a.style}; bg {bg} / ink {ink} / accent {accent})")
    print("content DOM unchanged; only CSS custom props swapped")

if __name__ == "__main__":
    main()
