from __future__ import annotations

import json
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


class SceneAgentBoundaryTests(unittest.TestCase):
    def test_scene_agent_rule_manifest_exists(self) -> None:
        rules = (PROJECT_ROOT / "agents" / "SCENE_AGENT_RULES.md").read_text(encoding="utf-8")

        self.assertIn("场景 Agent 是轻量偏好层", rules)
        self.assertIn("不可以放在 Agent 中", rules)

    def test_agents_reuse_core_and_do_not_claim_independent_execution(self) -> None:
        for manifest_path in (PROJECT_ROOT / "agents").glob("*/agent.json"):
            with self.subTest(agent=manifest_path.parent.name):
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                self.assertTrue(manifest["coreReuseRequired"])
                self.assertIn("plan_engine", manifest["usesCore"])
                self.assertIn("verification", manifest["usesCore"])

    def test_commercial_fitout_workflows_keep_core_pipeline(self) -> None:
        workflow_root = PROJECT_ROOT / "agents" / "commercial_fitout" / "workflows"
        for name in ["blank_store_to_layout.md", "existing_plan_to_elevation.md"]:
            with self.subTest(workflow=name):
                text = (workflow_root / name).read_text(encoding="utf-8")
                self.assertIn("DESIGN_PROPOSAL", text)
                self.assertIn("CAD_PLAN", text)
                self.assertIn("VERIFICATION_REPORT", text)
                self.assertIn("不绕过", text)

    def test_scene_agent_files_do_not_implement_core_execution_or_readback(self) -> None:
        forbidden = [
            "execute_plan_file",
            "AutoCADComDriver",
            "validate_plan(",
            "snapshot_modelspace",
            "AddLine(",
            "AddText(",
            "AddDimAligned(",
            "save_dwg",
            "delete_entity",
        ]
        paths = [
            *list((PROJECT_ROOT / "agents").rglob("*.py")),
            *list((PROJECT_ROOT / "agents").rglob("*.md")),
            *list((PROJECT_ROOT / "agents").rglob("*.json")),
        ]
        for path in paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                for pattern in forbidden:
                    self.assertNotIn(pattern, text)


if __name__ == "__main__":
    unittest.main()
