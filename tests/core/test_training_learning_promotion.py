from __future__ import annotations

import json
import shutil
import subprocess
import sys
import unittest

from tests.helpers import PROJECT_ROOT, artifact_path

from core.training.learning_promotion import (
    classify_learning_failure,
    run_training_round_gate,
    write_learning_promotion_report,
)


class TrainingLearningPromotionTests(unittest.TestCase):
    def _fresh_artifact_root(self, *parts: str):
        root = artifact_path(*parts)
        if root.exists():
            shutil.rmtree(root)
        return root

    def test_classifies_failures_to_promotion_destinations(self) -> None:
        pipeline = classify_learning_failure(
            {
                "summary": "Delivery skipped audit and still asked the user to review.",
                "root_cause": "链路：误请用户验收，reference_match gate missing.",
            },
            case_id="residential_sofa_2seat_20260528",
            scene="residential",
        )
        core_probe = classify_learning_failure(
            {
                "summary": "closed_outer_shell forbidden pattern was missed.",
                "root_cause": "方法论反模式：whole object drawn as a box.",
            },
            case_id="residential_sofa_2seat_20260528",
            scene="residential",
        )
        scene_rule = classify_learning_failure(
            {
                "summary": "User meant same product family, not clone fragments.",
                "root_cause": "场景词汇：家装产品块改座数不能碎线 clone.",
            },
            case_id="residential_sofa_2seat_20260528",
            scene="residential",
        )

        self.assertEqual(pipeline["category"], "pipeline")
        self.assertEqual(pipeline["promotion_target"], "docs/training/pipeline-changelog.md")
        self.assertEqual(core_probe["category"], "core_probe_candidate")
        self.assertEqual(core_probe["promotion_target"], "core/verification/training_geometry_audit.py")
        self.assertEqual(scene_rule["category"], "scene_rule")
        self.assertEqual(scene_rule["promotion_target"], "agents/residential/rules.md")

    def test_writes_learning_promotion_report_without_mutating_rules(self) -> None:
        root = self._fresh_artifact_root("training_learning", "report_writer")
        case_dir = root / "projects" / "case_a"
        (case_dir / "runs").mkdir(parents=True, exist_ok=True)
        failure = {
            "summary": "Audit missed missing required parts.",
            "root_cause": "链路 + 几何：missing_required_parts probe needed.",
        }

        report_path = write_learning_promotion_report(case_dir, "round12", failure, scene="residential")

        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["case_id"], "case_a")
        self.assertEqual(report["round"], "round12")
        self.assertEqual(report["decision"]["category"], "pipeline")
        self.assertFalse(report["mutated_targets"])

    def test_visual_contract_gate_requires_parseable_visual_parts(self) -> None:
        root = self._fresh_artifact_root("training_learning", "visual_gate")
        case_dir = root / "projects" / "case_a"
        runs = case_dir / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        (case_dir / "feedback.md").write_text("# feedback\n", encoding="utf-8")
        (runs / "round12_style_compare.md").write_text("# compare\n", encoding="utf-8")
        (runs / "round12_agent_review.json").write_text(
            json.dumps({"delivery_allowed": False, "blocked_reason": "round12_not_executed_yet"}),
            encoding="utf-8",
        )

        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "fail")
        self.assertIn("round12_visual_parts.json", report["missing_artifacts"])

        (runs / "round12_visual_parts.json").write_text(
            json.dumps({"object": "sofa_plan", "parts": [{"id": "seat_left"}], "layout": {}, "forbidden": []}),
            encoding="utf-8",
        )
        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "fail", report)
        self.assertIn("style_target_missing", report["blocking_reasons"])

        (runs / "round12_visual_parts.json").write_text(
            json.dumps(
                {
                    "object": "sofa_plan",
                    "style_target": "expected/style_target_2seat.png",
                    "parts": [{"id": "seat_left"}],
                    "layout": {},
                    "forbidden": [],
                }
            ),
            encoding="utf-8",
        )
        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "fail", report)
        self.assertIn("style_target_file_missing:expected/style_target_2seat.png", report["blocking_reasons"])

        (case_dir / "expected").mkdir(parents=True, exist_ok=True)
        (case_dir / "expected" / "style_target_2seat.png").write_bytes(b"fake-png")
        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "fail", report)
        self.assertIn("style_target_source_not_reference_derived", report["blocking_reasons"])
        self.assertIn("style_target_evidence_missing", report["blocking_reasons"])

        (runs / "round12_visual_parts.json").write_text(
            json.dumps(
                {
                    "object": "sofa_plan",
                    "style_target": "expected/style_target_2seat.png",
                    "style_target_source": "reference_crop",
                    "style_target_evidence": {
                        "source_image": "runs/reference_crop.png",
                        "reference_handle": "4A2",
                        "reference_block": "5S03232",
                        "derived_from_real_cad_screenshot": True,
                        "generated": False,
                    },
                    "parts": [{"id": "seat_left"}],
                    "layout": {},
                    "forbidden": [],
                }
            ),
            encoding="utf-8",
        )
        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "fail", report)
        self.assertIn("style_target_source_image_file_missing:runs/reference_crop.png", report["blocking_reasons"])

        (runs / "reference_crop.png").write_bytes(b"fake-png")
        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "pass", report)

    def test_visual_contract_gate_rejects_generated_style_target(self) -> None:
        root = self._fresh_artifact_root("training_learning", "generated_style_target")
        case_dir = root / "projects" / "case_a"
        runs = case_dir / "runs"
        expected = case_dir / "expected"
        runs.mkdir(parents=True, exist_ok=True)
        expected.mkdir(parents=True, exist_ok=True)
        (case_dir / "feedback.md").write_text("# feedback\n", encoding="utf-8")
        (runs / "round12_style_compare.md").write_text("# compare\n", encoding="utf-8")
        (runs / "round12_agent_review.json").write_text("{}", encoding="utf-8")
        (runs / "reference_crop.png").write_bytes(b"fake-png")
        (expected / "style_target.png").write_bytes(b"fake-png")
        (runs / "round12_visual_parts.json").write_text(
            json.dumps(
                {
                    "object": "sofa_plan",
                    "style_target": "expected/style_target.png",
                    "style_target_source": "generated",
                    "style_target_evidence": {
                        "source_image": "runs/reference_crop.png",
                        "reference_handle": "4A2",
                        "reference_block": "5S03232",
                        "derived_from_real_cad_screenshot": False,
                        "generated": True,
                    },
                    "parts": [{"id": "seat_left"}],
                    "layout": {},
                    "forbidden": [],
                }
            ),
            encoding="utf-8",
        )

        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "fail", report)
        self.assertIn("style_target_source_not_reference_derived", report["blocking_reasons"])
        self.assertIn("generated_style_target_forbidden", report["blocking_reasons"])
        self.assertIn("style_target_not_real_cad_screenshot", report["blocking_reasons"])

    def test_delivery_gate_blocks_until_audit_and_review_allow_delivery(self) -> None:
        root = self._fresh_artifact_root("training_learning", "delivery_gate")
        case_dir = root / "projects" / "case_a"
        runs = case_dir / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        (case_dir / "feedback.md").write_text("# feedback\n", encoding="utf-8")
        (runs / "round12_execution_summary.json").write_text("{}", encoding="utf-8")
        (runs / "round12_geometry_audit.json").write_text(
            json.dumps({"audit_pass": False, "audit_failures": ["missing_required_parts"]}),
            encoding="utf-8",
        )
        (runs / "round12_style_compare.md").write_text("- [x] visual compare complete\n", encoding="utf-8")
        (runs / "round12_agent_review.json").write_text(
            json.dumps({"delivery_allowed": False, "blocked_reason": "audit_failed"}),
            encoding="utf-8",
        )
        (runs / "round12_preview.png").write_bytes(b"fake-png")

        report = run_training_round_gate(case_dir, "round12", stage="delivery")

        self.assertEqual(report["status"], "fail")
        self.assertIn("audit_not_passed", report["blocking_reasons"])
        self.assertIn("delivery_not_allowed", report["blocking_reasons"])

    def test_delivery_gate_reports_missing_required_artifacts(self) -> None:
        root = self._fresh_artifact_root("training_learning", "delivery_missing")
        case_dir = root / "projects" / "case_a"
        (case_dir / "runs").mkdir(parents=True, exist_ok=True)
        (case_dir / "feedback.md").write_text("# feedback\n", encoding="utf-8")

        report = run_training_round_gate(case_dir, "round12", stage="delivery")

        self.assertEqual(report["status"], "fail")
        self.assertIn("round12_execution_summary.json", report["missing_artifacts"])
        self.assertIn("round12_geometry_audit.json", report["missing_artifacts"])
        self.assertIn("round12_style_compare.md", report["missing_artifacts"])
        self.assertIn("round12_preview.png", report["missing_artifacts"])

    def test_delivery_gate_blocks_pending_style_compare(self) -> None:
        root = self._fresh_artifact_root("training_learning", "delivery_pending_style_compare")
        case_dir = root / "projects" / "case_a"
        runs = case_dir / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        (case_dir / "feedback.md").write_text("# feedback\n", encoding="utf-8")
        (runs / "round12_execution_summary.json").write_text("{}", encoding="utf-8")
        (runs / "round12_geometry_audit.json").write_text(
            json.dumps({"audit_pass": True, "audit_failures": []}),
            encoding="utf-8",
        )
        (runs / "round12_style_compare.md").write_text(
            "| part_id | round12 gate |\n| --- | --- |\n| seat_left | pending execution |\n- [ ] style target compared\n",
            encoding="utf-8",
        )
        (runs / "round12_agent_review.json").write_text(
            json.dumps({"delivery_allowed": True, "blocked_reason": ""}),
            encoding="utf-8",
        )
        (runs / "round12_preview.png").write_bytes(b"fake-png")

        report = run_training_round_gate(case_dir, "round12", stage="delivery")

        self.assertEqual(report["status"], "fail")
        self.assertIn("style_compare_pending", report["blocking_reasons"])

    def test_wrong_shape_json_is_reported_as_parse_error(self) -> None:
        root = self._fresh_artifact_root("training_learning", "wrong_shape_json")
        case_dir = root / "projects" / "case_a"
        runs = case_dir / "runs"
        runs.mkdir(parents=True, exist_ok=True)
        (case_dir / "feedback.md").write_text("# feedback\n", encoding="utf-8")
        (runs / "round12_visual_parts.json").write_text("[]", encoding="utf-8")
        (runs / "round12_style_compare.md").write_text("# compare\n", encoding="utf-8")
        (runs / "round12_agent_review.json").write_text("{}", encoding="utf-8")

        report = run_training_round_gate(case_dir, "round12", stage="visual_contract")

        self.assertEqual(report["status"], "fail")
        self.assertTrue(report["parse_errors"], report)

    def test_cli_emits_round_gate_report(self) -> None:
        case_dir = PROJECT_ROOT / "projects" / "residential_sofa_2seat_20260528"
        completed = subprocess.run(
            [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_training_round_gate.py"),
                "--case-dir",
                str(case_dir),
                "--round",
                "round12",
                "--stage",
                "visual_contract",
            ],
            cwd=PROJECT_ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["stage"], "visual_contract")
        self.assertEqual(report["status"], "pass", report)


if __name__ == "__main__":
    unittest.main()
