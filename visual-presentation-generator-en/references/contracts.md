# Contract: Visual Presentation Generator

Server-authoritative facts for the local shell. Do not guess IDs.

## Cloud template (one row = one deck)
- Template ID: `ac6b6e7a-a131-4672-b96d-89b2a850be6c`
- Version: **4** (version ID `c9f9ac44-c065-42f5-bcd0-f2f2d5d20163`) — 25 garden-skills style enum + embedded mini style guide + anti-hallucination (QA grounds against raw topic/reference; hard no-invent rules; `[user-data-required]` placeholder). Keeps v1..v3.
- Account: main account (owner 70396). Inject the token via environment variable, not `--token`.
- Default model: `ali/qwen3.7-plus` (time-limited 20% off). The user may override via the "Model" column.
- **Style column**: accepts `modern` or one of the 25 keys, e.g. `linear`, `aesop`, `stripe-press`, `apple-hig`, `muji-kenya-hara`, `vercel-mesh`, `raycast`, `notion-pre-ai`, `tufte-dataink`, `bloomberg-terminal`, `pentagram`, `headspace-meditation`, `are-na`, `y2k-retrofuturism`… Full list in `references/style-catalog.json`.

## Input row (Excel columns)

| Column | Required | Meaning |
|---|---|---|
| topic | yes | one-line subject |
| audience | optional | investors / customers / engineers |
| slide_count | optional (default 8) | number of slides (string) |
| style | optional | modern / editorial / motion / brutalist / warm |
| density | optional | low / medium / high |
| motion | optional | none / subtle / expressive |
| brand_color | optional | accent hex color |
| reference | optional | source material / URL |

## Output artifacts (one run → as raw text)

1. `presentation.html` — the full deck **HTML source-code string** (inline CSS/JS)
2. `content_schema` — outline + narration (structured text)
3. `design_config` — style / density / motion / brand / layout tokens
4. `qa_report` — PASS/FAIL audit (structure / completeness / relevance / integrity)

## Local responsibilities
- Strip the coding-fence from the compile artifact, write a real `.html`, open the preview.
- **Checkpoint 1 (edit script)**: show the outline & narration; user edits → re-run with changed input.
- **Checkpoint 2 (choose style)**: show 1–2 style directions (or the design info); user picks → regenerate.
- Run `scripts/validate_presentation.py` on every artifact; only deliver when all pass.

## Cost / billing discipline
- Quote before every paid cloud run and confirm; re-quote + re-confirm when input changes.
- No creator fee applies until a market listing is created (this is a private template).