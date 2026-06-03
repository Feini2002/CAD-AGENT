## 1. Contract and Tests

- [x] 1.1 Add OpenSpec proposal, design, specs, and implementation tasks for screenshot orchestration
- [x] 1.2 Add failing tests for screenshot decision routing in `tests/core/test_render_preview.py`
- [x] 1.3 Add failing tests for runner payload consistency in `tests/core/test_table_c_evidence_gate.py` and `tests/core/test_cad_foundation_remaining_training.py`
- [x] 1.4 Add failing tests for shared Agent contract and workbench Agent check

## 2. Core Screenshot Orchestration

- [x] 2.1 Implement a structured screenshot decision helper in `core/verification/render_preview.py`
- [x] 2.2 Ensure `prepare_autocad_for_capture()` and `visual_preview_payload()` expose consistent `screenshotDecision` data
- [x] 2.3 Preserve task-scoped focus priority and prevent target-unavailable fallback to whole drawing

## 3. Runner and Agent Understanding

- [x] 3.1 Update `visual_cad_review` to report screenshot decision payload
- [x] 3.2 Update focused foundation training preview capture to report screenshot decision payload
- [x] 3.3 Update `agents/COMMON_PROMPT_CONTRACT.md` with screenshot orchestration rules
- [x] 3.4 Update `scripts/run_training_workbench_agent_check.py` so Agent checks verify screenshot capability understanding

## 4. Verification and Records

- [x] 4.1 Run focused tests for render preview, visual review, foundation training, and workbench Agent check
- [x] 4.2 Run `openspec.cmd validate --all --strict --json --no-interactive`
- [x] 4.3 Run `scripts/render_preview.py --check` and a representative real AutoCAD task-scoped capture when AutoCAD is available
- [x] 4.4 Update `docs/status/current.md`, `docs/status/changelog.md`, `docs/status/issues.md`, and complete this task list
