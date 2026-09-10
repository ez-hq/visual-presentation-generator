---
name: visual-presentation-generator
description: >-
  Generates a complete, browser-renderable HTML slide deck from a one-line topic.
  Cloud (LoomLoom) produces a full material pack (HTML source, content schema,
  design config, QA report); the local shell renders the HTML source into a real
  page, enforces two human checkpoints (edit script / choose style) via render-
  then-confirm, validates every artifact, and delivers. Use when a user wants a
  topic turned into a styled, self-contained HTML presentation / slide deck.
---

# Visual Presentation Generator

## What this Skill does
Turns a topic into a self-contained HTML slide deck plus a structured outline,
design config, and QA report. One topic = one deck.

## Before you start: Language (set by your zip)

- zip name contains `-zh` = Simplified Chinese → cloud output defaults to Chinese
- zip name contains `-en` = English → cloud output defaults to English

> The local full package behaves identically in both; only the cloud output
> language differs (follows your zip).
>
> Cloud execution runs only on Shengsuanyun (LoomLoom), billed in CNY. **Before
> every cloud run I state the estimated fee for that run (a ¥ amount) and deduct
> only after you confirm.** Pages needing numbers/metrics MUST be fed source
> material by you; missing figures always use `[user-data-required]` placeholders —
> the cloud never invents statistics.

## Responsibility split
- **Cloud (LoomLoom) = content production only.** It returns the presentation
  **HTML as a source-code string** (text/plain). The cloud cannot render, preview,
  screenshot, package, or edit.
- **Local (this Skill + you) = the delivery surface.** You render the HTML source
  into a real `.html`, open the preview, run the two human checkpoints (edit
  script / choose style), validate every artifact, and deliver/report. **The two
  checkpoints cannot live on the cloud.**

## Platform reality (authoritative)
- LoomLoom model steps: text / image / video / audio / model3d only. No code/browser
  step.
- `capability resolve` accepts only text / audio / video / image output.
- HTML is delivered as a `text/plain` / `.txt` source string; rendering and preview
  are local.
- No streaming, so all confirmation happens in local orchestration.

## Workflow (quote → confirm → run → wrap-up)

1. **One-line deliverable** - Tell the user what they get:
   "This topic → you get a full editable HTML deck (previewable and editable)."
2. **Converge input one question at a time** —
   Ask in order: `topic` (required) → `audience` (optional) → slide count/style
   (optional) → source/link (optional). Ask only one at a time.
3. **Local precheck (free)** — ensure `topic` is non-empty and page count ≤ 30.
3b. **Hallucination-risk preflight (mandatory, BEFORE quote; free, CPU only)** — run
   `scripts/preflight.py --topic "<topic>" --reference "<material>" --json` before any quote:
   - RED (exit 2): topic demands numbers/metrics/market/funding but `reference` is empty →
     BLOCK quoting and submission. User must provide material, or explicitly accept
     `[user-data-required]` placeholders. Never spend money on an input that will almost surely
     fabricate data.
   - YELLOW (exit 1): numeric cues but no material → warn the user, confirm to continue.
   - GREEN (exit 0): safe to quote.
4. **Quote → explicit confirm (spending node)**
   ```
   This run: 1 deck ≈ ¥Y (private template: model cost only)
   Will call the cloud to generate (CNY).
   Confirm and execute? (yes / no)
   ```
   Do not run without an explicit "yes".
5. **Choose the style template (ask before running the cloud + normalize it to a legal key)** — before submitting
   any cloud run, you MUST ask the user which visual template / style they want, then run it through
   `scripts/resolve_style.py`:
   - List the available styles: default `modern`, plus the 25 named style keys (e.g.
     `linear`, `aesop`, `apple-hig`, `muji-kenya-hara`, `stripe-press`, `vercel-mesh`,
     full list in `references/style-catalog.json`).
   - Ask explicitly: **"Which style template / visual style should this deck use?"**
     Offer 2–4 recommendations that fit the topic plus "Other (type a style key or
     description)".
   - **Run `python3 scripts/resolve_style.py --style "<user style>" --json` (local, free)**:
     - `action = use` (exit 0): exact legal key — write that `key` into the `style` column.
     - `action = map` (exit 1): not a legal key; mapped to a close one (e.g. `editorial ->
       monocle-magazine`). **You MUST tell the user the mapping and get their confirmation,
       then write the mapped `key` to the `style` column.** Never forward the raw unknown word to the cloud.
     - `action = fail` (exit 2): cannot map — list candidates and let the user re-pick; do NOT enter the cloud.
   - **Do not run the cloud before the user explicitly chooses AND the resolved key is confirmed.**
   - Default `style` column value if left empty: `linear`.
6. **Run once in the cloud** - via LoomLoom `template-spec run / submit-workbook`;
   template and version are in `references/contracts.md`. One row = one deck.
7. **Render locally + validate (free)** — take the compile artifact (HTML source),
   strip the code fence into a real `.html`, open the preview; run
   `scripts/validate_presentation.py --run-id <cloudRunId> --source "<raw material>" --html ... --schema ... --design ... --qa ...`.
   - **`--run-id` required** (must be a valid uuid returned by the cloud): the validator
     hard-fails without a cloud run id — this provenance gate ensures the deck really
     came through the full cloud chain, not fabricated locally.
   - **`--source` passes the raw material**: the validator enforces **unit fidelity** —
     if the source says "3.2Yi-yuan" but the HTML shows `million/billion`, it fails and
     refuses delivery (blocks unit-drift hallucination).
   - **Strict QA verdict**: PASS only when the QA report explicitly says
     `FULL_PASS=PASS`; a QA `FAIL` always blocks delivery.
   - If any hard gate fails → report what failed and what else is needed; fix and
     re-run; **never deliver a placeholder deck**.
   - **Checkpoint 1 (edit script)**: show the content + narration, let the user
     confirm or edit. If edited, re-run (re-preflight and re-run the cloud).
   - **Checkpoint 2 (choose style)**: if the style can still be tuned, show alternate
     style directions; user picks → regenerate with the new config.
8. **Deliver + summary**: give `presentation.html` (openable), `design_config`,
   `content_schema`, `qa_report`; summarize where, how long, cost. Expose no tokens
   or internal IDs.

8b. **Style mismatch -> re-style locally; never re-run the cloud for style (money saver)**:
   - Known: the cloud's honor of `style` is unreliable (`stp_compile` ignores style;
     `stp_design` only hints; passing `editorial` or `monocle-magazine` may still fall
     back to Linear dark #08090A). Treat any style mismatch as NOT a content re-run.
   - If only the look is off: `scripts/restyle.py --html <generated.html> --style <legal key>`
     to swap the visual layer locally for free (CSS vars / palette / accent); the body
     DOM is byte-for-byte unchanged.
   - Re-run the cloud ONLY for content problems; for style issues always restyle locally.
     Never re-run an already-good cloud deck just to change its style (it burns money and
     may regenerate broken content, as seen in run2).

## Quality gate (before deliver)
- Every artifact must pass `scripts/validate_presentation.py`; deliver **only after
  all required checks PASS**.
- Otherwise return "what failed and what the user must supply", fix, re-run, then
  deliver.
- Reject fabricated / unsupported / unreviewable conclusions. Numbers may only come
  from user input or be explicitly marked `[fill-in]`.

## Docs
- `references/contracts.md` — cloud template/version, input fields, output schema
- `references/validation.md` — validation checks and thresholds
- `references/schema.md` — schema of the four deliverables
- `agents/openai.yaml` — platform metadata

## Notes
- Speak the user's language. Keep file names and code in English.
- Do not publish to Market unless the user explicitly asks.