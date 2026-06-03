## Overview

The orchestration layer now builds an `a_to_a_task_contract` before allowing high-risk task dispatch. The contract is intentionally small and deterministic: it maps request semantics to required pipeline agents and machine hard gates, then evaluates whether those agents have supplied passing outputs.

## Contract Shape

The contract includes:

- `taskKind`: `ordinary_orchestration`, `system_asset_sedimentation`, `asset_dwg_layout`, or `visual_layout_review`
- `triggeredSemantics`: semantic tags found in the request and semantic asset route
- `requiredAgents`: pipeline agents that must output decisions for this task
- `hardGates`: machine gate names tied to those agents
- `missingRequiredAgents`: required agents with no output
- `failedHardGates`: present agent outputs that did not pass
- `blockingReasons`: user / audit friendly reasons for dispatch blocking
- `deliveryBoundary`: whether a complete claim is allowed

## Routing Rules

- System asset sedimentation requires:
  - `pipeline_asset_governor`
  - `pipeline_asset_librarian`
  - `pipeline_asset_dwg_curator`
  - `pipeline_asset_reuse_auditor`
- System asset DWG warehouse / rack / shelf / aisle / expandable layout requests require all asset agents plus `pipeline_visual_layout_reviewer`.
- Visual layout requests without asset semantics still require `pipeline_visual_layout_reviewer`.
- Ordinary requests are not blocked by this contract.

## Visual Layout Reviewer

`pipeline_visual_layout_reviewer` is a non-CAD-writing reviewer. It compares user metaphor, layout plan, screenshot / preview, created handles, readback summary, and registry context. It must not approve a layout merely because a screenshot is nonblank or CAD objects exist.

Its pass output requires:

- `layoutMatchesMetaphor=pass`
- `primaryShelvesClear=pass`
- `futureExpansionClear=pass`
- `retrievalPathReadable=pass`
- `visualNoiseAcceptable=pass`

## Integration

`orchestrate_request()` writes `a_to_a_task_contract` into every report. If the contract is blocked, `workflow_dispatch.status=blocked` and `workflow_dispatch.reason` contains `a-to-a hard gate`.

## Evidence Boundary

This change proves orchestration gating and Agent registration. It does not prove a specific DWG layout is visually accepted unless a real `visual_layout_review` output is present for that task. It does not save DWG files or claim CAD geometry correctness.
