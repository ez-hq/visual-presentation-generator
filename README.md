# Visual Presentation Generator

Turn a one-line topic into a complete, browser-renderable HTML slide deck, with
local edit checkpoints and a hard anti-hallucination gate.

Dual-language SkillBot, deployed to the Shengsuanyun / LoomLoom platform
(billed in CNY). Every cloud run states its estimated ¥ fee first and deducts only
after the user confirms. Install either the Chinese or English package.

## What it produces (one cloud run)
1. `presentation.html` — full deck HTML source (inline CSS/JS)
2. `content_schema` — outline + narration script
3. `design_config` — style / density / motion / brand tokens
4. `qa_report` — PASS/FAIL audit (grounded against the raw user input, v4+)

## Two packages (choose one)
| Package | Content | Cloud output |
|---|---|---|
| `-zh.zip` | Simplified Chinese full package | defaults to Chinese |
| `-en.zip` | English-only (0 CJK in docs) | defaults to English |

## Source layout (single source per language)
- `visual-presentation-generator-en/` — English source (SKILL/README/refs/scripts all English)
- `visual-presentation-generator-zh/` — Chinese source

Cloud templates / prompts are proprietary and are NOT in this public repo.

## Build
```bash
./build.sh v1.2.0      # → dist/<name>-zh.zip, -en.zip, <name>.zip + sha256
```

## Docs
- `SKILL.md` in each package — usage, quote/confirm, preflight, checkpoints
- 25 named HTML styles (linear, aesop, stripe-press, muji-kenya-hara…) from
  ConardLi/garden-skills (MIT) — attribution in each package's
  `references/NOTICE-garden-skills.md`.

## License
MIT (local code/package content only). Cloud templates & prompts remain
proprietary.