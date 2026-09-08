# Output schema: Visual Presentation Generator

One cloud run returns 4 text artifacts. This describes the expected structure of
each, for local validation and consumption.

## 1. presentation.html
- Self-contained single-file deck with `<style>` (design tokens) and `<script>`
  (slide navigation / keyboard arrows / motion).
- Each slide wrapped as `<section class="slide">`.
- No external fonts/resources/base64 images; missing numbers marked `[fill-in]`.

## 2. content_schema
Text outline + narration. Target structure:
```
slide_index | title | key_points[] | narration
```
The cloud returns "BLOCK 1 outline + BLOCK 2 script"; local normalizes to the
fields above.

## 3. design_config
JSON shape:
```json
{
  "design_config": {
    "styleName": "editorial",
    "color": {"background":"#FFFFFF","text":"#1E293B","accent":"#2563EB","brand":"#2563EB"},
    "typography": {"heading":"...","body":"...","family":"..."},
    "density": "medium",
    "motion": "subtle",
    "slideLayout": "...",
    "imageUsage": "...",
    "brandFidelity": 0.8
  }
}
```

## 4. qa_report
Text audit covering:
- structural validity (doctype / closing / no broken tags)
- completeness (all outline slides appear)
- relevance (topic keywords present)
- integrity (numbers from input or marked `[fill-in]`, no fabricated stats)
- ends with `FULL_PASS=PASS|FAIL`

## Validation
If anything cannot be satisfied or mapped to the input → "re-run / adjust param",
never deliver a placeholder.