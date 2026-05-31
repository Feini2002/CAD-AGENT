from __future__ import annotations

import unittest

from tests.bootstrap import PROJECT_ROOT


class PlanMdGovernanceTests(unittest.TestCase):
    def test_handoff_does_not_carry_active_or_remaining_package_queue(self) -> None:
        handoff = (PROJECT_ROOT / "docs" / "handoffs" / "CURSOR_PACKAGE_HANDOFFS.md").read_text(
            encoding="utf-8"
        )

        forbidden = [
            "## 下一包建议",
            "剩余开发包细分索引",
            "继续按下表剩余小包交付",
            "后续按下表小包继续交付",
        ]
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, handoff)

    def test_status_page_does_not_present_historical_split_as_active_queue(self) -> None:
        status = (PROJECT_ROOT / "docs" / "status" / "current.md").read_text(encoding="utf-8")

        self.assertNotIn("这些是后续 Cursor / Codex 按包执行的开发清单", status)
        self.assertIn("后续任务和优先级只写入 PlanMD", status)

    def test_planmd_phase_status_matches_completed_scene_alpha_queue(self) -> None:
        plan = (PROJECT_ROOT / "CORE_RESTRUCTURE_PLAN.md").read_text(encoding="utf-8")

        self.assertNotIn("正式 Alpha 验收未做", plan)
        self.assertNotIn("Phase X | 下一优先级", plan)

    def test_core_status_has_four_progress_metrics_section(self) -> None:
        core_status = (PROJECT_ROOT / "CORE_STATUS.md").read_text(encoding="utf-8")

        self.assertIn("## 四进度口径（固定模板，V-PROOF-04 + 表 C）", core_status)
        self.assertIn("表 C", core_status)
        self.assertIn("cad_strength_headline_percent", core_status)
        self.assertIn("cad_proof_coverage", core_status)
        self.assertIn("禁止", core_status)
        self.assertIn("100%", core_status)
        self.assertIn("97%", core_status)
        self.assertIn("≠", core_status)

    def test_handoff_has_capability_proof_extension_template(self) -> None:
        handoff = (PROJECT_ROOT / "docs" / "handoffs" / "CURSOR_PACKAGE_HANDOFFS.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("能力证明包附加项（V-PROOF-05", handoff)
        self.assertIn("capability_id", handoff)
        self.assertIn("claim_level", handoff)
        self.assertIn("ladder_level", handoff)
        self.assertIn("cad_capability_coverage.json", handoff)

    def test_capability_proof_status_template_exists(self) -> None:
        path = PROJECT_ROOT / "docs" / "verification" / "capability_proof_status_template.md"
        self.assertTrue(path.is_file())
        text = path.read_text(encoding="utf-8")
        self.assertIn("禁止", text)
        self.assertIn("cad_proof_coverage_rate", text)
        self.assertIn("表 C", text)
        self.assertIn("cad_strength_headline_percent", text)

    def test_task_list_has_real_cad_strength_command(self) -> None:
        task_list = (PROJECT_ROOT / "docs" / "planning" / "任务清单.md").read_text(encoding="utf-8")
        self.assertIn("真实 CAD 实力", task_list)
        self.assertIn("推进表 C", task_list)
        self.assertIn("### 0.1 真实 CAD 实力口令", task_list)
        agents = (PROJECT_ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("真实 CAD 实力", agents)
        self.assertIn("刷新表 C", agents)

    def test_active_cad_docs_use_portable_python_path_examples(self) -> None:
        active_docs = [
            PROJECT_ROOT / "CAD卡壳排障入口.md",
            PROJECT_ROOT / "CORE_CONTEXT_BRIEF.md",
            PROJECT_ROOT / "README.md",
        ]

        for path in active_docs:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(r"C:\Users\User\.codex\mcp\CAD-MCP", text)


if __name__ == "__main__":
    unittest.main()
