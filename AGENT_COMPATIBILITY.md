# Planner / Agent Compatibility

The render layer is planner-agnostic.

## Full integration

A tool can run the whole flow if it has:
- local file access
- image/vision support
- JSON planning ability
- shell/process execution

Codex commonly fits this pattern.

## Planner-only integration

A model can replace Codex's planning role if it can inspect labeled representative frames and return strict JSON. It does not need shell access.

Doubao can be used this way when the specific client/session supports image input and reliable structured JSON.

Verified Doubao protocol:

`labeled contact sheets -> Candidate Shot List -> locked candidate pool -> plan.json -> local render`

The Candidate Shot List is mandatory in the documented Doubao path because it grounds the model to real source timecodes before JSON generation.

## Other planners

Claude, Gemini, another multimodal model, or a human can also be compatible if they respect the same planner contract and `templates/plan.json`.

## Reproducibility

Different planners are not expected to produce identical `VARIATION` plans. Exact reproduction requires the same source files and the same accepted `plan.json` under `REPRODUCE`.
