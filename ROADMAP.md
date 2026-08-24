# Roadmap

## v1.0 — current simple workflow

- 1–2 MP4 inputs
- Codex full planner/executor path
- Doubao planner-only path
- B Result First + C Product Logic
- REPRODUCE / VARIATION
- Source Gate
- frozen Montaj + FFmpeg execution baseline

## Phase Next — Local Wrapper for Non-Codex Planners

Goal: make the Doubao experience approach the Codex experience:

`drop 1–2 videos -> planner interaction -> automatic B/C outputs`

The wrapper should orchestrate, without modifying the frozen core:

1. Accept 1–2 local videos + product brief.
2. Generate labeled representative frames automatically.
3. Prepare Candidate Shot List request.
4. Exchange planner input/output with Doubao when a supported integration/API is available.
5. Fall back to a guided manual copy/paste step when no direct API is available.
6. Validate final `plan.json` locally.
7. Call unchanged Montaj + portable FFmpeg 8.1.2.
8. Return `B_result_first.mp4`, `C_product_logic.mp4`, and `report.json`.

Constraints:
- do not modify `workflow/run_workflow.py` merely to implement the wrapper;
- do not modify Montaj;
- do not replace FFmpeg 8.1.2 without a separate validation phase;
- do not claim full automation when the selected Doubao product has no supported programmatic interface.

## Advanced project — intentionally separate

Future advanced editing should be a separate skill/project rather than expanding this basic one. Candidate topics:
- stronger emotional value in first 0–3 seconds
- Hook -> proof continuity
- dynamic shot duration
- Pain / WOW / Result / Satisfying / Comparison / Curiosity structures
- retention-data feedback loops
- advanced pacing and story structure
