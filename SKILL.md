---
name: tk-auto-edit-simple
description: Turn 1–2 local product videos into two 10–15s silent 9:16 TikTok Shop cuts. Uses a replaceable planner (Codex by default; Doubao/manual compatible), Montaj for exact cutting, and portable FFmpeg 8.1.2 for rendering. Supports REPRODUCE and VARIATION.
---

# TK 自动剪辑简单化

## Purpose

Use this skill when the user provides 1–2 product MP4 files plus a product name and up to 3 core selling points and wants fast TikTok Shop product-video cuts without BGM.

Frozen execution architecture:

`Planner -> Montaj -> portable FFmpeg 8.1.2`

The planner is replaceable. Codex is the reference planner; Doubao is supported through the documented two-stage planner protocol.

## Frozen baseline

- Montaj: `theSamPadilla/montaj` commit `4dfe02ab789868ee599574d945d14519ba1b1fc8`
- FFmpeg / ffprobe: portable 8.1.2
- Core runner: `workflow/run_workflow.py`
- Do not modify Montaj or the core runner for normal use.
- Do not require BGM, Node, Puppeteer, Whisper, browser automation, or an external LLM API for the render layer.

## Minimum input

Required:
- `1.mp4`
- product name
- 1–3 core selling points

Optional:
- `2.mp4`

Write text input to `templates/product_brief.json`.

## Output contract

Always target two versions unless the user explicitly asks otherwise.

### B_result_first
`Pain/Result -> Product/Proof -> Demo/Install -> Result/Feature`

### C_product_logic
`Product Hero -> Feature/Durability -> Install/Demo -> Result`

Each version:
- 5–8 clips
- 10–15 seconds total
- each clip 0.8–3.0 seconds, normally 0.8–2.5
- 1080x1920
- 30fps
- H.264
- silent / no BGM
- at most 4 English copy items
- <= 6 English words per copy item

## Source Gate

Allowed values only:
- `CLEAN_SOURCE`
- `CROPPABLE_TEXT`
- `MASKABLE_TEXT`
- `SOURCE_TEXT_LIMITATION`

`SOURCE_TEXT_LIMITATION` is a reportable limitation, not a request for complex cleanup. Do not default to OCR, inpainting, AI text removal, tracking, or watermark removal. Cropping or simple masking is not a copyright solution.

## Clip planning

Priority:

`strong action > visible result > demo > differentiating feature > detail > install > static hero`

Avoid:
- pure title cards
- blank / low-information transitions
- repeated near-identical actions
- clips that obscure the product
- mechanically forcing every segment to ~2 seconds
- unsupported product claims

Basic mode does not attempt advanced emotional pacing; that belongs to the separate advanced-editing project.

## Planning modes

### VARIATION (default)

- Compare at most the latest 3 plans.
- Prefer changing the first 0–2s Hook.
- Then replace 1–3 middle clips when good alternatives exist.
- Copy may vary while staying truthful.
- Target overlap with the latest same-structure plan: `<= 0.70`.
- If source is too limited, preserve quality and report `VARIATION_LIMITED_BY_SOURCE`.
- Never overwrite history.

### REPRODUCE

Use an existing plan exactly. Preserve source files, in/out timecodes, order, copy, copy timing, and crop mode. If the requested plan is missing, return `REPRODUCE_PLAN_MISSING`; never silently re-plan.

## Codex mode

1. Read `templates/product_brief.json`.
2. Analyze source using the frozen runner and representative frames.
3. Read `prompts/codex_planner.md`.
4. Assign Source Gate.
5. Produce valid `plan.json`.
6. Run the frozen Montaj + FFmpeg workflow.
7. Verify outputs with ffprobe and report limitations.

Codex may combine analyze/plan/render when it has local file and shell access.

## Doubao mode — mandatory two-stage planning

Doubao is a planner only. Do **not** ask it to jump directly from a contact sheet to final `plan.json`.

1. Generate representative frames at about 1 fps. Every cell must be traceable to `source filename + original timestamp`, e.g. `4.mp4 | 00:32`.
2. Send product name, up to 3 selling points, and labeled contact sheets.
3. Ask for Candidate Shot List only: `source | time range | visual content | recommended use`.
4. Check obvious filename/time/content mismatches.
5. Lock the candidate pool. Final plan may use only accepted candidate ranges.
6. Ask Doubao for final `plan.json` using `templates/plan.json`.
7. Validate source names, clip count, duration, copy constraints, Source Gate, and candidate-pool compliance.
8. If only a field/copy is wrong, request local correction only; do not re-plan everything.
9. Save final `plan.json` and render locally.

Stop instead of inventing a plan when timestamps cannot be resolved, Doubao cannot inspect the images, or candidate ranges are guessed.

Full wording: `prompts/doubao_planner.md` and `docs/DOUBAO_QUICKSTART.md`.

## Labeled contact sheet helper

`tools/make_labeled_contact_sheet.py` is a packaging helper for non-Codex planners. It does not change the frozen core workflow.

## Execution

Analyze:

```bash
python workflow/run_workflow.py analyze \
  --input /path/to/1.mp4 \
  --input /path/to/2.mp4 \
  --ffmpeg /path/to/ffmpeg \
  --ffprobe /path/to/ffprobe \
  --out-dir ./output
```

Render:

```bash
python workflow/run_workflow.py render \
  --input /path/to/1.mp4 \
  --input /path/to/2.mp4 \
  --plan ./plan.json \
  --montaj-root /path/to/montaj \
  --ffmpeg /path/to/ffmpeg \
  --ffprobe /path/to/ffprobe \
  --out-dir ./output
```

## Stop conditions

For basic production, stop after valid B/C outputs + `report.json`. Do not expand into advanced emotional-hook design, BGM strategy, publishing automation, or complex text removal unless explicitly requested.
