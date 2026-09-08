#!/usr/bin/env python3
"""build_style_catalog.py — Distill garden-skills style-recipes into compact tokens.

Pure standard library. Reads references/style-recipes/*.md and writes TWO artifacts
used by the local shell AND (optionally) the cloud design step's system prompt:

  references/style-catalog.json       — machine-readable token dictionary (id -> blocks)
  references/style-tokens/            — one .txt prompt-ready token block per style

Attribution: these design tokens are condensed from ConardLi/garden-skills
(https://github.com/ConardLi/garden-skills, MIT). Design language is verbatim
essence; see references/NOTICE-garden-skills.md.
"""
import argparse
import json
import re
from pathlib import Path

BLOCKS = ("Palette", "Typography", "Spacing", "Radius", "Shadow", "Motion",
          "Signature moves", "Avoid")


def section(md: str, name: str) -> str:
    pat = re.compile(rf"^\*\*{re.escape(name)}\*\*(.*?)(?=^\*\*|\Z)", re.M | re.S)
    m = pat.search(md)
    if not m:
        return ""
    s = re.sub(r"[ \t]+", " ", m.group(1)).strip()
    return s


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--recipes", required=True, type=Path, help="style-recipes dir")
    ap.add_argument("--out-json", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    catalog = []
    for rp in sorted(args.recipes.glob("*.md")):
        md = rp.read_text(encoding="utf-8")
        first = md.splitlines()[0] if md.splitlines() else rp.stem
        m = re.match(r"^#\s+([\w-]+)\s*(?:[—–-])?\s*(.*)$", first)
        name = (m.group(2) or rp.stem).strip()
        item = {"id": rp.stem, "name": name}
        for b in BLOCKS:
            item[b.lower().replace(" ", "_")] = section(md, b)
        catalog.append(item)
        # per-style prompt token
        tok = [
            f"STYLE: {item['id']} — {item['name']}",
            f"Palette: {item['palette']}",
            f"Typography: {item['typography']}",
            f"Spacing: {item['spacing']}",
            f"Radius: {item['radius']}",
            f"Shadow: {item['shadow']}",
            f"Motion: {item['motion']}",
            f"Signature: {item['signature_moves']}",
            f"Avoid: {item['avoid']}",
        ]
        (args.out_dir / f"{item['id']}.txt").write_text("\n".join(tok), encoding="utf-8")

    payload = {"source": "ConardLi/garden-skills (MIT)", "count": len(catalog), "styles": catalog}
    args.out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(catalog)} styles -> json {args.out_json} + {args.out_dir}/")


if __name__ == "__main__":
    raise SystemExit(main())