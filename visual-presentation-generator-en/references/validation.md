# Validation rules: Visual Presentation Generator

The local validator runs after every cloud result and before delivery. It is the
quality gate: **everything must pass or be resolved before delivery**. Reject
fabricated, mismatched, or unreviewable conclusions; never silently invent data.

## What `validate_presentation.py` checks

| Check | Pass rule (quantified) |
|---|---|
| HTML parsed / well-formed | starts with `<!DOCTYPE html>`; ends with `</html>`; structural tags balanced |
| Artifact completeness | HTML source, content_schema, design_config, qa_report all present & non-empty |
| Slides present | `<section … slide>` count >= 1; not far beyond the expected page count |
| Topic relevance | at least one meaningful topic keyword appears in the deck |
| Anti-hallucination | no bare fabricated statistic; missing data marked `[fill-in]` or from input |
| QA report sane | qa_report exists and states a verdict (PASS/FAIL or `FULL_PASS`) |

## Rejection / audit policy
- Structural or completeness FAIL → report the exact failing item + what the user
  should supply / which parameter to change; retry; do **not** deliver a placeholder `.html`.
- A number not present in the user input and not flagged `[fill-in]` → treat as
  "suspicious"; confirm with the user before delivering.
- Do not turn a subjective taste judgment (e.g. "this color looks bad") into an
  automatic rule; keep it as a review note.

## Output files (write into the working `review/`)
- `review/validation-report.json` — structured validator result
- `review/local-audit.json` — audit of cloud artifacts + Checkpoint decisions
- `review/final-report.md` — human-readable delivery report

## Example
```
python3 scripts/validate_presentation.py --html review/presentation.html \
  --schema review/content_schema.txt --design review/design_config.txt \
  --qa review/qa_report.txt --topic "Visual Presentation Generator"
```
Exit 0 = all pass; with `--json` it prints a machine-readable report.