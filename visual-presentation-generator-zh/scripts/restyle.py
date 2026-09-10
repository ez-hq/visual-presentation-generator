#!/usr/bin/env python3
"""restyle.py — RE-STYLE an already-generated deck locally, without re-running the cloud.

WHY THIS EXISTS
The cloud template does NOT consistently honor the `style` input in the step that
produces the final HTML (verified: stp_compile ignores style; stp_design only hints
it). Re-running the cloud to try different styles burns money and often returns the
same hardcoded linear look. This script lets you change the visual layer locally for
free: it swaps the presentation's CSS variables / font / accent to a named style
from references/style-tokens/*.txt, leaving the content DOM byte-for-byte untouched.

Usage:
  python3 restyle.py --html in.html --style monocle-magazine [--key STYLE_NAME] --out out.html
  python3 restyle.py --html in.html --tokens path/to/tokens.txt --out out.html
Pure stdlib. Reads the token file for the palette + typography.
"""
import argparse
import json
import re
import sys
from pathlib import Path

# emery style -> (bg ground, ink, accent, radius, font hint)
# Symmetric mapping applied against the CSS variables present in the HTML.
FALLBACKS = {
    "monocle-magazine": ("#F2EFE7", "#1A1A1A", "#C7322E", "0", "Plantin, 'Tiempos Headline', Georgia, serif"),
    "linear": ("#08090A", "#FFFFFF", "#0CE0E5", "8px", "Inter, 'Segoe UI', sans-serif"),
    "tufte-dataink": ("#FBFAF6", "#1B1B1A", "#A6300E", "0", "Georgia, serif"),
    "muji-kenya-hara": ("#FAFAF7", "#3A3A3A", "#6B6B5F", "2px", "'Helvetica Neue', Arial, sans-serif"),
    "stripe-press": ("#F6F8F9", "#0A2540", "#635BFF", "6px", "Georgia, serif"),
    "vignelli-swiss-helvetica": ("#FFFFFF", "#1A1A1A", "#E2231A", "0", "Helvetica, Arial, sans-serif"),
    "aesop": ("#F6F1E7", "#3A3229", "#7E6C57", "0", "'EB Garamond', Georgia, serif"),
}


def parse_tokens(token_text):
    """Extract colors and optional font hints from a token file. Returns a dict."""
    palette = re.findall(r"#[0-9A-Fa-f]{6}\b", token_text)
    out = {"colors": palette}
    m = re.search(r"Display:\s*([^\n•;#]+)", token_text)
    if m:
        out["display_font"] = m.group(1).strip().strip("`\"'")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", required=True, help="existing presentation.html (local, from a past run)")
    ap.add_argument("--style", default="monocle-magazine", help="a style key (monocle-magazine, superAhes…) OR a path to a tokens .txt")
    ap.add_argument("--out", default=None, help="output path (default: <html stem>-<style>.html)")
    args = ap.parse_args()

    html = Path(args.html).read_text(encoding="utf-8")
    if not html.strip().lower().startswith("<!doctype html"):
        print(f"WARN: {args.html} doesn't start with <!DOCTYPE html>; still trying")

    # resolve token source
    tokens_path = Path(args.style)
    if tokens_path.is_file():
        tok = tokens_path.read_text(encoding="utf-8")
        key = tokens_path.stem
    else:
        key = args.style
        td = Path(__file__).parent.parent / "references" / "style-tokens"
        token_file = td / f"{key}.txt"
        if token_file.is_file():
            tok = token_file.read_text(encoding="utf-8")
        else:
            tok = ""
    fb = FALLBACKS.get(key, ("#FFFFFF", "#111111", "#333333", "4px", "sans-serif"))
    palette = re.findall(r"#[0-9A-Fa-f]{6}\b", tok) or list(fb)
    ground = palette[0] if palette else fb[0]              # e.g. #F2EFE7 paper
    ink_color = palette[1] if len(palette) > 1 else fb[1]  # e.g. #1A1A1A
    accent = palette[2] if len(palette) > 2 else fb[2]     # e.g. #C7322E editorial red
    # swap to :root
    html = re.sub(r"(--bg:\s*)[^;]+", rf"\g<1>{ground}", html, count=1)
    html = re.sub(r"(--text:\s*)[^;]+", rf"\g<1>{ink_color}", html, count=1)
    html = re.sub(r"(--accent:\s*)[^;]+", rf"\g<1>{accent}", html, count=1)
    html = re.sub(r"(--brand:\s*)[^;]+", rf"\g<1>{accent}", html, count=1)
    # radius
    html = re.sub(r"(--radius:\s*)[^;]+", rf"\g<1>{fb[3]}", html, count=1) if "--radius:" in html else html
    # body font
    font = fb[4] if isinstance(fb[4], str) and fb[4] else "Georgia, serif"
    html = re.sub(r"body\s*\{[^}]*font-family:[^;]+;",
                  lambda m: m.group(0).replace("font-family: " + m.group(0).split("font-family:")[1].split(";")[0] + ";",
                                              "font-family: " + font + ";"), html, count=1)
    # generic font-family fallback for any serif usage
    html = re.sub(r"font-family:\s*'?GT Sectra'?,? ?serif;?", "font-family: " + font + ";", html)

    out = args.out or str(Path(args.html).with_name(Path(args.html).stem + "-" + key.replace("/", "-") + ".html"))
    Path(out).write_text(html, encoding="utf-8")
    print(f"Restyled {args.html} -> {out} (style: {key})")
    print(f"  palette: {' '.join(palette[:4])} / ink={ink_color} / accent={accent}")
    print("  NOTE: content DOM unchanged; only CSS vars/font swapped (best-effort before a full style token rewrite).")


if __name__ == "__main__":
    main()