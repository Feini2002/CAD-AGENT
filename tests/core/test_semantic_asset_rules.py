from __future__ import annotations

import json
import unittest
from pathlib import Path

from tests.helpers import temporary_artifact_dir


class SemanticAssetRulesTests(unittest.TestCase):
    def _write_registry(self, root: Path, assets: list[dict[str, object]]) -> None:
        path = root / "libraries/system_library/registry.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"schemaVersion": 1, "packages": [], "assets": assets}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _style_asset(self, asset_id: str, *, status: str, native: bool) -> dict[str, object]:
        return {
            "assetId": asset_id,
            "name": "线型表",
            "category": "drawing_standards.basic",
            "aliases": ["线型表", "线型样式"],
            "useWhen": ["需要查看线型样式时"],
            "status": status,
            "lifecycleStatus": status,
            "assetKind": "style_standard",
            "nativeDwg": "libraries/system_library/drawing_standards/basic/standard_assets.dwg",
            "nativeDwgExists": native,
            "native": {
                "dwg": "libraries/system_library/drawing_standards/basic/standard_assets.dwg",
                "nativeDwgExists": native,
            },
            "exportManifest": {"assetKind": "style_standard", "exportMode": "style_export", "includedHandles": []},
        }

    def test_registry_encoding_preflight_blocks_reuse_workflow_before_matching(self) -> None:
        from core.assets.system_asset_reuse import build_system_asset_reuse_workflow

        with temporary_artifact_dir("semantic_rules_registry_encoding") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            bad_asset = self._style_asset("bad_linetype", status="verified", native=True)
            bad_asset["name"] = "绾垮瀷鏍峰紡"
            self._write_registry(root, [bad_asset])

            workflow = build_system_asset_reuse_workflow("放一个线型表到当前图", project_root=root)

            self.assertEqual(workflow["status"], "asset_registry_encoding_failed", workflow)
            self.assertEqual(workflow["understanding"]["encodingPreflight"]["status"], "fail")
            self.assertEqual(workflow["reusePlans"], [])
            self.assertFalse(workflow["target"]["saveCurrentDwg"])

    def test_candidate_ranking_prefers_verified_native_reusable_asset(self) -> None:
        from core.assets.system_asset_reuse import find_system_asset_matches

        with temporary_artifact_dir("semantic_rules_candidate_ranking") as root:
            native = root / "libraries/system_library/drawing_standards/basic/standard_assets.dwg"
            native.parent.mkdir(parents=True, exist_ok=True)
            native.write_bytes(b"dwg-placeholder")
            candidate = self._style_asset("linetype_candidate", status="candidate", native=False)
            systemized = self._style_asset("linetype_systemized", status="systemized", native=False)
            verified = self._style_asset("linetype_verified", status="verified", native=True)
            self._write_registry(root, [candidate, systemized, verified])

            matches = find_system_asset_matches("调用线型表", project_root=root, min_score=1.0, max_matches=3)

            self.assertEqual([match.asset["assetId"] for match in matches], ["linetype_verified", "linetype_systemized", "linetype_candidate"])

    def test_semantic_rule_catalog_routes_linetype_table_and_sedimentation(self) -> None:
        from core.assets.semantic_rules import match_semantic_rules

        reuse_matches = match_semantic_rules("放一个线型表到当前图")
        generic_reuse_matches = match_semantic_rules("调用尺寸样式资产")
        sediment_matches = match_semantic_rules("沉淀线型表资产")

        self.assertEqual(reuse_matches[0]["ruleId"], "linetype_style_summary_table")
        self.assertIn("system_asset_reuse", reuse_matches[0]["routes"])
        self.assertEqual(generic_reuse_matches[0]["ruleId"], "system_asset_reuse")
        self.assertIn("reuse_workflow_probe", generic_reuse_matches[0]["requiredGuards"])
        self.assertEqual(sediment_matches[0]["ruleId"], "system_asset_sedimentation")
        self.assertIn("save_asset_dwg", sediment_matches[0]["requiredGuards"])
        self.assertIn("native_visible_asset_gate", sediment_matches[0]["requiredGuards"])
        self.assertIn("reuse_workflow_probe", sediment_matches[0]["requiredGuards"])

    def test_weak_asset_overlap_does_not_generate_ready_reuse_plan(self) -> None:
        from core.assets.system_asset_reuse import analyze_system_asset_search_need, build_system_asset_reuse_workflow

        with temporary_artifact_dir("semantic_rules_weak_asset_overlap") as root:
            asset = self._style_asset("layout_reference_asset", status="verified", native=True)
            asset["assetId"] = "weak_reference_asset"
            asset["name"] = "版式参考资产"
            asset["aliases"] = ["版式参考"]
            asset["category"] = "misc.reference"
            asset["retrieval"] = {"matchText": ["layout_catalog_reference"]}
            self._write_registry(root, [asset])

            decision = analyze_system_asset_search_need("draw layout guide", project_root=root)
            workflow = build_system_asset_reuse_workflow("draw layout guide", project_root=root)

            self.assertFalse(decision["shouldSearchSystemAssets"], decision)
            self.assertEqual(decision["trigger"], "no_asset_signal")
            self.assertEqual(decision["candidateMatches"][0]["assetId"], "weak_reference_asset")
            self.assertEqual(workflow["status"], "not_asset_reuse_request", workflow)
            self.assertEqual(workflow["reusePlans"], [])


if __name__ == "__main__":
    unittest.main()
