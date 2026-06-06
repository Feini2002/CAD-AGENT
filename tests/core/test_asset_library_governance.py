from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import temporary_artifact_dir


def _valid_visual_rack_plan() -> dict[str, object]:
    return {
        "schemaVersion": 2,
        "layoutMode": "classified_expandable_visual_warehouse_v2",
        "warehouseArchitecture": {
            "kind": "category_visual_warehouse",
            "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
            "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
            "expansionPolicy": "expand typed racks before adding new DWGs",
        },
        "acceptanceCriteria": {
            "slotContainment": "slot has owning rack and bbox-compatible zone",
            "assetOwnership": "occupied slots list assetIds or category/nativeDwg",
            "expansionCapacity": "each rack keeps empty or future slots",
            "copyPolicy": "only clean source slots can copy geometry",
            "screenshotBoundary": "screenshots are visual aids only",
        },
        "zoneBboxes": {
            "01_CLEAN_ASSETS": {"min": [0.0, 0.0], "max": [12000.0, 9000.0]},
            "B_OBJECT_ASSET_INDEX": {"min": [13200.0, 0.0], "max": [20000.0, 9000.0]},
            "02_PREVIEW_CARDS": {"min": [0.0, -2200.0], "max": [6000.0, -500.0]},
            "03_REVIEW_QUARANTINE": {"min": [6400.0, -2200.0], "max": [12400.0, -500.0]},
            "99_EVIDENCE_LINKS": {"min": [12800.0, -2200.0], "max": [20000.0, -500.0]},
        },
        "rackFamilies": [
            {
                "rackId": "A_BASE_SCAFFOLD",
                "zoneId": "01_CLEAN_ASSETS",
                "familyRole": "reusable_style_source",
                "copyPolicy": "clean_source_slots_only",
                "minExpansionSlots": 1,
                "slots": [
                    {
                        "slotId": "A02_LINETYPE_STANDARD",
                        "status": "occupied",
                        "assetIds": ["linetype_style_summary_table"],
                        "copySourceAllowed": True,
                    },
                    {
                        "slotId": "A06_LEADER_SYMBOL_STYLE",
                        "status": "empty_reserved",
                        "assetIds": [],
                        "copySourceAllowed": False,
                    },
                ],
            },
            {
                "rackId": "B_OBJECT_ASSET_INDEX",
                "zoneId": "B_OBJECT_ASSET_INDEX",
                "familyRole": "cross_category_object_index",
                "copyPolicy": "index_only_never_copy",
                "minExpansionSlots": 1,
                "slots": [
                    {
                        "slotId": "B01_BEDS",
                        "status": "index_only",
                        "category": "furniture.sleeping.beds",
                        "nativeDwg": "libraries/system_library/furniture/sleeping/beds/bed_assets.dwg",
                        "copySourceAllowed": False,
                        "copyPolicy": "never_copy",
                    },
                    {
                        "slotId": "B08_CUSTOM_EXPANSION",
                        "status": "future_expansion",
                        "category": "custom",
                        "nativeDwg": "libraries/system_library/custom/custom_assets.dwg",
                        "copySourceAllowed": False,
                        "copyPolicy": "never_copy",
                    },
                ],
            },
        ],
    }


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _write_minimal_governance_project(root: Path, *, package: dict[str, object]) -> None:
    manifest = {
        "orchestration": {
            "flow_variants": {
                "system_asset_sedimentation": [
                    "pipeline_asset_governor",
                    "pipeline_asset_librarian",
                    "pipeline_asset_dwg_curator",
                    "pipeline_asset_reuse_auditor",
                ]
            },
            "hard_gates": {"asset_governance": {"requires": []}},
        },
        "agents": [
            {"agent_id": "pipeline_asset_governor"},
            {"agent_id": "pipeline_asset_librarian"},
            {"agent_id": "pipeline_asset_dwg_curator"},
            {"agent_id": "pipeline_asset_reuse_auditor"},
        ],
    }
    _write_json(root / "agents/pipeline/pipeline_manifest.json", manifest)
    for agent_dir in ("asset_governor", "asset_librarian", "asset_dwg_curator", "asset_reuse_auditor"):
        _write_json(root / "agents/pipeline" / agent_dir / "agent.json", {"agent_id": f"pipeline_{agent_dir}"})
    protocol = "\n".join(
        [
            "00_INDEX",
            "01_CLEAN_ASSETS",
            "02_PREVIEW_CARDS",
            "03_REVIEW_QUARANTINE",
            "99_EVIDENCE_LINKS",
            "polishHardeningDecision",
            "",
        ]
    )
    protocol_path = root / "docs/architecture/system-asset-sedimentation-protocol.md"
    protocol_path.parent.mkdir(parents=True, exist_ok=True)
    protocol_path.write_text(protocol, encoding="utf-8")
    _write_json(root / "libraries/system_library/drawing_standards/basic/assets.json", package)

    shelf_report = {
        "status": "pass",
        "savedAssetDwg": True,
        "savedCurrentBusinessDwg": False,
        "rackPlan": _valid_visual_rack_plan(),
        "createdEntityReadback": {
            "status": "ok",
            "resolvedHandleCount": 1,
            "unresolvedHandleCount": 0,
            "unmanagedLayerCount": 0,
            "entityBboxes": [
                {
                    "handle": "A1",
                    "layer": "ASSET_LABEL",
                    "objectName": "AcDbLine",
                    "bbox": {"min": [0.0, 0.0], "max": [10.0, 10.0]},
                }
            ],
        },
        "protectedContentReadback": {
            "status": "ok",
            "clusters": [
                {
                    "clusterId": "A2_ANNOTATION_STYLES",
                    "entityCount": 2,
                    "bbox": {"min": [100.0, 100.0], "max": [500.0, 500.0]},
                    "layers": ["ASSET_PROOF_CONTENT"],
                    "layerCounts": {"ASSET_PROOF_CONTENT": 2},
                }
            ],
        },
        "visualClearanceAudit": {"status": "pass", "overlapCount": 0},
        "visualReadabilityAudit": {"status": "pass", "issueCount": 0, "issues": []},
    }
    _write_json(root / "output/validation_runs/system-assets/asset-library-shelves/shelf_layout_report.json", shelf_report)


