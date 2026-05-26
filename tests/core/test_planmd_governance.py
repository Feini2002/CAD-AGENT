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
        status = (PROJECT_ROOT / "CAD_AGENT_STATUS.md").read_text(encoding="utf-8")

        self.assertNotIn("这些是后续 Cursor / Codex 按包执行的开发清单", status)
        self.assertIn("后续优先级、Phase 顺序、待办和退出标准只以唯一 `PlanMD`", status)

    def test_planmd_phase_status_matches_completed_scene_alpha_queue(self) -> None:
        plan = (PROJECT_ROOT / "CORE_RESTRUCTURE_PLAN.md").read_text(encoding="utf-8")

        self.assertNotIn("正式 Alpha 验收未做", plan)
        self.assertNotIn("Phase X | 下一优先级", plan)

    def test_active_cad_docs_use_portable_python_path_examples(self) -> None:
        active_docs = [
            PROJECT_ROOT / "CAD_AGENT_BLOCKER_PLAYBOOK.md",
            PROJECT_ROOT / "CORE_CONTEXT_BRIEF.md",
            PROJECT_ROOT / "README.md",
        ]

        for path in active_docs:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertNotIn(r"C:\Users\User\.codex\mcp\CAD-MCP", text)


if __name__ == "__main__":
    unittest.main()
