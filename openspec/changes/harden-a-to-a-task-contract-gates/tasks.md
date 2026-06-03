## 1. Contract And Dispatch

- [x] 1.1 Add A-to-A TaskContract builder for asset sedimentation, asset DWG layout, and visual layout review semantics
- [x] 1.2 Integrate the contract into `orchestrate_request()` reports
- [x] 1.3 Block `workflow_dispatch` with `a-to-a hard gate` when required Agent outputs are missing or hard gates fail

## 2. Agent Manifest

- [x] 2.1 Add `pipeline_visual_layout_reviewer` Agent definition
- [x] 2.2 Register the Agent in the global pipeline manifest
- [x] 2.3 Add `asset_dwg_layout`, `visual_layout_review`, `asset_dwg_curation`, and `asset_reuse_audit` manifest gates / flow metadata

## 3. Tests And Governance

- [x] 3.1 Add focused unit tests for contract detection, missing Agent blocking, sedimentation Agent dispatch, and pass-output readiness
- [x] 3.2 Add `scripts/run_a_to_a_orchestration_gate_check.py`
- [x] 3.3 Run focused unit tests, workflow dispatch regression, governance check, OpenSpec validation, and diff hygiene

## 4. Records

- [x] 4.1 Update architecture docs and global rules
- [x] 4.2 Update short context, current status, changelog, and issues
- [x] 4.3 Record final verification evidence after checks pass
