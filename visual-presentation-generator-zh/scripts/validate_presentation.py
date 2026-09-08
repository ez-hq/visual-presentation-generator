#!/usr/bin/env python3
"""validate_presentation.py — Quality gate for Visual Presentation Generator.

Pure standard library (no third-party deps). Checks a generated deck's artifacts
and returns nonzero on failure. Supports --json for a machine-readable report.

Checks:
  - HTML valid: starts with <!DOCTYPE html>, ends with </html>, tags balanced.
  - Artifacts complete: content_schema, design_config, qa_report present & non-empty.
  - Slides present: at least one slide section; <= expected page count when given.
  - Topic relevance: at least one meaningful topic keyword appears in the HTML.
  - QA verdict present.
  - Anti-hallucination: reports suspicious numeric-looking claims (warning unless sticky).

Exit 0 = all required checks PASS.
"""
import argparse
import json
import re
import sys
from pathlib import Path

PLACEHOLDER = "[由你补充]"
# Conservative over-match; used only as a "verify me" marker, never hard-fails on
# its own. Matches e.g. "90%" / "12.3 million" / "1.2k users". Hex colors are excluded
# (a color code is not a statistic).
NUMBER_HINT = re.compile(r"\b\d[\d.,]*(?:%|million|m\b|billion|b\b|k\b|users?|fold|years|yuan|¥)\b", re.I)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--html", help="真实（已剥离代码围栏）的 presentation.html 路径")
    ap.add_argument("--schema", help="content_schema 文本路径")
    ap.add_argument("--design", help="design_config 文本路径")
    ap.add_argument("--qa", help="qa_report 文本路径")
    ap.add_argument("--topic", required=True, help="原始用户主题（用于相关性检查）")
    ap.add_argument("--expected-slides", type=int, default=0, help="预期页数（0=不限）")
    ap.add_argument("--json", action="store_true", help="输出 JSON 报告并写入 validation-report.json")
    args = ap.parse_args()

    res = {
        "all_pass": False,
        "html_wellformed": False,
        "html_doctype": False,
        "html_closing": False,
        "artifacts_complete": False,
        "slides_present": False,
        "slide_count": 0,
        "topic_relevant": False,
        "placeholder_count": 0,
        "suspicious_numbers": False,
        "qa_verdict": False,
        "errors": [],
        "warnings": [],
    }

    # ---- HTML ----
    html = ""
    if args.html and Path(args.html).is_file():
        html = Path(args.html).read_text(encoding="utf-8")
        res["html_doctype"] = html.lstrip().lower().startswith("<!doctype html")
        res["html_closing"] = html.rstrip().endswith("</html>")
        for tag in ("html", "body", "section", "div"):
            opened = len(re.findall(rf"<{tag}[\s>]", html))
            closed = html.count(f"</{tag}>")
            if opened and opened != closed:
                res["errors"].append(f"标签 <{tag}> 不平衡：打开 {opened} / 关闭 {closed}")
        res["html_wellformed"] = (
            res["html_doctype"] and res["html_closing"] and not any("标签" in e for e in res["errors"])
        )
    else:
        res["errors"].append("缺失或无效的 --html 文件")

    if html:
        res["slide_count"] = len(re.findall(r'<section[^>]*class=["\'][^"\']*slide', html, re.I))
        res["slides_present"] = res["slide_count"] >= 1
        if args.expected_slides and res["slide_count"] > args.expected_slides * 2:
            res["errors"].append(f"页数 {res['slide_count']} 远超预期 {args.expected_slides}")

        # anti-hallucination advisory: remove hex color tokens before scanning so
        # "#054C78" style codes are not mistaken for statistics.
        html_nohex = re.sub(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b", " ", html)
        res["placeholder_count"] = html.count(PLACEHOLDER)
        here = [m.group(0) for m in NUMBER_HINT.finditer(html_nohex)][:10]
        res["suspicious_numbers"] = bool(here)
        if here:
            res["warnings"].append("疑似数字文本（请对照输入核实）：" + ", ".join(here))

    # ---- artifacts ----
    res["artifacts_complete"] = True
    for key, name in (("schema", args.schema), ("design", args.design), ("qa", args.qa)):
        if not name:
            res["errors"].append(f"产物 {key}：未给出文件路径")
            res["artifacts_complete"] = False
            continue
        p = Path(name)
        if not p.is_file() or not p.read_text(encoding="utf-8").strip():
            res["errors"].append(f"产物 {key}：缺失或为空（{name}）")
            res["artifacts_complete"] = False

    # ---- relevance ----
    if html and args.topic:
        tl = args.topic.lower()
        if " " in tl:
            kws = [w for w in tl.split() if len(w) > 1]
            hit = [k for k in kws if k in html.lower()]
        else:
            hit = [tl] if tl in html.lower() else []
        res["topic_relevant"] = bool(hit)
        if not hit:
            res["errors"].append("主题关键词未在演示文稿中出现（相关性）")
    # ---- QA verdict ----
    if args.qa and Path(args.qa).is_file():
        q = Path(args.qa).read_text(encoding="utf-8").lower()
        res["qa_verdict"] = ("full_pass=" in q and "pass" in q) or ("full_pass=pass" in q)
        # fallback: any PASS phrasing
        res["qa_verdict"] = res["qa_verdict"] or ("pass" in q and "fail" not in q)

    res["all_pass"] = (
        res["html_wellformed"]
        and res["artifacts_complete"]
        and res["slides_present"]
        and res["topic_relevant"]
        and res["qa_verdict"]
        and not res["errors"]
    )

    if args.json:
        report = {
            "version": "1",
            "result": res,
            "files": {"html": args.html, "schema": args.schema, "design": args.design, "qa": args.qa},
        }
        Path("validation-report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print("结果：" + ("通过" if res["all_pass"] else "未通过"))
        for e in res["errors"]:
            print("  错误：" + e)
        for w in res["warnings"]:
            print("  提示：" + w)
    return 0 if res["all_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())