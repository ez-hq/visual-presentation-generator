#!/usr/bin/env python3
"""resolve_style.py — 在花钱之前把「用户想要的风格」解析成云端 25 个合法风格键之一。

根因修复：模板 stp_design 只认识 25 个写死的风格键（style-catalog.json），
且云端把 style 当自由文本透传、无枚举校验。若用户给的风格意图（如 editorial）
不在 25 键内，云端模型会静默 fallback 到默认 linear——用户白跑一次并付费。
本脚本在提交云端之前拦截映射：
  - 精确命中 25 键 -> 直接用（matched）
  - 命中别名/语义 -> 映射到最贴近的合法键并说明（mapped，需用户确认）
  - 无匹配 -> 列候选让用户选（fail，禁止进云端）
pure stdlib，无网络。用法：python3 resolve_style.py --style "<用户想要的风格>"
"""
import argparse
import json
import re
from pathlib import Path

LEGAL = {
    "active-theory", "aesop", "apple-hig", "are-na", "balenciaga-post-2017",
    "bloomberg-businessweek-turley", "bloomberg-terminal", "dieter-rams-braun",
    "field-io", "headspace-meditation", "linear", "mailchimp-freddie",
    "mid-century-modern", "monocle-magazine", "muji-kenya-hara", "notion-pre-ai",
    "nyt-the-daily", "pentagram", "raycast", "resn-storytelling", "stripe-press",
    "tufte-dataink", "vercel-mesh", "vignelli-swiss-helvetica", "y2k-retrofuturism",
}

# 别名/近义 -> 合法键。editorial=专业杂志感，优先映射浅色杂志系。
ALIASES = {
    "editorial": "monocle-magazine",
    "杂志": "monocle-magazine",
    "杂志感": "monocle-magazine",
    "专业杂志": "monocle-magazine",
    "newspaper": "nyt-the-daily",
    "报刊": "nyt-the-daily",
    "报纸": "nyt-the-daily",
    "新闻编辑": "nyt-the-daily",
    "新闻": "nyt-the-daily",
    "极简": "muji-kenya-hara",
    "简约": "muji-kenya-hara",
    "商务": "stripe-press",
    "创业公司": "linear",
    "tech": "linear",
    "科技": "linear",
    "数据": "tufte-dataink",
    "极繁": "pentagram",
    "swiss": "vignelli-swiss-helvetica",
    "瑞士": "vignelli-swiss-helvetica",
    "国际主义": "vignelli-swiss-helvetica",
}


def norm(s):
    return re.sub(r"[\s_\-]+", "", (s or "").strip().lower())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--style", required=True, help="用户想要的风格（editorial / 杂志 / linear …）")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    raw = (args.style or "").strip()
    n = norm(raw)

    payload = {"input": raw, "action": "?", "key": None, "reason": "", "candidates": []}

    if n in LEGAL:
        payload.update(action="use", key=n, reason="精确命中合法风格键")
    else:
        hit = None
        for alias, key in ALIASES.items():
            if alias in raw or norm(alias) in n:
                hit = key
                break
        if hit:
            payload.update(action="map", key=hit,
                           reason=f"“{raw}”不在 25 键内，已就近映射为「{hit}」（请先确认此映射，再进入云端付费）")
        else:
            # 语义兜底：按包含词找最接近的合法键
            for legal in sorted(LEGAL):
                if legal.split("-")[0] in n and len(legal) > 3:
                    payload["candidates"].append(legal)
            payload.update(action="fail", reason=f"“{raw}”不是支持的风格键，且无法自动映射。请从候选中选择：")

    if args.json:
        import json as _j
        print(_j.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"[{payload['action'].upper()}] 输入={raw!r}")
        print("  " + payload["reason"])
        if payload["candidates"]:
            print("  候选: " + ", ".join(payload["candidates"]))
    code = {"use": 0, "map": 1, "fail": 2}[payload["action"]]
    raise SystemExit(code)


if __name__ == "__main__":
    main()