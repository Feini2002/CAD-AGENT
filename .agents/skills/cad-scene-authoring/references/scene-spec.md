# SceneSpec Reference

Codex creates `scene_spec.json`; the repository does not generate it from a keyword router.

Required fields:

- `schema_version`: `scene-spec/v1`
- `run_id`: current run id
- `scene_id`: stable scene id
- `units`: `mm`
- `view`: `plan_2d`
- `objects`: semantic objects with `id`, `kind`, optional `dimensions`, and `placement`
- `target_layer`: always `CODEX_PREVIEW`

Gate 0 object kinds are `desk`, `monitor`, `keyboard`, `mouse`, and `vase`.

Use relative placements for desktop objects:

- monitor on desk rear anchor
- keyboard in front of monitor
- mouse left or right of keyboard
- vase on desk with clearance from keyboard and monitor

Unsupported objects should be omitted or explicitly blocked; do not add a fixed scene template or exact prompt route.
