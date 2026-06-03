import json
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


class SystemAssetReuseTests(unittest.TestCase):
    def _write_registry(self, root: Path, assets: list[dict[str, Any]]) -> None:
        registry = {
            "schemaVersion": 1,
            "packages": [
                {
                    "category": "drawing_standards.basic",
                    "packagePath": "libraries/system_library/drawing_standards/basic",
                    "contractPath": "libraries/system_library/drawing_standards/basic/assets.json",
                    "nativeDwg": "libraries/system_library/drawing_standards/basic/standard_assets.dwg",
                    "nativeDwgExists": True,
                }
            ],
            "assets": assets,
        }
        path = root / "libraries/system_library/registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")

    def _linetype_asset(self) -> dict[str, Any]:
        return {
            "assetId": "linetype_style_summary_table",
            "name": "线型样式与颜色归纳表",
            "category": "drawing_standards.basic",
            "aliases": ["线型表", "线宽线型颜色归纳", "开启范围线样例"],
            "useWhen": ["需要统一查看或复用 CAD 线型、颜色、线宽和线型比例时"],
            "tags": ["drawing-standard", "linetype", "style-table"],
            "retrieval": {
                "matchText": ["线型样式与颜色归纳表", "线型表", "开启范围线样例", "linetype", "style-table"]
            },
            "status": "verified",
            "lifecycleStatus": "verified",
            "verificationStatus": "native_dwg_visual_verified",
            "assetKind": "style_standard",
            "nativeDwg": "libraries/system_library/drawing_standards/basic/standard_assets.dwg",
            "nativeDwgExists": True,
            "native": {
                "dwg": "libraries/system_library/drawing_standards/basic/standard_assets.dwg",
                "nativeDwgExists": True,
            },
            "exportManifest": {
                "assetKind": "style_standard",
                "exportMode": "style_export",
                "includedHandles": [],
            },
        }

    def _native_written_dimension_style_asset(self) -> dict[str, Any]:
        return {
            "assetId": "interior_dimension_style_visual_standard",
            "name": "室内尺寸样式视觉标准",
            "category": "drawing_standards.basic",
            "aliases": ["尺寸样式视觉标准", "室内洞口宽高尺寸", "05 06 尺寸样式修复"],
            "useWhen": ["室内立面高度、完成面、门洞、窗洞、设备洞口需要统一尺寸样式和可读比例样例时"],
            "tags": ["drawing-standard", "dimstyle", "interior-elevation", "opening-dimension"],
            "retrieval": {
                "matchText": [
                    "室内尺寸样式视觉标准",
                    "尺寸样式视觉标准",
                    "室内洞口宽高尺寸",
                    "05 06 尺寸样式修复",
                ]
            },
            "status": "systemized",
            "lifecycleStatus": "systemized",
            "verificationStatus": "native_style_definition_written",
            "assetKind": "style_standard",
            "nativeDwg": "libraries/system_library/drawing_standards/basic/standard_assets.dwg",
            "exportManifest": {
                "assetKind": "style_standard",
                "exportMode": "style_export",
                "includedHandles": [],
                "nativeWrite": "written_to_standard_assets_dwg",
                "sourceBoundary": {"mode": "style_definition", "precision": "precise_style_definition_native_write"},
            },
        }

    def _sofa_asset(self, *, precise_source: bool = True) -> dict[str, Any]:
        native = {
            "dwg": "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg",
            "nativeDwgExists": True,
        }
        manifest = {
            "assetKind": "object_block",
            "exportMode": "block_export" if precise_source else "metadata_only",
            "includedHandles": [],
        }
        if precise_source:
            native["blockName"] = "SOFA_A_2SEAT_TOP_VIEW"
            manifest["targetBlockName"] = "SOFA_A_2SEAT_TOP_VIEW"
        return {
            "assetId": "sofa_a_2seat_top_view" if precise_source else "sofa_unclear_source",
            "name": "双人沙发平面块" if precise_source else "来源不清沙发",
            "category": "furniture.seating.sofas",
            "aliases": ["沙发", "双人沙发", "sofa"],
            "useWhen": ["用户要求绘制或复用沙发平面资产"],
            "tags": ["furniture", "seating", "living-room"],
            "retrieval": {"matchText": ["沙发", "双人沙发", "sofa", "客厅沙发"]},
            "status": "verified" if precise_source else "candidate",
            "lifecycleStatus": "verified" if precise_source else "candidate",
            "assetKind": "object_block",
            "nativeDwg": "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg",
            "nativeDwgExists": True,
            "native": native,
            "exportManifest": manifest,
        }

    def test_semantic_query_builds_reuse_plan_for_verified_style_asset(self) -> None:
        from core.assets.system_asset_reuse import build_system_asset_reuse_plan, should_search_system_assets

        with temporary_artifact_dir("system_asset_reuse_plan") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset()])

            self.assertTrue(should_search_system_assets("从线型表资产调用开启范围线样例放到当前dwg"))
            self.assertFalse(should_search_system_assets("画一个普通矩形"))

            plan = build_system_asset_reuse_plan(
                "从线型表资产调用开启范围线样例放到当前dwg",
                project_root=root,
                base_point=[100.0, 200.0, 0.0],
            )

            self.assertEqual(plan["status"], "ready")
            self.assertEqual(plan["assetId"], "linetype_style_summary_table")
            self.assertEqual(plan["sourceSpec"]["mode"], "layer")
            self.assertEqual(plan["sourceSpec"]["layer"], "CODEX_PREVIEW")
            self.assertFalse(plan["target"]["saveCurrentDwg"])

    def test_native_written_style_asset_builds_style_definition_plan(self) -> None:
        from core.assets.system_asset_reuse import apply_system_asset_reuse_plan, build_system_asset_reuse_workflow
        from core.verification.fake_cad_driver import FakeCadDriver

        class NoCopyDriver(FakeCadDriver):
            def copy_entities_from_dwg(self, **kwargs: Any) -> dict[str, Any]:
                raise AssertionError("style_definition reuse must not copy CODEX_PREVIEW geometry")

        with temporary_artifact_dir("system_asset_reuse_native_written_style") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._native_written_dimension_style_asset()])

            workflow = build_system_asset_reuse_workflow(
                "调用室内洞口宽高尺寸样式，复用尺寸样式视觉标准",
                project_root=root,
            )

            self.assertEqual(workflow["status"], "ready")
            self.assertEqual(workflow["reusePlans"][0]["assetId"], "interior_dimension_style_visual_standard")
            self.assertEqual(workflow["reusePlans"][0]["sourceSpec"]["mode"], "style_definition")
            self.assertEqual(workflow["reusePlans"][0]["sourceSpec"]["nativeWrite"], "written_to_standard_assets_dwg")
            self.assertFalse(workflow["reusePlans"][0]["target"]["saveCurrentDwg"])

            report = apply_system_asset_reuse_plan(workflow["reusePlans"][0], driver=NoCopyDriver())

            self.assertEqual(report["status"], "style_reuse_deferred_cad_required")
            self.assertFalse(report["savedCurrentDwg"])

    def test_implicit_asset_need_uses_strong_semantic_match(self) -> None:
        from core.assets.system_asset_reuse import analyze_system_asset_search_need, build_system_asset_reuse_workflow

        with temporary_artifact_dir("system_asset_reuse_implicit") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset()])

            decision = analyze_system_asset_search_need("放一个线型表到当前图", project_root=root)
            workflow = build_system_asset_reuse_workflow("放一个线型表到当前图", project_root=root)

            self.assertTrue(decision["shouldSearchSystemAssets"])
            self.assertEqual(decision["trigger"], "implicit_asset_match")
            self.assertEqual(workflow["status"], "ready")
            self.assertEqual(workflow["understanding"]["taskCount"], 1)
            self.assertEqual(workflow["reusePlans"][0]["assetId"], "linetype_style_summary_table")

    def test_workflow_decomposes_multiple_asset_reuse_tasks(self) -> None:
        from core.assets.system_asset_reuse import build_system_asset_reuse_workflow

        with temporary_artifact_dir("system_asset_reuse_workflow") as root:
            standard = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            sofa = root / "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg"
            standard.parent.mkdir(parents=True, exist_ok=True)
            sofa.parent.mkdir(parents=True, exist_ok=True)
            standard.write_bytes(b"dwg-placeholder")
            sofa.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset(), self._sofa_asset()])

            workflow = build_system_asset_reuse_workflow(
                "放一个线型表，再放一个沙发",
                project_root=root,
                base_point=[100.0, 200.0, 0.0],
            )

            self.assertEqual(workflow["status"], "ready")
            self.assertEqual(workflow["understanding"]["taskCount"], 2)
            self.assertEqual({plan["assetId"] for plan in workflow["reusePlans"]}, {"linetype_style_summary_table", "sofa_a_2seat_top_view"})
            self.assertEqual(workflow["reusePlans"][0]["target"]["basePoint"], [100.0, 200.0, 0.0])
            self.assertEqual(workflow["reusePlans"][1]["target"]["basePoint"], [12100.0, 200.0, 0.0])

    def test_workflow_infers_multiple_assets_from_single_clause(self) -> None:
        from core.assets.system_asset_reuse import build_system_asset_reuse_workflow

        with temporary_artifact_dir("system_asset_reuse_single_clause_multi") as root:
            standard = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            sofa = root / "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg"
            standard.parent.mkdir(parents=True, exist_ok=True)
            sofa.parent.mkdir(parents=True, exist_ok=True)
            standard.write_bytes(b"dwg-placeholder")
            sofa.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset(), self._sofa_asset()])

            workflow = build_system_asset_reuse_workflow("放一个线型表和沙发", project_root=root)

            self.assertEqual(workflow["status"], "ready")
            self.assertEqual(workflow["understanding"]["taskCount"], 2)
            self.assertEqual({task["assetId"] for task in workflow["tasks"]}, {"linetype_style_summary_table", "sofa_a_2seat_top_view"})

    def test_workflow_reports_partial_when_one_asset_source_is_unclear(self) -> None:
        from core.assets.system_asset_reuse import build_system_asset_reuse_workflow

        with temporary_artifact_dir("system_asset_reuse_workflow_partial") as root:
            standard = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            sofa = root / "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg"
            standard.parent.mkdir(parents=True, exist_ok=True)
            sofa.parent.mkdir(parents=True, exist_ok=True)
            standard.write_bytes(b"dwg-placeholder")
            sofa.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset(), self._sofa_asset(precise_source=False)])

            workflow = build_system_asset_reuse_workflow("放一个线型表，再放一个沙发", project_root=root)

            self.assertEqual(workflow["status"], "partial")
            self.assertEqual(workflow["understanding"]["readyTaskCount"], 1)
            self.assertEqual(workflow["understanding"]["blockedTaskCount"], 1)
            self.assertEqual(workflow["blockedTasks"][0]["planStatus"], "needs_precise_native_source")

    def test_matching_asset_without_precise_source_is_blocked(self) -> None:
        from core.assets.system_asset_reuse import build_system_asset_reuse_plan

        asset = {
            "assetId": "sofa_unclear_source",
            "name": "来源不清沙发",
            "category": "furniture.seating.sofas",
            "aliases": ["沙发"],
            "status": "candidate",
            "assetKind": "object_block",
            "nativeDwg": "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg",
            "native": {"dwg": "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg"},
            "exportManifest": {"assetKind": "object_block", "exportMode": "metadata_only"},
        }
        with temporary_artifact_dir("system_asset_reuse_blocked") as root:
            native = root / "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [asset])

            plan = build_system_asset_reuse_plan("调用沙发资产放到当前dwg", project_root=root)

            self.assertEqual(plan["status"], "needs_precise_native_source")
            self.assertEqual(plan["assetId"], "sofa_unclear_source")

    def test_apply_reuse_plan_uses_driver_copy_and_readback_without_saving_current_dwg(self) -> None:
        from core.assets.system_asset_reuse import apply_system_asset_reuse_plan, build_system_asset_reuse_plan
        from core.verification.fake_cad_driver import FakeCadDriver

        class CopyingFakeDriver(FakeCadDriver):
            def copy_entities_from_dwg(self, **kwargs: Any) -> dict[str, Any]:
                line = self.draw_line(
                    start_point=[0, 0, 0],
                    end_point=[100, 0, 0],
                    layer=kwargs["target_layer"],
                )
                return {
                    "status": "copied",
                    "created_handles": [line["handle"]],
                    "sourceDwg": kwargs["source_dwg"],
                    "savedCurrentDwg": False,
                }

        with temporary_artifact_dir("system_asset_reuse_apply") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset()])
            plan = build_system_asset_reuse_plan("调用线型表资产", project_root=root)

            report = apply_system_asset_reuse_plan(plan, driver=CopyingFakeDriver())

            self.assertEqual(report["status"], "asset_reused")
            self.assertEqual(report["createdHandleCount"], 1)
            self.assertEqual(report["readbackEntityCount"], 1)
            self.assertEqual(report["readbackStatus"], "ok")
            self.assertFalse(report["savedCurrentDwg"])

    def test_apply_reuse_plan_does_not_pass_when_created_handles_cannot_be_read_back(self) -> None:
        from core.assets.system_asset_reuse import apply_system_asset_reuse_plan, build_system_asset_reuse_plan
        from core.verification.fake_cad_driver import FakeCadDriver

        class MissingReadbackDriver(FakeCadDriver):
            def copy_entities_from_dwg(self, **kwargs: Any) -> dict[str, Any]:
                return {
                    "status": "copied",
                    "created_handles": ["MISSING"],
                    "sourceDwg": kwargs["source_dwg"],
                    "savedCurrentDwg": False,
                }

        with temporary_artifact_dir("system_asset_reuse_missing_readback") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset()])
            plan = build_system_asset_reuse_plan("调用线型表资产", project_root=root)

            report = apply_system_asset_reuse_plan(plan, driver=MissingReadbackDriver())

            self.assertEqual(report["status"], "asset_reuse_readback_empty")
            self.assertEqual(report["createdHandleCount"], 1)
            self.assertEqual(report["readbackEntityCount"], 0)
            self.assertFalse(report["savedCurrentDwg"])

    def test_apply_reuse_workflow_runs_ready_plans_and_combines_readback(self) -> None:
        from core.assets.system_asset_reuse import apply_system_asset_reuse_workflow, build_system_asset_reuse_workflow
        from core.verification.fake_cad_driver import FakeCadDriver

        class CopyingFakeDriver(FakeCadDriver):
            def __init__(self) -> None:
                super().__init__()
                self.copy_calls: list[dict[str, Any]] = []

            def copy_entities_from_dwg(self, **kwargs: Any) -> dict[str, Any]:
                self.copy_calls.append(kwargs)
                line = self.draw_line(
                    start_point=[0, 0, 0],
                    end_point=[100, 0, 0],
                    layer=kwargs["target_layer"],
                )
                return {
                    "status": "copied",
                    "created_handles": [line["handle"]],
                    "sourceDwg": kwargs["source_dwg"],
                    "savedCurrentDwg": False,
                }

        with temporary_artifact_dir("system_asset_reuse_apply_workflow") as root:
            standard = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            sofa = root / "libraries/system_library/furniture/seating/sofas/sofa_assets.dwg"
            standard.parent.mkdir(parents=True, exist_ok=True)
            sofa.parent.mkdir(parents=True, exist_ok=True)
            standard.write_bytes(b"dwg-placeholder")
            sofa.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset(), self._sofa_asset()])
            workflow = build_system_asset_reuse_workflow("放一个线型表，再放一个沙发", project_root=root)
            driver = CopyingFakeDriver()

            report = apply_system_asset_reuse_workflow(workflow, driver=driver)

            self.assertEqual(report["status"], "asset_reuse_workflow_completed")
            self.assertEqual(report["createdHandleCount"], 2)
            self.assertEqual(report["readbackEntityCount"], 2)
            self.assertEqual(len(driver.copy_calls), 2)
            self.assertFalse(report["savedCurrentDwg"])

    def test_apply_reuse_workflow_without_ready_plans_is_blocked_explicitly(self) -> None:
        from core.assets.system_asset_reuse import apply_system_asset_reuse_workflow
        from core.verification.fake_cad_driver import FakeCadDriver

        report = apply_system_asset_reuse_workflow(
            {
                "kind": "system_asset_reuse_workflow",
                "status": "needs_asset_match",
                "reusePlans": [],
                "blockedTasks": [{"taskId": "asset_reuse_1", "planStatus": "needs_asset_match"}],
            },
            driver=FakeCadDriver(),
        )

        self.assertEqual(report["status"], "asset_reuse_workflow_blocked")
        self.assertEqual(report["workflowStatus"], "needs_asset_match")
        self.assertFalse(report["savedCurrentDwg"])

    def test_cli_plan_only_resolves_system_asset(self) -> None:
        with temporary_artifact_dir("system_asset_reuse_cli") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset()])

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "reuse_system_asset.py"),
                    "--project-root",
                    str(root),
                    "--plan-only",
                    "调用线型表资产",
                ],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "ready")
            self.assertEqual(report["assetId"], "linetype_style_summary_table")

    def test_cli_workflow_plan_only_resolves_system_asset(self) -> None:
        with temporary_artifact_dir("system_asset_reuse_cli_workflow") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset()])

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "reuse_system_asset.py"),
                    "--project-root",
                    str(root),
                    "--workflow",
                    "--plan-only",
                    "放一个线型表到当前图",
                ],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["kind"], "system_asset_reuse_workflow")
            self.assertEqual(report["status"], "ready")
            self.assertEqual(report["understanding"]["trigger"], "implicit_asset_match")

    def test_cli_workflow_plan_only_returns_strict_json_for_negative_probe(self) -> None:
        with temporary_artifact_dir("system_asset_reuse_cli_negative") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            self._write_registry(root, [self._linetype_asset()])

            result = subprocess.run(
                [
                    sys.executable,
                    str(PROJECT_ROOT / "scripts" / "reuse_system_asset.py"),
                    "--project-root",
                    str(root),
                    "--workflow",
                    "--plan-only",
                    "画一个普通矩形",
                ],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
            )

            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["status"], "not_asset_reuse_request")
            self.assertEqual(report["understanding"]["candidateMatches"], [])


if __name__ == "__main__":
    unittest.main()