class AssetLibraryGovernanceTests(unittest.TestCase):
    def test_visual_rack_audit_rejects_sample_only_protected_layer_report(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        report = audit_visual_rack_plan(
            visual_rack_plan=_valid_visual_rack_plan(),
            protected_content_report={
                "status": "ok",
                "clusters": [
                    {
                        "clusterId": "A2_ANNOTATION_STYLES",
                        "entityCount": 129,
                        "layerSamples": ["ASSET_PROOF_CONTENT"],
                    }
                ],
            },
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("protected content layer census missing; layerSamples is not enough", report["issues"])

    def test_visual_rack_audit_rejects_preview_layer_in_full_protected_layer_census(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        report = audit_visual_rack_plan(
            visual_rack_plan=_valid_visual_rack_plan(),
            protected_content_report={
                "status": "ok",
                "clusters": [
                    {
                        "clusterId": "A2_ANNOTATION_STYLES",
                        "entityCount": 129,
                        "layers": ["ASSET_PROOF_CONTENT", "CODEX_PREVIEW"],
                        "layerCounts": {"ASSET_PROOF_CONTENT": 128, "CODEX_PREVIEW": 1},
                    }
                ],
            },
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("protected asset proof content is still on CODEX_PREVIEW", report["issues"])
        self.assertEqual(report["metrics"]["protectedContentLayerCounts"]["CODEX_PREVIEW"], 1)

    def test_visual_rack_audit_uses_top_level_protected_layer_counts_without_double_counting(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        report = audit_visual_rack_plan(
            visual_rack_plan=_valid_visual_rack_plan(),
            protected_content_report={
                "status": "ok",
                "layerCounts": {"ASSET_PROOF_CONTENT": 349},
                "clusters": [
                    {"clusterId": "A1_LINE_STANDARDS", "layerCounts": {"ASSET_PROOF_CONTENT": 179}},
                    {"clusterId": "A2_ANNOTATION_STYLES", "layerCounts": {"ASSET_PROOF_CONTENT": 170}},
                ],
            },
        )

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["metrics"]["protectedContentLayerCounts"]["ASSET_PROOF_CONTENT"], 349)

    def test_governance_check_rejects_missing_referenced_evidence_files(self) -> None:
        from scripts.run_asset_library_governance_check import run_check

        with temporary_artifact_dir("asset_library_governance_missing_evidence") as root:
            package = {
                "nativeLayout": {"visualRackPlan": _valid_visual_rack_plan()},
                "assets": [
                    {
                        "assetId": "interior_dimension_style_visual_standard",
                        "evidenceRefs": ["output/previews/missing-proof.png"],
                        "nativeVisiblePanelEvidence": {
                            "status": "pass",
                            "summary": "output/validation_runs/missing-summary.json",
                            "focusedScreenshot": "output/previews/missing-focused.png",
                        },
                    }
                ],
            }
            _write_minimal_governance_project(root, package=package)

            report = run_check(project_root=root)

        self.assertEqual(report["status"], "fail")
        self.assertIn("referenced evidence file missing: output/previews/missing-proof.png", report["issues"])
        self.assertIn("referenced evidence file missing: output/validation_runs/missing-summary.json", report["issues"])
        self.assertIn("referenced evidence file missing: output/previews/missing-focused.png", report["issues"])

    def test_model_asset_governor_suggestion_cannot_override_rule_source_boundary(self) -> None:
        from core.assets.system_asset_library_governance import (
            build_asset_library_governance,
            build_asset_library_layout_plan,
        )

        export_manifest = {
            "assetKind": "object_block",
            "exportMode": "metadata_only",
            "sourceBoundary": {
                "mode": "whole_codex_preview",
                "precision": "unclear",
                "includedHandles": [],
            },
        }
        layout_plan = build_asset_library_layout_plan(
            asset_id="sofa_training_panel_candidate",
            index=0,
            asset_name="training panel candidate",
            category="furniture.seating.sofas",
            asset_kind="object_block",
            export_manifest=export_manifest,
        )

        governance = build_asset_library_governance(
            asset_id="sofa_training_panel_candidate",
            category="furniture.seating.sofas",
            asset_kind="object_block",
            export_manifest=export_manifest,
            anti_contamination={"checks": ["do not copy training panel to clean source"]},
            layout_plan=layout_plan,
            native_dwg_exists=False,
            lifecycle_status="candidate",
            model_review_report={
                "status": "pass",
                "assetLifecycleDecision": "candidate",
                "sourceBoundaryDecision": "created_handles_recommended_by_model_only",
                "cleanSourceAllowed": True,
                "quarantineReason": "",
                "requiredChildAgents": ["pipeline_asset_librarian", "pipeline_asset_dwg_curator"],
                "nativeVisibleEvidenceRequired": True,
                "reuseProofRequired": True,
                "classificationSuggestion": {
                    "assetKind": "object_block",
                    "category": "furniture.seating.sofas",
                    "confidence": "medium",
                },
                "sourceBoundaryRecommendation": {
                    "mode": "created_handles",
                    "precision": "precise",
                    "includedHandles": ["AA1"],
                },
                "cleanSourceRecommendation": {
                    "cleanSourceAllowed": True,
                    "reason": "model thinks visible sofa is reusable",
                },
                "repairPlanRecommendation": {
                    "mode": "local_repair_candidate",
                    "targetHandles": ["AA1"],
                },
                "blockingReasons": [],
                "evidenceRequired": ["created handle readback"],
                "decision": "model_advisory_only",
                "statePatch": {
                    "phase": "model_reviewed",
                    "phaseLabelForUser": "model advisory review",
                    "completedEvidence": ["model source-boundary suggestion"],
                    "pendingEvidence": ["rule source-boundary gate", "CAD readback"],
                    "pendingUserAction": "",
                    "blockedReason": "",
                    "nextSafeAction": "continue_rule_gate_checks",
                },
                "finalResponseAllowedClaims": ["model advisory fields are complete"],
                "evidenceUsed": ["synthetic model review"],
                "evidenceMissing": ["CAD handles/readback"],
                "assumptions": ["rule gates remain authoritative"],
                "alternativesConsidered": [],
                "nextRequiredEvidence": ["rule source-boundary gate"],
                "learningCandidate": {},
                "toolIntent": None,
            },
        )

        self.assertEqual(governance["decision"], "metadata_only_until_native_cad_export")
        self.assertFalse(governance["sourceBoundaryDecision"]["cleanSourceAllowed"])
        self.assertEqual(governance["modelAssistedDecision"]["status"], "pass")
        self.assertEqual(
            governance["modelAssistedDecision"]["cleanSourceRecommendation"]["cleanSourceAllowed"],
            True,
        )
        self.assertIn("model suggestions are advisory only", governance["requiredGuards"])


if __name__ == "__main__":
    unittest.main()
