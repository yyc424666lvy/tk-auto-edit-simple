# Templates

## product_brief.json

Fill in:
- `product_name`
- up to 3 `core_selling_points`

Keep `bgm` as `false` for this simple workflow.

## plan.json

Planner output contract.

Required rules:
- `source_gate` must be one of the four allowed Source Gate values.
- `crop_mode` must be `safe_crop` or `safe_scale`.
- B and C each use 5–8 clips.
- each clip is 0.8–3.0 seconds.
- each version totals 10–15 seconds.
- each version has <=4 copy items.
- each copy has <=6 English words.

Historical plans should be saved as `plans/001_plan.json`, `plans/002_plan.json`, etc. Do not overwrite old plans.
