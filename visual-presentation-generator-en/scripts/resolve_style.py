#!/usr/bin/env python3
"""resolve_style.py — resolve a user's desired style to one of the 25 legal cloud keys BEFORE paying.

Root-cause fix: the cloud stp_design step only knows 25 hardcoded style keys
(style-catalog.json) and passes `style` through as free text with no enum check.
If a user's style intent (e.g. "editorial") is not among the 25, the cloud model
silently falls back to default `linear` — the user pays for a wrong look. This
gate intercepts before submission:
  - exact hit of a legal key -> use (exit 0)
  - alias / semantic match -> map to the closest legal key and explain (exit 1)
  - no match -> list candidates, do NOT enter the cloud (exit 2)
Pure stdlib, no network. Usage: python3 resolve_style.py --style "<user style>"
"""
import argparse
import json
import re

LEGAL = {
    "active-theory", "aesop", "apple-hig", "are-na", "balenciaga-post-2017",
    "bloomberg-businessweek-turley", "bloomberg-terminal", "dieter-rams-braun",
    "field-io", "headspace-meditation", "linear", "mailchimp-freddie",
    "mid-century-modern", "monocle-magazine", "muji-kenya-hara", "notion-pre-ai",
    "nyt-the-daily", "pentagram", "raycast", "resn-storytelling", "stripe-press",
    "tufte-dataink", "vercel-mesh", "vignelli-swiss-helvetica", "y2k-retrofuturism",
}

# alias / near-synonym -> legal key. editorial = editorial-magazine look; prefer a
# light magazine key.
ALIASES = {
    "editorial": "monocle-magazine",
    "magazine": "monocle-magazine",
    "mag": "monocle-magazine",
    "journal": "monocle-magazine",
    "newspaper": "nyt-the-daily",
    "press": "nyt-the-daily",
    "news": "nyt-the-daily",
    "minimal": "muji-kenya-hara",
    "simple": "muji-kenya-hara",
    "corporate": "stripe-press",
    "startup": "linear",
    "tech": "linear",
    "data": "tufte-dataink",
    "maximal": "pentagram",
    "swiss": "vignelli-swiss-helvetica",
    "international": "vignelli-swiss-helvetica",
}


def norm(s):
    return re.sub(r"[\s_\-]+", "", (s or "").strip().lower())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--style", required=True, help="user's desired style (editorial / magazine / linear ...)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    raw = (args.style or "").strip()
    n = norm(raw)

    payload = {"input": raw, "action": "?", "key": None, "reason": "", "candidates": []}

    if n in LEGAL:
        payload.update(action="use", key=n, reason="exact hit of a legal style key")
    else:
        hit = None
        for alias, key in ALIASES.items():
            if alias in raw or norm(alias) in n:
                hit = key
                break
        if hit:
            payload.update(action="map", key=hit,
                           reason=f"'{raw}' is not one of the 25 keys; mapped to '{hit}' (confirm before entering the paid cloud)")
        else:
            for legal in sorted(LEGAL):
                if legal.split("-")[0] in n and len(legal) > 3:
                    payload["candidates"].append(legal)
            payload.update(action="fail",
                           reason=f"'{raw}' is not a supported style key and cannot be auto-mapped. Choose one of the candidates:")

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"[{payload['action'].upper()}] input={raw!r}")
        print("  " + payload["reason"])
        if payload["candidates"]:
            print("  candidates: " + ", ".join(payload["candidates"]))
    code = {"use": 0, "map": 1, "fail": 2}[payload["action"]]
    raise SystemExit(code)


if __name__ == "__main__":
    main()