from __future__ import annotations

import unittest

from tests.helpers import temporary_artifact_dir


class RuleContextPackTests(unittest.TestCase):
    def test_pack_includes_traceable_safety_sources_and_excludes_derived_snapshots(self) -> None:
        from core.orchestrator.rule_context_pack import build_rule_context_pack

        pack = build_rule_context_pack(
            run_id="rule-pack-case",
            agent_id="pipeline_design_director",
            task_kind="design_stage",
            trigger_signals=["design_judgment", "closeout_boundary"],
            retrieval_queries=["CAD_PLAN safety", "closeout claims", "capability-map-data.js"],
            schemas=["core/model_review/schemas/design_director_review.schema.json"],
            hard_gates=["cad_plan_validate", "closeout_gate"],
            forbidden_actions=["cad_write", "dwg_save", "delete_entities", "table_c_claim"],
        )

        self.assertEqual(pack["status"], "ready")
        self.assertIn("AGENTS.md", "\n".join(pack["sourceRefs"]))
        self.assertIn("docs/architecture/cad-agent-task-chain.md", "\n".join(pack["sourceRefs"]))
        self.assertNotIn("capability-map-data.js", "\n".join(pack["sourceRefs"]))
        self.assertIn("模型只能只读判断", "\n".join(pack["ruleDigest"]))
        self.assertIn("cad_plan_validate", pack["hardGates"])
        self.assertIn("cad_write", pack["forbiddenActions"])
        self.assertEqual(pack["schemas"], ["core/model_review/schemas/design_director_review.schema.json"])
        self.assertFalse(pack["missingContext"])

    def test_pack_blocks_when_l0_safety_rules_are_missing(self) -> None:
        from core.orchestrator.rule_context_pack import build_rule_context_pack

        with temporary_artifact_dir("rule_context_pack_missing_l0") as root:
            (root / "docs" / "architecture").mkdir(parents=True)
            (root / "docs" / "architecture" / "cad-agent-task-chain.md").write_text(
                "# task chain\n自然语言先拆成结构化任务。\n",
                encoding="utf-8",
            )

            pack = build_rule_context_pack(
                root=root,
                run_id="missing-l0-case",
                agent_id="pipeline_orchestrator",
                task_kind="ordinary_orchestration",
                retrieval_queries=["CAD_PLAN safety"],
            )

        self.assertEqual(pack["status"], "blocked")
        self.assertIn("L0 safety rules missing", pack["missingContext"])

    def test_context_budget_preserves_l0_safety_when_trimming_rule_refs(self) -> None:
        from core.orchestrator.rule_context_pack import build_rule_context_pack

        pack = build_rule_context_pack(
            run_id="budget-case",
            agent_id="pipeline_design_reviewer",
            task_kind="design_review",
            retrieval_queries=["CAD_PLAN", "trace", "manifest", "prompt", "style", "closeout"],
            context_budget={"maxRuleRefs": 1, "maxDigestItems": 1, "maxUpstreamOutputs": 1},
        )

        self.assertEqual(pack["status"], "ready")
        self.assertTrue(pack["contextBudget"]["criticalL0Preserved"])
        self.assertIn("AGENTS.md", "\n".join(pack["sourceRefs"]))
        self.assertIn("模型只能只读判断", "\n".join(pack["ruleDigest"]))


if __name__ == "__main__":
    unittest.main()
