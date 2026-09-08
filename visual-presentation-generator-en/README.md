# Visual Presentation Generator

Turn a one-line topic into a complete, browser-renderable HTML slide deck, with
local edit checkpoints and a validation gate.

## What it produces
One LoomLoom run returns a material pack:
1. `presentation.html` — full deck HTML source-code (inline CSS/JS)
2. `content_schema` — outline + narration script
3. `design_config` — style / density / motion / brand tokens
4. `qa_report` — PASS/FAIL audit

The local agent renders the HTML source to a real page, holds two human
checkpoints (edit script / choose style), runs `scripts/validate_presentation.py`,
and only delivers when all checks pass.

## Boundaries
- Cloud = content production (text only). It cannot render, preview or edit.
- Local = rendering + confirmations + validation + delivery.

## Requirements
- Python 3.9+ (standard library only, no third-party deps)
- LoomLoom CLI + token (see `references/contracts.md`)

## Usage
See `SKILL.md` and `references/validation.md`.

## License
MIT.