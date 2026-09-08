#!/usr/bin/env python3
"""preflight.py — Hallucination-risk gate that runs BEFORE any money is spent.

Reads an input snapshot (a JSON rows file, or a default single-row topic) and
decides whether a row is SAFE to bill a cloud run for. If a row is "data-hungry"
(wants numbers / market / revenue / metrics) but no material (reference) is
provided, the cloud is likely to invent figures, so we block before the user pays.

Pure standard library. No network, no LoomLoom calls.

Usage:
  python3 preflight.py --input rows.json
  python3 preflight.py --topic "...咖啡 业绩..." --reference "" --json
Exit: 0 GREEN · 1 YELLOW · 2 RED (block)
"""
import argparse
import json
import re

# Cues that a narrative will want concrete numbers or evidence.
NUMERIC_CUES = [
    "营收", "收入", "增长", "融资", "估值", "市场", "用户", "占比", "份额",
    "业绩", "利润", "成本", "销售", "流量", "同比", "环比",
    "revenue", "funding", "valuation", "market", "users", "growth",
    "share", "mrr", "arr", "roi", "profit", "cagr",
]
CRITICAL_CUE = re.compile(r"(%|亿元|百万|同比|环比|yoy|cagr|营收|收入|估值|市场份额|cagr|revenue|users|funding|valuation)")
PLACEHOLDER = "[待用户提供]"


def _norm(s):
    return (s or "").strip().lower()


def scan_row(topic, reference):
    """Return (level: 'green'|'yellow'|'red', issues: list[str])."""
    t = _norm(topic)
    ref = _norm(reference)
    has_mat = ref not in ("", "-", "none", "n/a", "null", "[]", "{}")
    cue_caught = any(k in t for k in NUMERIC_CUES)
    critical = bool(CRITICAL_CUE.search(t))

    issues = []
    if critical and not has_mat:
        issues.append(
            "ROW wants concrete numbers/evidence but 'reference' is empty. "
            "The cloud is very likely to fabricate figures. Provide source material, "
            "or accept " + PLACEHOLDER + " placeholders instead of invented stats."
        )
        return "red", issues
    if cue_caught and not has_mat:
        return "yellow", ["No reference given and topic hints numeric content; risk of invented figures."]
    if has_mat:
        return ("green", ["Material provided; figures can trace to reference."]) if cue_caught else ("green", [])
    return "green", []


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", help="path to rows .json (list of {topic,reference})")
    ap.add_argument("--topic", help="topic string")
    ap.add_argument("--reference", default="", help="reference string")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.input:
        rows = json.load(open(args.input, encoding="utf-8"))
        if isinstance(rows, dict):
            rows = rows.get("rows", [rows])
    else:
        rows = [{"topic": args.topic, "reference": args.reference}]

    results = []
    worst = 0
    for i, r in enumerate(rows):
        level, issues = scan_row(r.get("topic", ""), r.get("reference", ""))
        code = {"green": "GREEN", "yellow": "YELLOW", "red": "RED"}[level]
        results.append({"row": i, "verdict": level, "code": code, "issues": issues})
        worst = max(worst, {"green": 0, "yellow": 1, "red": 2}[level])

    if args.json:
        print(json.dumps({"result": worst, "rows": results}, ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"[{r['code']}] row {r['row']}: " + ("; ".join(r["issues"]) if r["issues"] else "ok"))
    raise SystemExit(worst)


if __name__ == "__main__":
    main()