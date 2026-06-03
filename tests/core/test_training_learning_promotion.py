from __future__ import annotations

import json
import unittest

from tests.helpers import temporary_artifact_dir


class TrainingLearningPromotionTests(unittest.TestCase):
    def accepted_report(self) -> dict:
        return {
            "status": "pass",
            "generated_at": "2026-06-01T00:00:00Z",
            "queueId": "cad-foundation-first-10",
            "mode": "unsupervised",
            "created_handle_count": 24,
            "readback_count": 24,
            "items": [
                {
                    "capabilityId": "cad-primitives",
                    "title": "01 基础图元",
                    "status": "pass",
                    "handle_count": 14,
                    "readback_count": 14,
                    "feedback": "中文面板已生成；handles 已回读；全部在 CODEX_PREVIEW",
                },
                {
                    "capabilityId": "cad-selection-edit",
                    "title": "02 选择编辑",
                    "status": "pass",
                    "handle_count": 10,
                    "readback_count": 10,
                    "feedback": "选择边界、删除边界和正式图层保护已通过",
                },
            ],
            "checks": [
                {"name": "all_10_items_generated", "status": "pass"},
                {"name": "persistent_handle_readback", "status": "pass"},
                {"name": "preview_layer_only", "status": "pass"},
                {"name": "dwg_not_saved", "status": "pass"},
                {"name": "chinese_labels", "status": "pass"},
            ],
            "visual_self_check": {"status": "pass"},
        }

    def programs(self) -> list[dict]:
        return [
            {
                "capabilityId": "cad-primitives",
                "name": "基础图元绘制",
                "responsibleAgentIds": ["cad_designer", "pipeline_intent", "pipeline_execute", "pipeline_audit"],
            },
            {
                "capabilityId": "cad-selection-edit",
                "name": "选择与基础编辑",
                "responsibleAgentIds": ["cad_designer", "pipeline_execute", "pipeline_audit"],
            },
        ]

    def test_promote_acceptance_writes_agent_memory_and_prompt_addenda(self) -> None:
        from core.training.learning_promotion import promote_training_acceptance

        with temporary_artifact_dir("training_learning") as root:
            report_path = root / "accepted_report.json"
            report_path.write_text(json.dumps(self.accepted_report(), ensure_ascii=False), encoding="utf-8")

            result = promote_training_acceptance(root=root, report_paths=[report_path], programs=self.programs())

            self.assertEqual(result["status"], "promoted")
            self.assertEqual(result["acceptedItemCount"], 2)
            self.assertEqual(result["promotedAgentCount"], 4)

            designer_memory = root / "agents" / "cad_designer" / "training_memory.json"
            designer_prompt = root / "agents" / "cad_designer" / "prompt_addendum.md"
            execute_memory = root / "agents" / "pipeline" / "execute" / "training_memory.json"
            execute_prompt = root / "agents" / "pipeline" / "execute" / "prompt_addendum.md"
            common_prompt = root / "agents" / "COMMON_PROMPT_CONTRACT.md"
            self.assertTrue(designer_memory.is_file())
            self.assertTrue(designer_prompt.is_file())
            self.assertTrue(execute_memory.is_file())
            self.assertTrue(execute_prompt.is_file())
            self.assertTrue(common_prompt.is_file())

            memory = json.loads(designer_memory.read_text(encoding="utf-8"))
            self.assertEqual(memory["agentId"], "cad_designer")
            self.assertEqual(memory["learningState"], "prompt_updated")
            self.assertEqual(len(memory["acceptedCapabilities"]), 2)
            self.assertIn("中文标注", " ".join(memory["promptUpdateSummary"]))
            self.assertIn("截图编排", " ".join(memory["promptUpdateSummary"]))
            self.assertIn("COMMON_PROMPT_CONTRACT.md", designer_prompt.read_text(encoding="utf-8"))
            self.assertIn("COMMON_PROMPT_CONTRACT.md", execute_prompt.read_text(encoding="utf-8"))
            self.assertNotIn("CAD 测试必须使用中文标注", designer_prompt.read_text(encoding="utf-8"))
            self.assertNotIn("任务级截图编排", designer_prompt.read_text(encoding="utf-8"))
            self.assertIn("真实 CAD 测试默认只写 CODEX_PREVIEW", common_prompt.read_text(encoding="utf-8"))
            self.assertIn("## 截图编排规则", common_prompt.read_text(encoding="utf-8"))
            self.assertIn("target_handles", common_prompt.read_text(encoding="utf-8"))

    def test_promote_acceptance_accepts_generic_all_items_generated_check(self) -> None:
        from core.training.learning_promotion import promote_training_acceptance

        with temporary_artifact_dir("training_learning_generic_items") as root:
            report = self.accepted_report()
            report["checks"] = [
                {"name": "all_items_generated", "status": "pass", "message": "2/2"},
                {"name": "persistent_handle_readback", "status": "pass"},
                {"name": "preview_layer_only", "status": "pass"},
                {"name": "dwg_not_saved", "status": "pass"},
                {"name": "chinese_labels", "status": "pass"},
            ]
            report_path = root / "accepted_report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

            result = promote_training_acceptance(root=root, report_paths=[report_path], programs=self.programs())

            self.assertEqual(result["status"], "promoted")
            self.assertEqual(result["acceptedItemCount"], 2)

    def test_promote_acceptance_accepts_utf8_bom_json_reports(self) -> None:
        from core.training.learning_promotion import promote_training_acceptance

        with temporary_artifact_dir("training_learning_bom") as root:
            report_path = root / "accepted_report.json"
            payload = json.dumps(self.accepted_report(), ensure_ascii=False)
            report_path.write_text("\ufeff" + payload, encoding="utf-8")

            result = promote_training_acceptance(root=root, report_paths=[report_path], programs=self.programs())

            self.assertEqual(result["status"], "promoted")
            self.assertEqual(result["acceptedItemCount"], 2)

    def test_promote_acceptance_preserves_custom_prompt_guidance(self) -> None:
        from core.training.learning_promotion import promote_training_acceptance

        with temporary_artifact_dir("training_learning_custom_guidance") as root:
            report = self.accepted_report()
            report["items"][0]["promptGuidance"] = [
                "用户用箭头或圈选指定 CAD 位置时，先从当前 CAD 实体回读参照 bbox，再按图像语义定位。",
            ]
            report_path = root / "accepted_report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

            promote_training_acceptance(root=root, report_paths=[report_path], programs=self.programs())

            designer_memory = json.loads(
                (root / "agents" / "cad_designer" / "training_memory.json").read_text(encoding="utf-8")
            )
            designer_prompt = (root / "agents" / "cad_designer" / "prompt_addendum.md").read_text(encoding="utf-8")
            self.assertIn("箭头或圈选", designer_memory["lessons"][0]["promptGuidance"][-1])
            self.assertIn("箭头或圈选", designer_prompt)

    def test_quick_trial_gate_remains_observation_without_system_writes(self) -> None:
        from core.training.promotion_gate import build_training_promotion_gate

        report = self.accepted_report()
        report["mode"] = "quick_trial"

        gate = build_training_promotion_gate(
            reports=[report],
            accepted_items=[],
            agent_updates=[],
            source_reports=["output/training/quick_trial.json"],
        )

        self.assertEqual(gate["promotionLevel"], "observation")
        self.assertEqual(gate["decisions"]["updateTrainingSource"]["required"], False)
        self.assertEqual(gate["decisions"]["updateWorkbench"]["required"], False)
        self.assertEqual(gate["decisions"]["updateAgentCalibration"]["required"], False)
        self.assertIn("快试", gate["decisions"]["updateTrainingSource"]["reason"])

    def test_promote_acceptance_writes_promotion_gate_for_sync_and_agent_calibration(self) -> None:
        from core.training.learning_promotion import promote_training_acceptance

        with temporary_artifact_dir("training_learning_gate") as root:
            report_path = root / "accepted_report.json"
            report_path.write_text(json.dumps(self.accepted_report(), ensure_ascii=False), encoding="utf-8")

            result = promote_training_acceptance(root=root, report_paths=[report_path], programs=self.programs())

            gate = result["promotionGate"]
            self.assertEqual(gate["schemaVersion"], 1)
            self.assertEqual(gate["promotionLevel"], "systemized")
            self.assertEqual(gate["decisions"]["updateTrainingSource"]["required"], True)
            self.assertEqual(gate["decisions"]["updateWorkbench"]["required"], True)
            self.assertEqual(gate["decisions"]["updateAgentCalibration"]["required"], True)
            self.assertEqual(gate["decisions"]["updateAgentCalibration"]["status"], "ready")
            self.assertEqual(gate["decisions"]["retestOriginalTask"]["required"], False)
            self.assertTrue({"cad_designer", "pipeline_execute"}.issubset(set(gate["agentCalibration"]["affectedAgentIds"])))
            self.assertIn("截图", " ".join(gate["agentCalibration"]["negativeExamples"]))

            ledger = json.loads((root / "output" / "training_learning" / "agent_learning_ledger.json").read_text(encoding="utf-8"))
            self.assertEqual(ledger["promotionGate"]["promotionLevel"], "systemized")

    def test_rule_deltas_are_candidates_and_require_reviewed_rule_updates(self) -> None:
        from core.training.learning_promotion import promote_training_acceptance

        with temporary_artifact_dir("training_learning_rule_deltas") as root:
            report = self.accepted_report()
            report["systemLearning"] = {
                "baseRuleDeltas": ["训练收尾必须生成 promotion gate。"],
                "taskRuleDeltas": ["线型表任务必须记录样例 containment 审计。"],
                "checkerDeltas": ["新增 promotion_gate_required_for_systemized 检查。"],
                "originalTaskRef": "projects/sample_case/runs/round2_report.json",
            }
            report_path = root / "accepted_report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

            result = promote_training_acceptance(root=root, report_paths=[report_path], programs=self.programs())
            decisions = result["promotionGate"]["decisions"]

            self.assertEqual(decisions["updateBaseRules"]["required"], True)
            self.assertEqual(decisions["updateBaseRules"]["status"], "needs_reviewed_package")
            self.assertEqual(decisions["updateTaskRules"]["required"], True)
            self.assertEqual(decisions["updateChecker"]["required"], True)
            self.assertEqual(decisions["retestOriginalTask"]["required"], True)
            self.assertIn("round2_report", decisions["retestOriginalTask"]["target"])

    def test_unknown_capability_does_not_fallback_to_designer_calibration(self) -> None:
        from core.training.learning_promotion import promote_training_acceptance

        with temporary_artifact_dir("training_learning_unknown_capability") as root:
            report = self.accepted_report()
            report["items"] = [
                {
                    "capabilityId": "unknown-capability",
                    "title": "未知能力",
                    "status": "pass",
                    "handle_count": 1,
                    "readback_count": 1,
                    "feedback": "不应自动写入 cad_designer",
                }
            ]
            report_path = root / "accepted_report.json"
            report_path.write_text(json.dumps(report, ensure_ascii=False), encoding="utf-8")

            result = promote_training_acceptance(root=root, report_paths=[report_path], programs=self.programs())

            self.assertEqual(result["status"], "no_promotable_acceptance")
            self.assertEqual(result["acceptedItemCount"], 0)
            self.assertFalse((root / "agents" / "cad_designer" / "training_memory.json").exists())
            self.assertEqual(result["promotionGate"]["promotionLevel"], "observation")

    def test_failure_promotion_report_records_candidate_gate_without_mutating_targets(self) -> None:
        from core.training.learning_promotion import write_learning_promotion_report

        with temporary_artifact_dir("training_failure_gate") as root:
            case_dir = root / "projects" / "case_a"
            failure = {
                "summary": "pipeline 跳过 audit 后直接 delivery，属于根源链路问题。",
                "root_cause": "delivery bypassed audit",
                "originalTaskRef": "projects/case_a/runs/round2_report.json",
            }

            path = write_learning_promotion_report(case_dir, "2", failure, scene="residential")

            report = json.loads(path.read_text(encoding="utf-8"))
            gate = report["promotionGate"]
            self.assertEqual(gate["promotionLevel"], "learning_candidate")
            self.assertEqual(report["mutated_targets"], [])
            self.assertEqual(gate["decisions"]["updateTaskRules"]["required"], True)
            self.assertEqual(gate["decisions"]["updateTaskRules"]["status"], "needs_reviewed_package")
            self.assertEqual(gate["decisions"]["updateAgentCalibration"]["required"], True)
            self.assertEqual(gate["decisions"]["retestOriginalTask"]["required"], True)
            self.assertIn("round2_report", gate["decisions"]["retestOriginalTask"]["target"])

    def test_build_learning_index_maps_capability_to_agent_updates(self) -> None:
        from core.training.learning_promotion import build_learning_index

        ledger = {
            "status": "promoted",
            "agentUpdates": [
                {
                    "agentId": "cad_designer",
                    "acceptedCapabilities": ["cad-primitives", "cad-selection-edit"],
                    "sourceRefs": ["agents/cad_designer/training_memory.json"],
                },
                {
                    "agentId": "pipeline_execute",
                    "acceptedCapabilities": ["cad-selection-edit"],
                    "sourceRefs": ["agents/pipeline/execute/training_memory.json"],
                },
            ],
            "promotionGate": {
                "schemaVersion": 1,
                "promotionLevel": "systemized",
                "decisions": {"updateWorkbench": {"required": True, "status": "required"}},
            },
        }

        index = build_learning_index(ledger)

        self.assertEqual(index["status"], "promoted")
        self.assertEqual(index["byCapability"]["cad-selection-edit"]["promotedAgentCount"], 2)
        self.assertEqual(index["byAgent"]["pipeline_execute"]["acceptedCapabilityCount"], 1)
        self.assertEqual(index["promotionGate"]["promotionLevel"], "systemized")
        self.assertEqual(index["byCapability"]["cad-selection-edit"]["promotionGate"]["decisions"]["updateWorkbench"]["required"], True)


if __name__ == "__main__":
    unittest.main()
