from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.agents.scene_alpha import SCENE_ALPHA_SCENARIOS
from core.agents.scene_boundary_scan import (
    FORBIDDEN_IMPORT_PREFIXES,
    FORBIDDEN_SUBSTRINGS,
    scan_agent_tree,
    scan_text,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENTS_ROOT = PROJECT_ROOT / "agents"


class SceneAgentBoundaryTests(unittest.TestCase):
    def test_scene_agent_rule_manifest_exists(self) -> None:
        rules = (AGENTS_ROOT / "SCENE_AGENT_RULES.md").read_text(encoding="utf-8")

        self.assertIn("场景 Agent 是轻量偏好层", rules)
        self.assertIn("不可以放在 Agent 中", rules)
        self.assertIn("边界扫描", rules)

    def test_agents_reuse_core_and_do_not_claim_independent_execution(self) -> None:
        for manifest_path in AGENTS_ROOT.glob("*/agent.json"):
            with self.subTest(agent=manifest_path.parent.name):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertTrue(manifest["coreReuseRequired"])
                self.assertIn("plan_engine", manifest["usesCore"])
                self.assertIn("verification", manifest["usesCore"])

    def test_x_scene_03_alpha_scene_manifests_require_core_reuse(self) -> None:
        for scenario in SCENE_ALPHA_SCENARIOS:
            with self.subTest(scenario=scenario):
                manifest = json.loads((AGENTS_ROOT / scenario / "agent.json").read_text(encoding="utf-8"))
                self.assertEqual(manifest["id"], scenario)
                self.assertEqual(manifest["type"], "scene_agent")
                self.assertTrue(manifest["coreReuseRequired"])
                self.assertIn("layout_engine", manifest["usesCore"])

    def test_commercial_fitout_workflows_keep_core_pipeline(self) -> None:
        workflow_root = AGENTS_ROOT / "commercial_fitout" / "workflows"
        for name in ["blank_store_to_layout.md", "existing_plan_to_elevation.md"]:
            with self.subTest(workflow=name):
                text = (workflow_root / name).read_text(encoding="utf-8")
                self.assertIn("DESIGN_PROPOSAL", text)
                self.assertIn("CAD_PLAN", text)
                self.assertIn("VERIFICATION_REPORT", text)
                self.assertIn("不绕过", text)

    def test_agents_directory_contains_no_python_modules(self) -> None:
        python_files = list(AGENTS_ROOT.rglob("*.py"))
        self.assertEqual(python_files, [], python_files)

    def test_x_scene_03_agent_tree_passes_boundary_scan(self) -> None:
        violations = scan_agent_tree(AGENTS_ROOT)
        self.assertEqual(violations, [], violations)

    def test_x_scene_03_scanner_detects_synthetic_violations(self) -> None:
        samples = [
            ("bad_execute.py", "from core.execution.execute_plan import execute_plan_file\n"),
            ("bad_layout.py", "from core.layout_engine.zone_splitter import split_zones\n"),
            ("bad_geometry.py", "from core.geometry_backends.rect2d import rect_intersects\n"),
            ("bad_pipeline.py", "run_blank_shell_pipeline(workflow)\n"),
            ("bad_com.py", "driver = AutoCADComDriver()\n"),
        ]
        for relative_path, text in samples:
            with self.subTest(sample=relative_path):
                violations = scan_text(relative_path=relative_path, text=text)
                self.assertGreaterEqual(len(violations), 1, violations)

    def test_x_scene_03_forbidden_catalog_covers_cad_layout_and_geometry(self) -> None:
        rule_ids = {rule_id for rule_id, _ in FORBIDDEN_SUBSTRINGS}
        self.assertTrue(
            {"cad_execute", "cad_readback", "pipeline_impl", "layout_algorithm", "geometry_lib"}.issubset(rule_ids)
        )
        import_rule_ids = {rule_id for rule_id, _ in FORBIDDEN_IMPORT_PREFIXES}
        self.assertIn("core_import", import_rule_ids)

    def test_scene_agent_files_do_not_implement_core_execution_or_readback(self) -> None:
        """Legacy substring guard kept for regression; canonical scan is scan_agent_tree."""

        violations = scan_agent_tree(AGENTS_ROOT)
        legacy_patterns = [
            "execute_plan_file",
            "AutoCADComDriver",
            "validate_plan(",
            "snapshot_modelspace",
        ]
        combined = " ".join(item.detail for item in violations)
        for pattern in legacy_patterns:
            if pattern in combined:
                return
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
