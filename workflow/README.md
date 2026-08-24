# TK Product Video

Reusable local workflow for one or two product videos:

```text
Codex: source gate + representative-frame review + B/C plan
Montaj: exact multi-source cut/concat
portable FFmpeg 8.1.2: 9:16 crop/scale + simple English copy + silent H.264 encode
```

Montaj source code is not copied or modified by this workflow. Node/Puppeteer,
LLM APIs, music and subtitle systems are not required.

## Run

Analyze and cache one-second representative frames:

```bash
python3 run_workflow.py analyze \
  --input /path/to/1.mp4 \
  --input /path/to/2.mp4 \
  --out-dir ./tk-product-video-output
```

Render a Codex-produced plan:

```bash
MONTAJ_FFMPEG=/path/to/portable/ffmpeg \
MONTAJ_FFPROBE=/path/to/portable/ffprobe \
python3 run_workflow.py render \
  --input /path/to/1.mp4 \
  --input /path/to/2.mp4 \
  --plan plan.json \
  --montaj-root /path/to/montaj \
  --out-dir ./tk-product-video-output
```

`run` combines the cache-aware analysis and render steps. Re-running with the
same source file size and mtime reuses `analysis_cache.json`.

## Plan contract

The plan must contain:

- `source_gate`: `CLEAN_SOURCE`, `CROPPABLE_TEXT`, `MASKABLE_TEXT`, or `SOURCE_TEXT_LIMITATION`.
- `crop_mode`: `safe_crop` or `safe_scale`.
- `versions.B_result_first.timeline`: 5–8 segments.
- `versions.C_product_logic.timeline`: 5–8 segments.
- Each timeline total: 10–15 seconds; each segment: 0.8–3.0 seconds.
- Each version has at most four copy items, with no more than six words per screen.

The render report is written to `report.json` and contains:
`SOURCE_GATE`, `SOURCE_SUMMARY`, `B_TIMELINE`, `C_TIMELINE`, `COPY`, `OUTPUT`,
`RUNTIME`, and `LIMITATION`.

## Source gate policy

`SOURCE_TEXT_LIMITATION` is a reportable risk, not a repair task. The workflow
does not run OCR, inpainting, subject tracking, external APIs, or complex
text-removal logic. Simple opaque top/bottom copy bands are supported when the
Codex plan marks the text as maskable.
