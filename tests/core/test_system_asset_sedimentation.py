from __future__ import annotations

import json
import subprocess
import sys
import unittest

from tests.bootstrap import PROJECT_ROOT
from tests.helpers import temporary_artifact_dir


class SystemAssetSedimentationTests(unittest.TestCase):
    def test_category_resolution_reserves_stable_sofa_package(self) -> None:
        from core.assets.system_asset_sedimentation import resolve_system_asset_location

        location = resolve_system_asset_location("furniture.seating.sofas")

        self.assertEqual(location.category_path, "furniture/seating/sofas")
        self.assertEqual(location.package_path, "libraries/system_library/furniture/seating/sofas")
        self.assertEqual(location.contract_path, "libraries/system_library/furniture/seating/sofas/assets.json")
        self.assertEqual(location.native_dwg_path, "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg")

    def test_repeated_sofa_sedimentation_updates_same_package_and_registry(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_sedimentation") as root:
            first = sediment_system_asset(
                project_root=root,
                asset_id="sofa_a_2seat_top_view",
                name="沙发 A 双人平面",
                category="furniture.seating.sofas",
                aliases=["双人沙发", "sofa A"],
                use_when=["用户要求双人沙发平面图"],
                tags=["plan", "seating"],
                dimensions={"width_mm": 1860, "depth_mm": 920},
                block_name="SOFA_A_2SEAT_TOP_VIEW",
                evidence_refs=["output/previews/sofa_a.png"],
                source={"type": "active_dwg_handles", "handles": ["A1", "A2"]},
            )
            second = sediment_system_asset(
                project_root=root,
                asset_id="sofa_b_3seat_top_view",
                name="沙发 B 三人平面",
                category="furniture.seating.sofas",
                aliases=["三人沙发", "sofa B"],
                use_when=["用户要求三人沙发平面图", "客厅沙发布置"],
                tags=["plan", "seating"],
                dimensions={"width_mm": 2800, "depth_mm": 960},
                block_name="SOFA_B_3SEAT_TOP_VIEW",
                evidence_refs=["output/previews/sofa_b.png"],
                source={"type": "active_dwg_handles", "handles": ["B1"]},
            )

            self.assertEqual(first["packagePath"], second["packagePath"])
            self.assertEqual(second["nativeDwg"], "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg")
            self.assertFalse(second["nativeDwgExists"])

            package = json.loads((root / "libraries/system_library/furniture/seating/sofas/assets.json").read_text(encoding="utf-8"))
            self.assertEqual([asset["assetId"] for asset in package["assets"]], ["sofa_a_2seat_top_view", "sofa_b_3seat_top_view"])
            self.assertEqual(package["assets"][1]["native"]["blockName"], "SOFA_B_3SEAT_TOP_VIEW")
            self.assertEqual(package["tools"]["apply"], "scripts/sediment_system_asset.py")

            registry = json.loads((root / "libraries/system_library/registry.json").read_text(encoding="utf-8"))
            self.assertEqual(registry["schemaVersion"], 1)
            self.assertIn("furniture.seating.sofas", [package["category"] for package in registry["packages"]])
            self.assertEqual(
                [asset["assetId"] for asset in registry["assets"]],
                ["sofa_a_2seat_top_view", "sofa_b_3seat_top_view"],
            )
            self.assertEqual(registry["assets"][1]["contractPath"], "libraries/system_library/furniture/seating/sofas/assets.json")

    def test_sedimentation_is_idempotent_for_same_asset_id(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_sedimentation_idempotent") as root:
            sediment_system_asset(
                project_root=root,
                asset_id="sofa_a_2seat_top_view",
                name="沙发 A 初版",
                category="furniture.seating.sofas",
                aliases=["双人沙发"],
                use_when=["初版"],
            )
            sediment_system_asset(
                project_root=root,
                asset_id="sofa_a_2seat_top_view",
                name="沙发 A 复核版",
                category="furniture.seating.sofas",
                aliases=["双人沙发", "客厅双人位"],
                use_when=["复核后使用"],
            )

            package = json.loads((root / "libraries/system_library/furniture/seating/sofas/assets.json").read_text(encoding="utf-8"))
            registry = json.loads((root / "libraries/system_library/registry.json").read_text(encoding="utf-8"))

            self.assertEqual(len(package["assets"]), 1)
            self.assertEqual(package["assets"][0]["name"], "沙发 A 复核版")
            self.assertEqual(package["assets"][0]["aliases"], ["双人沙发", "客厅双人位"])
            self.assertEqual(len(registry["assets"]), 1)

    def test_hardened_contract_records_lifecycle_retrieval_layout_and_feedback(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_sedimentation_hardened") as root:
            report = sediment_system_asset(
                project_root=root,
                asset_id="sofa_c_lounge_top_view",
                name="沙发 C 贵妃位平面",
                category="furniture.seating.sofas",
                aliases=["贵妃沙发", "lounge sofa"],
                use_when=["客厅需要贵妃位沙发", "用户要求 L 型沙发平面"],
                tags=["plan", "seating"],
                scenario_tags=["residential", "living_room"],
                constraints=["仅用于平面布置", "插入前需确认朝向"],
                dimensions={"width_mm": 3200, "depth_mm": 1650},
                block_name="SOFA_C_LOUNGE_TOP_VIEW",
                evidence_refs=["output/previews/sofa_c.png"],
                source={"type": "active_dwg_handles", "handles": ["C1", "C2"]},
                feedback_refs=["projects/demo/feedback.md#sofa-c"],
                promotion_refs=["agents/cad_designer/prompt_addendum.md"],
                failure_reason="上一轮 L 型沙发方向容易放反",
                generated_at="2026-06-02T10:00:00+00:00",
            )

            self.assertEqual(report["assetStatus"], "candidate")
            self.assertEqual(report["verification"]["status"], "metadata_only")
            package = json.loads((root / "libraries/system_library/furniture/seating/sofas/assets.json").read_text(encoding="utf-8"))
            asset = package["assets"][0]

            self.assertEqual(asset["lifecycle"]["status"], "candidate")
            self.assertEqual(asset["lifecycle"]["allowedStatuses"], ["candidate", "systemized", "verified", "deprecated"])
            self.assertEqual(asset["retrieval"]["aliases"], ["贵妃沙发", "lounge sofa"])
            self.assertEqual(asset["retrieval"]["scenarioTags"], ["residential", "living_room"])
            self.assertIn("width_mm:3200", asset["retrieval"]["matchText"])
            self.assertEqual(asset["native"]["layoutPlan"]["slotKey"], "sofa_c_lounge_top_view")
            self.assertEqual(asset["native"]["layoutPlan"]["schemaVersion"], 2)
            self.assertEqual(asset["native"]["layoutPlan"]["policy"], "governed_category_library_zones")
            self.assertIn("01_CLEAN_ASSETS", [zone["zoneId"] for zone in asset["native"]["layoutPlan"]["zones"]])
            self.assertEqual(asset["native"]["layoutPlan"]["cleanSource"]["zoneId"], "01_CLEAN_ASSETS")
            self.assertTrue(asset["native"]["layoutPlan"]["cleanSource"]["copySourceAllowed"])
            self.assertIn("training_notes", asset["native"]["layoutPlan"]["cleanupPolicy"]["excludedContentTypes"])
            self.assertEqual(asset["native"]["layoutPlan"]["grid"]["column"], 0)
            self.assertEqual(asset["native"]["layoutPlan"]["grid"]["row"], 0)
            self.assertEqual(asset["libraryGovernance"]["governorAgentId"], "pipeline_asset_governor")
            self.assertEqual(asset["libraryGovernance"]["decision"], "ready_for_clean_source_layout")
            self.assertIn("pipeline_asset_dwg_curator", asset["libraryGovernance"]["managedChildAgents"])
            self.assertIn("needs_native_cad_relayout", asset["libraryGovernance"]["polishHardeningDecision"]["categories"])
            self.assertEqual(asset["verification"]["status"], "metadata_only")
            self.assertIn("native DWG geometry reuse", asset["verification"]["notChecked"])
            self.assertEqual(asset["feedbackLoop"]["failureReason"], "上一轮 L 型沙发方向容易放反")
            self.assertEqual(asset["feedbackLoop"]["feedbackRefs"], ["projects/demo/feedback.md#sofa-c"])

            registry = json.loads((root / "libraries/system_library/registry.json").read_text(encoding="utf-8"))
            self.assertEqual(registry["assets"][0]["lifecycleStatus"], "candidate")
            self.assertEqual(registry["assets"][0]["retrieval"]["scenarioTags"], ["residential", "living_room"])
            self.assertEqual(registry["assets"][0]["verificationStatus"], "metadata_only")
            self.assertEqual(registry["assets"][0]["libraryGovernance"]["governorAgentId"], "pipeline_asset_governor")
            self.assertEqual(registry["assets"][0]["nativeLayoutPlan"]["schemaVersion"], 2)

    def test_refresh_layout_metadata_upgrades_legacy_package_and_registry(self) -> None:
        from core.assets.system_asset_sedimentation import (
            refresh_system_asset_layout_metadata,
            sediment_system_asset,
            verify_system_asset_package,
        )

        with temporary_artifact_dir("system_asset_layout_metadata_refresh") as root:
            sediment_system_asset(
                project_root=root,
                asset_id="legacy_style_asset",
                name="Legacy style asset",
                category="drawing_standards.basic",
                asset_kind="style_standard",
                export_mode="style_export",
                source_boundary_mode="style_definition",
                generated_at="2026-06-03T01:00:00+00:00",
            )
            package_path = root / "libraries/system_library/drawing_standards/basic/assets.json"
            registry_path = root / "libraries/system_library/registry.json"
            package = json.loads(package_path.read_text(encoding="utf-8"))
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            package["assets"][0].pop("libraryGovernance", None)
            package["assets"][0]["native"]["layoutPlan"] = {"policy": "append_to_category_library_grid"}
            registry["assets"][0].pop("libraryGovernance", None)
            registry["assets"][0]["nativeLayoutPlan"] = {"policy": "append_to_category_library_grid"}
            package_path.write_text(json.dumps(package, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

            report = refresh_system_asset_layout_metadata(
                project_root=root,
                category="drawing_standards.basic",
                native_layout_write_status="asset_library_shelf_scaffold_written_to_standard_assets_dwg",
                visual_rack_plan={
                    "schemaVersion": 2,
                    "layoutMode": "classified_expandable_visual_warehouse_v2",
                    "warehouseArchitecture": {
                        "kind": "category_visual_warehouse",
                        "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
                        "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
                        "expansionPolicy": "large typed racks grow by slot families before adding new DWGs",
                    },
                    "acceptanceCriteria": {
                        "slotContainment": "each asset slot has an owning rack and bbox-compatible zone",
                        "assetOwnership": "each occupied slot lists assetIds or category/nativeDwg",
                        "expansionCapacity": "each rack family declares empty or future slots",
                        "copyPolicy": "only clean source slots can copy geometry",
                        "screenshotBoundary": "screenshot is visual aid only; handles and readback remain authoritative",
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
                                    "assetIds": ["legacy_style_asset"],
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
                },
                generated_at="2026-06-03T02:00:00+00:00",
            )

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["updatedAssetIds"], ["legacy_style_asset"])
            self.assertEqual(report["nativeLayoutWrite"], "asset_library_shelf_scaffold_written_to_standard_assets_dwg")
            package = json.loads(package_path.read_text(encoding="utf-8"))
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            asset = package["assets"][0]
            self.assertEqual(package["nativeLayout"]["nativeWrite"], "asset_library_shelf_scaffold_written_to_standard_assets_dwg")
            self.assertEqual(package["nativeLayout"]["visualRackPlan"]["layoutMode"], "classified_expandable_visual_warehouse_v2")
            self.assertEqual(package["nativeLayout"]["visualRackPlan"]["rackFamilies"][0]["rackId"], "A_BASE_SCAFFOLD")
            self.assertEqual(report["visualRackPlan"]["rackFamilies"][1]["rackId"], "B_OBJECT_ASSET_INDEX")
            self.assertEqual(report["visualRackAudit"]["status"], "pass")
            self.assertEqual(asset["native"]["layoutPlan"]["schemaVersion"], 2)
            self.assertEqual(asset["native"]["layoutPlan"]["policy"], "governed_category_library_zones")
            self.assertEqual(asset["libraryGovernance"]["governorAgentId"], "pipeline_asset_governor")
            self.assertEqual(registry["assets"][0]["nativeLayoutPlan"]["schemaVersion"], 2)
            self.assertEqual(registry["assets"][0]["libraryGovernance"]["governorAgentId"], "pipeline_asset_governor")
            verify = verify_system_asset_package(project_root=root, category="drawing_standards.basic")
            self.assertEqual(verify["status"], "pass", verify["issues"])

    def test_refresh_layout_metadata_rejects_visual_rack_plan_without_warehouse_audit(self) -> None:
        from core.assets.system_asset_sedimentation import refresh_system_asset_layout_metadata, sediment_system_asset

        with temporary_artifact_dir("system_asset_layout_metadata_rejects_weak_rack") as root:
            sediment_system_asset(
                project_root=root,
                asset_id="legacy_style_asset",
                name="Legacy style asset",
                category="drawing_standards.basic",
                asset_kind="style_standard",
                export_mode="style_export",
                source_boundary_mode="style_definition",
            )

            report = refresh_system_asset_layout_metadata(
                project_root=root,
                category="drawing_standards.basic",
                visual_rack_plan={
                    "schemaVersion": 1,
                    "layoutMode": "r4_three_column_warehouse_with_object_index",
                    "rackFamilies": [{"rackId": "A_BASE_SCAFFOLD", "slots": [{"slotId": "A02_LINETYPE"}]}],
                },
            )

            self.assertEqual(report["status"], "fail")
            self.assertIn("visualRackPlan schemaVersion must be >= 2", report["issues"])
            self.assertFalse(report["wroteContract"])
            self.assertFalse(report["wroteRegistry"])

    def test_visual_rack_plan_audit_rejects_label_only_warehouse_metadata(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        report = audit_visual_rack_plan(
            visual_rack_plan={
                "schemaVersion": 1,
                "layoutMode": "r4_three_column_warehouse_with_object_index",
                "rackFamilies": [
                    {"rackId": "A_BASE_SCAFFOLD", "slots": [{"slotId": "A02_LINETYPE"}]},
                    {"rackId": "B_OBJECT_ASSET_INDEX", "slots": [{"slotId": "B01_BEDS"}]},
                ],
            },
            zones={
                "01_CLEAN_ASSETS": {"min": [0.0, 0.0], "max": [4000.0, 3000.0]},
                "02_PREVIEW_CARDS": {"min": [0.0, -2400.0], "max": [6000.0, -200.0]},
                "03_REVIEW_QUARANTINE": {"min": [0.0, -5200.0], "max": [6000.0, -3000.0]},
                "99_EVIDENCE_LINKS": {"min": [0.0, -8000.0], "max": [6000.0, -5800.0]},
            },
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("visualRackPlan schemaVersion must be >= 2", report["issues"])
        self.assertIn("visualRackPlan missing warehouseArchitecture", report["issues"])
        self.assertIn("visualRackPlan missing acceptanceCriteria", report["issues"])

    def test_visual_rack_plan_audit_accepts_expandable_visual_warehouse(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        plan = {
            "schemaVersion": 2,
            "layoutMode": "classified_expandable_visual_warehouse_v2",
            "warehouseArchitecture": {
                "kind": "category_visual_warehouse",
                "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
                "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
                "expansionPolicy": "large typed racks grow by slot families before adding new DWGs",
            },
            "acceptanceCriteria": {
                "slotContainment": "each asset slot has an owning rack and bbox-compatible zone",
                "assetOwnership": "each occupied slot lists assetIds or category/nativeDwg",
                "expansionCapacity": "each rack family declares empty or future slots",
                "copyPolicy": "only clean source slots can copy geometry",
                "screenshotBoundary": "screenshot is visual aid only; created handles and readback remain authoritative",
            },
            "rackFamilies": [
                {
                    "rackId": "A_BASE_SCAFFOLD",
                    "zoneId": "01_CLEAN_ASSETS",
                    "familyRole": "reusable_style_source",
                    "copyPolicy": "clean_source_slots_only",
                    "minExpansionSlots": 2,
                    "slots": [
                        {
                            "slotId": "A02_LINETYPE_STANDARD",
                            "title": "线型标准",
                            "status": "occupied",
                            "assetIds": ["linetype_style_summary_table"],
                            "copySourceAllowed": True,
                            "sourceKind": "style_definition",
                        },
                        {
                            "slotId": "A06_LEADER_SYMBOL_STYLE",
                            "title": "引线 / 符号样式",
                            "status": "empty_reserved",
                            "assetIds": [],
                            "copySourceAllowed": False,
                            "sourceKind": "style_definition",
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
                            "title": "床铺",
                            "status": "index_only",
                            "category": "furniture.sleeping.beds",
                            "nativeDwg": "libraries/system_library/furniture/sleeping/beds/bed_assets.dwg",
                            "copySourceAllowed": False,
                            "copyPolicy": "never_copy",
                        },
                        {
                            "slotId": "B08_CUSTOM_EXPANSION",
                            "title": "自定义扩展",
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

        report = audit_visual_rack_plan(
            visual_rack_plan=plan,
            zones={
                "01_CLEAN_ASSETS": {"min": [0.0, 0.0], "max": [12000.0, 9000.0]},
                "B_OBJECT_ASSET_INDEX": {"min": [13200.0, 0.0], "max": [20000.0, 9000.0]},
                "02_PREVIEW_CARDS": {"min": [0.0, -2200.0], "max": [6000.0, -500.0]},
                "03_REVIEW_QUARANTINE": {"min": [6400.0, -2200.0], "max": [12400.0, -500.0]},
                "99_EVIDENCE_LINKS": {"min": [12800.0, -2200.0], "max": [20000.0, -500.0]},
            },
        )

        self.assertEqual(report["status"], "pass", report["issues"])
        self.assertIn("visual warehouse architecture", report["checked"])
        self.assertIn("object index rack is never-copy", report["checked"])
        self.assertGreaterEqual(report["metrics"]["primaryWarehouseAreaRatio"], 0.7)

    def test_visual_rack_plan_audit_rejects_failed_created_entity_readback(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        plan = {
            "schemaVersion": 2,
            "layoutMode": "classified_expandable_visual_warehouse_v2",
            "warehouseArchitecture": {
                "kind": "category_visual_warehouse",
                "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
                "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
                "expansionPolicy": "large typed racks grow by slot families before adding new DWGs",
            },
            "acceptanceCriteria": {
                "slotContainment": "each asset slot has an owning rack and bbox-compatible zone",
                "assetOwnership": "each occupied slot lists assetIds or category/nativeDwg",
                "expansionCapacity": "each rack family declares empty or future slots",
                "copyPolicy": "only clean source slots can copy geometry",
                "screenshotBoundary": "screenshot is visual aid only; handles and readback remain authoritative",
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
                        }
                    ],
                },
            ],
        }

        report = audit_visual_rack_plan(
            visual_rack_plan=plan,
            zones={
                "01_CLEAN_ASSETS": {"min": [0.0, 0.0], "max": [12000.0, 9000.0]},
                "B_OBJECT_ASSET_INDEX": {"min": [13200.0, 0.0], "max": [20000.0, 9000.0]},
                "02_PREVIEW_CARDS": {"min": [0.0, -2200.0], "max": [6000.0, -500.0]},
                "03_REVIEW_QUARANTINE": {"min": [6400.0, -2200.0], "max": [12400.0, -500.0]},
                "99_EVIDENCE_LINKS": {"min": [12800.0, -2200.0], "max": [20000.0, -500.0]},
            },
            entity_readback={"status": "fail", "unresolvedHandles": ["BAD1"]},
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("created shelf entity readback failed", report["issues"])

    def test_visual_rack_plan_audit_rejects_failed_clearance_report(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        plan = {
            "schemaVersion": 2,
            "layoutMode": "classified_expandable_visual_warehouse_v2",
            "warehouseArchitecture": {
                "kind": "category_visual_warehouse",
                "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
                "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
                "expansionPolicy": "large typed racks grow by slot families before adding new DWGs",
            },
            "acceptanceCriteria": {
                "slotContainment": "each asset slot has an owning rack and bbox-compatible zone",
                "assetOwnership": "each occupied slot lists assetIds or category/nativeDwg",
                "expansionCapacity": "each rack family declares empty or future slots",
                "copyPolicy": "only clean source slots can copy geometry",
                "screenshotBoundary": "screenshot is visual aid only; handles and readback remain authoritative",
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
                        }
                    ],
                },
            ],
        }

        report = audit_visual_rack_plan(
            visual_rack_plan=plan,
            zones={
                "01_CLEAN_ASSETS": {"min": [0.0, 0.0], "max": [12000.0, 9000.0]},
                "B_OBJECT_ASSET_INDEX": {"min": [13200.0, 0.0], "max": [20000.0, 9000.0]},
                "02_PREVIEW_CARDS": {"min": [0.0, -2200.0], "max": [6000.0, -500.0]},
                "03_REVIEW_QUARANTINE": {"min": [6400.0, -2200.0], "max": [12400.0, -500.0]},
                "99_EVIDENCE_LINKS": {"min": [12800.0, -2200.0], "max": [20000.0, -500.0]},
            },
            clearance_report={"status": "fail", "overlapCount": 2},
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("visual shelf clearance audit failed", report["issues"])

    def test_visual_rack_plan_audit_rejects_failed_readability_report(self) -> None:
        from core.assets.system_asset_library_governance import audit_visual_rack_plan

        plan = {
            "schemaVersion": 2,
            "layoutMode": "classified_expandable_visual_warehouse_v2",
            "warehouseArchitecture": {
                "kind": "category_visual_warehouse",
                "primaryWarehouseZones": ["01_CLEAN_ASSETS", "B_OBJECT_ASSET_INDEX"],
                "reviewOnlyZones": ["02_PREVIEW_CARDS", "03_REVIEW_QUARANTINE", "99_EVIDENCE_LINKS"],
                "expansionPolicy": "large typed racks grow by slot families before adding new DWGs",
            },
            "acceptanceCriteria": {
                "slotContainment": "each asset slot has an owning rack and bbox-compatible zone",
                "assetOwnership": "each occupied slot lists assetIds or category/nativeDwg",
                "expansionCapacity": "each rack family declares empty or future slots",
                "copyPolicy": "only clean source slots can copy geometry",
                "screenshotBoundary": "screenshot is visual aid only; handles and readback remain authoritative",
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
                        }
                    ],
                },
            ],
        }

        report = audit_visual_rack_plan(
            visual_rack_plan=plan,
            zones={
                "01_CLEAN_ASSETS": {"min": [0.0, 0.0], "max": [12000.0, 9000.0]},
                "B_OBJECT_ASSET_INDEX": {"min": [13200.0, 0.0], "max": [20000.0, 9000.0]},
                "02_PREVIEW_CARDS": {"min": [0.0, -2200.0], "max": [6000.0, -500.0]},
                "03_REVIEW_QUARANTINE": {"min": [6400.0, -2200.0], "max": [12400.0, -500.0]},
                "99_EVIDENCE_LINKS": {"min": [12800.0, -2200.0], "max": [20000.0, -500.0]},
            },
            readability_report={
                "status": "fail",
                "issueCount": 2,
                "issues": ["A1 content density exceeds max", "A1/A2 aisle is too narrow"],
            },
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("visual warehouse readability audit failed", report["issues"])

    def test_visual_warehouse_readability_rejects_cramped_columns_and_preview_layer_content(self) -> None:
        from scripts.layout_system_asset_shelves import _audit_visual_warehouse_readability

        zones = {
            "A1_LINE_STANDARDS": {"min": [7590.0, -3650.0], "max": [20400.0, 9580.0]},
            "A2_ANNOTATION_STYLES": {"min": [21199.0, -3650.0], "max": [30733.0, 9580.0]},
            "B_OBJECT_ASSET_INDEX": {"min": [31933.0, -3650.0], "max": [45163.0, 9580.0]},
        }
        content_slots = {
            "A1_LINE_STANDARDS": {
                "bbox": {"min": [8350.0, 1446.0], "max": [19640.0, 6874.0]},
                "clusterStatus": "clustered_from_existing_content",
            },
            "A2_ANNOTATION_STYLES": {
                "bbox": {"min": [21960.0, -2003.0], "max": [29974.0, 7877.0]},
                "clusterStatus": "clustered_from_existing_content",
            },
        }
        protected_content = {
            "status": "ok",
            "clusters": [
                {
                    "clusterId": "A1_LINE_STANDARDS",
                    "bbox": content_slots["A1_LINE_STANDARDS"]["bbox"],
                    "entityCount": 24,
                    "layerSamples": ["CODEX_PREVIEW"],
                },
                {
                    "clusterId": "A2_ANNOTATION_STYLES",
                    "bbox": content_slots["A2_ANNOTATION_STYLES"]["bbox"],
                    "entityCount": 48,
                    "layerSamples": ["CODEX_PREVIEW"],
                },
            ],
        }

        report = _audit_visual_warehouse_readability(
            zones=zones,
            content_slots=content_slots,
            protected_content=protected_content,
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("A1_LINE_STANDARDS content width ratio exceeds 0.80", report["issues"])
        self.assertIn("A1/A2 visual aisle is too narrow", report["issues"])
        self.assertIn("protected asset proof content is still on CODEX_PREVIEW", report["issues"])

    def test_shelf_clearance_audit_rejects_entities_over_existing_asset_content(self) -> None:
        from scripts.layout_system_asset_shelves import _audit_shelf_content_clearance

        report = _audit_shelf_content_clearance(
            protected_content={
                "status": "ok",
                "clusters": [
                    {
                        "clusterId": "A2_ANNOTATION_STYLES",
                        "bbox": {"min": [100.0, 100.0], "max": [500.0, 500.0]},
                        "entityCount": 4,
                    }
                ],
            },
            created_entity_readback={
                "status": "ok",
                "entityBboxes": [
                    {
                        "handle": "AA1",
                        "layer": "ASSET_LABEL",
                        "bbox": {"min": [220.0, 240.0], "max": [360.0, 310.0]},
                    }
                ],
            },
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("shelf entity overlaps protected asset content", report["issues"])
        self.assertEqual(report["overlapCount"], 1)

    def test_content_cluster_layout_keeps_shelf_columns_outside_asset_content(self) -> None:
        from scripts.layout_system_asset_shelves import _bbox_contains, _layout_from_content_clusters

        clusters = [
            {
                "clusterId": "A1_LINE_STANDARDS",
                "bbox": {"min": [8000.0, 0.0], "max": [20800.0, 6000.0]},
                "entityCount": 24,
            },
            {
                "clusterId": "A2_ANNOTATION_STYLES",
                "bbox": {"min": [21400.0, 300.0], "max": [30200.0, 6800.0]},
                "entityCount": 48,
            },
        ]

        layout = _layout_from_content_clusters(clusters, fallback_bbox={"min": [8000.0, 0.0], "max": [30200.0, 6800.0]})
        zones = layout["zones"]

        self.assertTrue(_bbox_contains(zones["A1_LINE_STANDARDS"], clusters[0]["bbox"]))
        self.assertTrue(_bbox_contains(zones["A2_ANNOTATION_STYLES"], clusters[1]["bbox"]))
        self.assertLess(zones["A1_LINE_STANDARDS"]["max"][0], clusters[1]["bbox"]["min"][0])
        self.assertGreater(zones["A2_ANNOTATION_STYLES"]["min"][0], clusters[0]["bbox"]["max"][0])

    def test_object_asset_without_precise_boundary_stays_metadata_only(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_source_boundary_metadata") as root:
            report = sediment_system_asset(
                project_root=root,
                asset_id="sofa_unclear_source",
                name="来源不清沙发",
                category="furniture.seating.sofas",
                asset_kind="object_block",
                source={"type": "manual_metadata"},
            )

            package = json.loads((root / "libraries/system_library/furniture/seating/sofas/assets.json").read_text(encoding="utf-8"))
            asset = package["assets"][0]

            self.assertEqual(report["exportManifest"]["exportMode"], "metadata_only")
            self.assertEqual(report["libraryGovernance"]["decision"], "metadata_only_until_native_cad_export")
            self.assertIn("needs_source_boundary_review", report["polishHardeningDecision"]["categories"])
            self.assertEqual(asset["exportManifest"]["assetKind"], "object_block")
            self.assertEqual(asset["exportManifest"]["sourceBoundary"]["mode"], "manual_metadata")
            self.assertEqual(asset["antiContamination"]["decision"], "defer_export_until_precise_source_boundary")
            self.assertEqual(asset["native"]["layoutPlan"]["cleanSource"]["zoneId"], "03_REVIEW_QUARANTINE")
            self.assertFalse(asset["native"]["layoutPlan"]["cleanSource"]["copySourceAllowed"])
            self.assertIn("block export", asset["verification"]["notChecked"])

    def test_sedimentation_rejects_corrupted_chinese_before_writing_contract(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_encoding_preflight") as root:
            with self.assertRaises(ValueError) as ctx:
                sediment_system_asset(
                    project_root=root,
                    asset_id="bad_linetype_table",
                    name="绾垮瀷鏍峰紡",
                    category="drawing_standards.basic",
                    aliases=["绾垮瀷琛?"],
                    use_when=["鏀惧埌褰撳墠dwg"],
                )

            self.assertIn("text encoding preflight failed", str(ctx.exception))
            self.assertFalse((root / "libraries/system_library/registry.json").exists())
            self.assertFalse((root / "libraries/system_library/drawing_standards/basic/assets.json").exists())

    def test_cli_rejects_corrupted_chinese_as_structured_json(self) -> None:
        with temporary_artifact_dir("system_asset_encoding_preflight_cli") as root:
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "sediment_system_asset.py"),
                    "--project-root",
                    str(root),
                    "--category",
                    "drawing_standards.basic",
                    "--asset-id",
                    "bad_linetype_table",
                    "--name",
                    "绾垮瀷鏍峰紡",
                ],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 1)
            self.assertNotIn("Traceback", result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "fail")
            self.assertIn("text encoding preflight failed", report["reason"])
            self.assertFalse((root / "libraries/system_library/registry.json").exists())

    def test_object_block_export_requires_precise_source_boundary(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_source_boundary_reject") as root:
            with self.assertRaises(ValueError):
                sediment_system_asset(
                    project_root=root,
                    asset_id="sofa_bad_export",
                    name="错误边界沙发",
                    category="furniture.seating.sofas",
                    asset_kind="object_block",
                    export_mode="block_export",
                    source_boundary_mode="whole_codex_preview",
                    included_handles=["A1", "A2"],
                )

    def test_precise_created_handles_can_prepare_block_export_manifest(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_source_boundary_block") as root:
            report = sediment_system_asset(
                project_root=root,
                asset_id="sofa_precise_block",
                name="精确边界沙发",
                category="furniture.seating.sofas",
                asset_kind="object_block",
                export_mode="block_export",
                source_boundary_mode="created_handles",
                included_handles=["B1", "B2"],
                excluded_handles=["TXT1", "DIM1"],
                block_name="SOFA_PRECISE_BLOCK",
            )

            package = json.loads((root / "libraries/system_library/furniture/seating/sofas/assets.json").read_text(encoding="utf-8"))
            asset = package["assets"][0]

            self.assertEqual(report["exportManifest"]["exportMode"], "block_export")
            self.assertEqual(asset["exportManifest"]["sourceBoundary"]["mode"], "created_handles")
            self.assertEqual(asset["exportManifest"]["includedHandles"], ["B1", "B2"])
            self.assertEqual(asset["exportManifest"]["excludedHandles"], ["TXT1", "DIM1"])
            self.assertEqual(asset["antiContamination"]["decision"], "export_manifest_ready")
            self.assertIn("whole_codex_preview", asset["antiContamination"]["forbiddenSourceModes"])

    def test_style_standard_uses_style_export_and_rejects_block_export(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_source_boundary_style") as root:
            report = sediment_system_asset(
                project_root=root,
                asset_id="lineweight_style_standard",
                name="线宽线型样式标准",
                category="drawing_standards.basic",
                asset_kind="style_standard",
                source_boundary_mode="style_definition",
            )

            package = json.loads((root / "libraries/system_library/drawing_standards/basic/assets.json").read_text(encoding="utf-8"))
            asset = package["assets"][0]
            self.assertEqual(report["exportManifest"]["exportMode"], "style_export")
            self.assertEqual(asset["exportManifest"]["assetKind"], "style_standard")
            self.assertEqual(asset["antiContamination"]["decision"], "style_export_only")

            with self.assertRaises(ValueError):
                sediment_system_asset(
                    project_root=root,
                    asset_id="lineweight_bad_block",
                    name="错误块导出样式",
                    category="drawing_standards.basic",
                    asset_kind="style_standard",
                    export_mode="block_export",
                    source_boundary_mode="style_definition",
                )

    def test_conflict_policy_can_reject_or_create_variant(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_sedimentation_conflict") as root:
            sediment_system_asset(
                project_root=root,
                asset_id="sofa_reused_id",
                name="沙发初版",
                category="furniture.seating.sofas",
                dimensions={"width_mm": 1800},
                block_name="SOFA_ORIGINAL",
            )

            with self.assertRaises(ValueError):
                sediment_system_asset(
                    project_root=root,
                    asset_id="sofa_reused_id",
                    name="沙发冲突版",
                    category="furniture.seating.sofas",
                    dimensions={"width_mm": 2400},
                    block_name="SOFA_CHANGED",
                    conflict_policy="reject",
                )

            report = sediment_system_asset(
                project_root=root,
                asset_id="sofa_reused_id",
                name="沙发变体版",
                category="furniture.seating.sofas",
                dimensions={"width_mm": 2400},
                block_name="SOFA_CHANGED",
                conflict_policy="new_variant",
            )

            self.assertEqual(report["assetId"], "sofa_reused_id_v2")
            package = json.loads((root / "libraries/system_library/furniture/seating/sofas/assets.json").read_text(encoding="utf-8"))
            self.assertEqual([asset["assetId"] for asset in package["assets"]], ["sofa_reused_id", "sofa_reused_id_v2"])
            self.assertEqual(package["assets"][1]["versioning"]["derivedFromAssetId"], "sofa_reused_id")
            self.assertEqual(package["assets"][1]["versioning"]["conflictPolicy"], "new_variant")

    def test_verify_system_asset_package_checks_registry_and_contract(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset, verify_system_asset_package

        with temporary_artifact_dir("system_asset_sedimentation_verify") as root:
            sediment_system_asset(
                project_root=root,
                asset_id="sofa_verify_demo",
                name="沙发验收样例",
                category="furniture.seating.sofas",
                aliases=["验收沙发"],
                use_when=["验证资产包时使用"],
            )

            report = verify_system_asset_package(project_root=root, category="furniture.seating.sofas")

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["category"], "furniture.seating.sofas")
            self.assertEqual(report["assetCount"], 1)
            self.assertFalse(report["nativeDwgExists"])
            self.assertIn("metadata contract", report["checked"])
            self.assertIn("native DWG geometry", report["notChecked"])

    def test_registry_asset_rows_include_native_dwg_exists_flag(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset

        with temporary_artifact_dir("system_asset_registry_native_flag") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")

            sediment_system_asset(
                project_root=root,
                asset_id="dimstyle_native_flag",
                name="尺寸样式 native 标志",
                category="drawing_standards.basic",
                asset_kind="style_standard",
                export_mode="style_export",
                source_boundary_mode="style_definition",
            )

            registry = json.loads((root / "libraries/system_library/registry.json").read_text(encoding="utf-8"))
            asset = next(row for row in registry["assets"] if row["assetId"] == "dimstyle_native_flag")

            self.assertTrue(asset["nativeDwgExists"])

    def test_verify_fails_native_written_style_without_visible_panel_or_reuse_probe(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset, verify_system_asset_package

        with temporary_artifact_dir("system_asset_verify_style_gates_missing") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            sediment_system_asset(
                project_root=root,
                asset_id="dimstyle_missing_gates",
                name="缺门禁尺寸样式",
                category="drawing_standards.basic",
                asset_kind="style_standard",
                export_mode="style_export",
                source_boundary_mode="style_definition",
            )

            contract_path = root / "libraries/system_library/drawing_standards/basic/assets.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            asset = contract["assets"][0]
            asset["status"] = "verified"
            asset["lifecycle"]["status"] = "verified"
            asset["verification"]["status"] = "native_style_definition_written"
            asset["exportManifest"]["nativeWrite"] = "written_to_standard_assets_dwg"
            contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")

            registry_path = root / "libraries/system_library/registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry_asset = registry["assets"][0]
            registry_asset["status"] = "verified"
            registry_asset["lifecycleStatus"] = "verified"
            registry_asset["verificationStatus"] = "native_style_definition_written"
            registry_asset["exportManifest"]["nativeWrite"] = "written_to_standard_assets_dwg"
            registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")

            report = verify_system_asset_package(
                project_root=root,
                category="drawing_standards.basic",
                asset_id="dimstyle_missing_gates",
            )

            self.assertEqual(report["status"], "fail")
            self.assertIn("asset dimstyle_missing_gates missing native visible asset evidence", report["issues"])
            self.assertIn("asset dimstyle_missing_gates missing executable reuse workflow probe", report["issues"])
            self.assertIn("native visible asset evidence", report["notChecked"])
            self.assertIn("executable reuse workflow probe", report["notChecked"])

    def test_verify_accepts_visible_style_asset_with_reuse_probe_and_registry_summary(self) -> None:
        from core.assets.system_asset_sedimentation import sediment_system_asset, verify_system_asset_package

        visible_panel = {
            "status": "pass",
            "summary": "output/validation_runs/system-assets/dim/native_visible_panel_summary.json",
            "focusedScreenshot": "output/previews/dim-visible.png",
            "createdHandleCount": 12,
            "dimensionReadbackCount": 4,
            "savedAssetDwg": True,
            "savedCurrentDwg": False,
        }
        reuse_probe = {
            "status": "ready",
            "report": "output/validation_runs/system-assets/dim/reuse_probe.json",
            "readyTaskCount": 1,
            "blockedTaskCount": 0,
            "sourceSpecMode": "style_definition",
            "encodingPreflightStatus": "pass",
            "savedCurrentDwg": False,
        }
        with temporary_artifact_dir("system_asset_verify_style_gates_ready") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            sediment_system_asset(
                project_root=root,
                asset_id="dimstyle_ready_gates",
                name="完整门禁尺寸样式",
                category="drawing_standards.basic",
                asset_kind="style_standard",
                export_mode="style_export",
                source_boundary_mode="style_definition",
            )

            contract_path = root / "libraries/system_library/drawing_standards/basic/assets.json"
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
            asset = contract["assets"][0]
            asset["status"] = "verified"
            asset["lifecycle"]["status"] = "verified"
            asset["verification"]["status"] = "native_style_definition_written"
            asset["verification"]["evidence"] = {
                "nativeVisiblePanel": visible_panel,
                "reuseWorkflowProbe": reuse_probe,
            }
            asset["native"]["nativeVisiblePanelEvidence"] = visible_panel
            asset["nativeVisiblePanelEvidence"] = visible_panel
            asset["reuseWorkflowProbe"] = reuse_probe
            asset["exportManifest"]["nativeWrite"] = "written_to_standard_assets_dwg"
            contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2), encoding="utf-8")

            registry_path = root / "libraries/system_library/registry.json"
            registry = json.loads(registry_path.read_text(encoding="utf-8"))
            registry_asset = registry["assets"][0]
            registry_asset["status"] = "verified"
            registry_asset["lifecycleStatus"] = "verified"
            registry_asset["verificationStatus"] = "native_style_definition_written"
            registry_asset["nativeVisiblePanelEvidence"] = visible_panel
            registry_asset["reuseWorkflowProbe"] = reuse_probe
            registry_asset["exportManifest"]["nativeWrite"] = "written_to_standard_assets_dwg"
            registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")

            report = verify_system_asset_package(
                project_root=root,
                category="drawing_standards.basic",
                asset_id="dimstyle_ready_gates",
            )

            self.assertEqual(report["status"], "pass")
            self.assertIn("native visible asset evidence", report["checked"])
            self.assertIn("executable reuse workflow probe", report["checked"])
            self.assertIn("nativeVisiblePanelEvidence", registry["assets"][0])
            self.assertIn("reuseWorkflowProbe", registry["assets"][0])

    def test_cli_writes_system_asset_contract(self) -> None:
        with temporary_artifact_dir("system_asset_sedimentation_cli") as root:
            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "sediment_system_asset.py"),
                    "--project-root",
                    str(root),
                    "--asset-id",
                    "sofa_cli_demo",
                    "--name",
                    "命令行沙发资产",
                    "--category",
                    "furniture.seating.sofas",
                    "--alias",
                    "命令行沙发",
                    "--use-when",
                    "用户要求命令行沉淀沙发",
                    "--tag",
                    "plan",
                    "--block-name",
                    "SOFA_CLI_DEMO",
                    "--width-mm",
                    "2100",
                    "--depth-mm",
                    "900",
                    "--evidence-ref",
                    "output/previews/sofa_cli_demo.png",
                    "--scenario-tag",
                    "residential",
                    "--constraint",
                    "插入前确认朝向",
                    "--status",
                    "systemized",
                    "--feedback-ref",
                    "projects/demo/feedback.md#cli",
                    "--asset-kind",
                    "object_block",
                    "--source-boundary-mode",
                    "created_handles",
                    "--included-handle",
                    "CLI1",
                    "--excluded-handle",
                    "LABEL1",
                    "--export-mode",
                    "block_export",
                ],
                cwd=PROJECT_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["assetId"], "sofa_cli_demo")
            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["assetStatus"], "systemized")
            self.assertEqual(report["exportManifest"]["exportMode"], "block_export")
            self.assertEqual(report["libraryGovernance"]["governorAgentId"], "pipeline_asset_governor")
            self.assertEqual(report["assetGovernanceDecision"], "ready_for_clean_source_layout")
            self.assertEqual(report["nativeLayoutPlan"]["schemaVersion"], 2)
            self.assertEqual(report["nativeLayoutPlan"]["cleanSource"]["zoneId"], "01_CLEAN_ASSETS")
            self.assertIn("needs_native_cad_relayout", report["polishHardeningDecision"]["categories"])
            self.assertFalse(report["wroteCad"])
            self.assertTrue((root / "libraries/system_library/furniture/seating/sofas/assets.json").is_file())

    def test_pipeline_manifest_registers_asset_governance_agents(self) -> None:
        manifest = json.loads((PROJECT_ROOT / "agents/pipeline/pipeline_manifest.json").read_text(encoding="utf-8"))
        agents = {agent["agent_id"]: agent for agent in manifest["agents"]}

        for agent_id in (
            "pipeline_asset_governor",
            "pipeline_asset_librarian",
            "pipeline_asset_dwg_curator",
            "pipeline_asset_reuse_auditor",
        ):
            self.assertIn(agent_id, agents)

        self.assertIn("system_asset_sedimentation", manifest["orchestration"]["flow_variants"])
        sedimentation_flow = manifest["orchestration"]["flow_variants"]["system_asset_sedimentation"]
        self.assertEqual(sedimentation_flow[2], "pipeline_asset_governor")
        self.assertIn("asset_governance", manifest["orchestration"]["hard_gates"])


if __name__ == "__main__":
    unittest.main()
