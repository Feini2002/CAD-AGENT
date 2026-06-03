## 1. Agent Governance Contract

- [x] 1.1 Register asset governor and child governance agents in the global pipeline manifest
- [x] 1.2 Add agent definitions for asset governor, librarian, DWG curator, and reuse auditor
- [x] 1.3 Update CAD Designer and pipeline docs so explicit asset sedimentation routes through the governor

## 2. Core Governance And Layout

- [x] 2.1 Add a Core asset library layout helper that produces layoutPlan v2 with zones, slot, bbox, cleanup policy, preview card, evidence links, and hardening decision
- [x] 2.2 Integrate layoutPlan v2 and library governance metadata into system asset sedimentation contracts and registry entries
- [x] 2.3 Export new helpers from `core.assets`

## 3. CLI And Self-Checks

- [x] 3.1 Extend `scripts/sediment_system_asset.py` to expose asset-governance decisions in JSON output
- [x] 3.2 Add tests for layoutPlan v2, quarantine/metadata-only behavior, agent manifest registration, and CLI governance output
- [x] 3.3 Run OpenSpec validation and focused test suites for asset governance

## 4. Records And Completion Gate

- [x] 4.1 Update system asset protocol, system library README, global pipeline docs, and training docs with the governance model
- [x] 4.2 Update status, changelog, issues if needed, and handoff records for this package
- [x] 4.3 Record final polish-hardening decision and evidence boundary for not-run native CAD relayout

## 5. Visual Warehouse Acceptance Correction

- [x] 5.1 Add a Core `visualRackPlan` audit that rejects label-only warehouse metadata and checks v2 architecture, acceptance criteria, rack ownership, copy policy, expansion slots, and zone bbox ratios
- [x] 5.2 Require `refresh_system_asset_layout_metadata()` to reject weak visual rack plans before writing `assets.json` or registry
- [x] 5.3 Upgrade `scripts/layout_system_asset_shelves.py` to emit `classified_expandable_visual_warehouse_v2`, run pre-write plan audit, write the system asset DWG, and include created-handle entity readback by layer / bbox
- [x] 5.4 Extend `scripts/run_asset_library_governance_check.py` so completion depends on the current system library `nativeLayout.visualRackPlan` audit, not only agent registration and protocol text
- [x] 5.5 Run focused tests, real system asset DWG layout, asset package verify, governance check, and AutoCAD screenshot capture

## 6. Shelf / Content Clearance Correction

- [x] 6.1 Add regression tests that reject shelf entities overlapping existing asset content and catch A2 content being cut by union-bbox column splitting
- [x] 6.2 Upgrade system asset shelf layout to cluster non-shelf protected content bboxes and place shelf frames / labels outside those bboxes
- [x] 6.3 Record full created shelf `entityBboxes`, protected content clusters, and `visualClearanceAudit` in the real CAD shelf layout report
- [x] 6.4 Extend `audit_visual_rack_plan()` and `run_asset_library_governance_check.py` so visual warehouse completion requires latest CAD readback plus zero shelf/content overlaps
- [x] 6.5 Re-run focused tests, real system asset DWG relayout, asset package verify, governance check, AutoCAD screenshot capture, OpenSpec validation, and training workbench sync

## 7. Visual Warehouse Readability Hard Gate

- [x] 7.1 Add regression tests that reject visually cramped warehouse layouts even when bbox overlap count is zero
- [x] 7.2 Extend Core visual rack audit and governance checks with readability metrics: aisle clearance, content density, source/proof role separation, layer semantics, and non-screenshot evidence
- [x] 7.3 Upgrade A-to-A `visual_layout_review` so the visual reviewer must report the readability fields before delivery can become ready
- [x] 7.4 Update the visual layout reviewer prompt contract, common Prompt contract, and prompt generation / agent-check sources with the same warehouse acceptance rule
- [x] 7.5 Re-layout the system asset DWG with widened aisles, proof-panel boundaries separated from source definitions, reflowed content if needed, and rerun focused tests plus real CAD evidence
