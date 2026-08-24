# Codex Planner Prompt

Use the frozen `tk-auto-edit-simple` workflow.

Do not modify Montaj, do not replace portable FFmpeg 8.1.2, and do not modify `workflow/run_workflow.py` for normal use.

Inputs:
- 1–2 MP4 files
- `product_brief.json`
- analysis contact sheets / source metadata
- up to 3 most recent plans when VARIATION history exists

Task:
1. Assign Source Gate.
2. Build `B_result_first` and `C_product_logic`.
3. Each version: 5–8 clips, 10–15s total, each clip 0.8–3.0s.
4. Prefer strong action / result / demo over static presentation.
5. Avoid title cards, blank transitions, repeated near-identical shots, unsupported claims, and unsafe crops.
6. Copy: max 4 items/version, <=6 English words each, truthful to visible footage.
7. Default mode `VARIATION`. Prefer changing Hook first; target overlap <=0.70 when quality permits.
8. `REPRODUCE` must use the requested existing plan exactly; if missing, return `REPRODUCE_PLAN_MISSING`.
9. Write valid UTF-8 `plan.json`.
10. Render through the frozen workflow and verify with ffprobe when shell access is available.

Return a short status, plan path, B/C output paths, runtime, and limitation.
