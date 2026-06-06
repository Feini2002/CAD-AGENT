from __future__ import annotations

import json
from pathlib import Path
import unittest

from core.model_review.codex_cli_client import CodexCliReviewConfig
from core.orchestrator.run_package_state import create_run_package, load_run_state
from tests.helpers import temporary_artifact_dir


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _prepare_run_package(root: Path) -> Path:
    state = create_run_package(
        "reviewer-host-runtime-case",
        user_request={"text": "画一个小茶几并请用户验收"},
        root_dir=root,
    )
    run_dir = Path(state["runDir"])
    _write_json(
        run_dir / "dispatch_plan.json",
        {
            "schemaVersion": "orchestrator-host-dispatch-plan/v1",
            "runId": state["runId"],
            "status": "ready",
            "route": "standard_draw",
            "taskKind": "ordinary_orchestration",
            "hardGates": ["validate_plan", "dry_run", "cad_readback", "visual_acceptance_review", "neighbor_protection"],
            "requiredAgents": ["pipeline_visual_acceptance_reviewer", "pipeline_delivery"],
        },
    )
    _write_json(
        run_dir / "task_contract.json",
        {
            "schemaVersion": "orchestrator-host-task-contract/v1",
            "runId": state["runId"],
            "status": "ready",
            "requiredAgents": ["pipeline_visual_acceptance_reviewer", "pipeline_delivery"],
            "hardGates": ["validate_plan", "dry_run", "cad_readback", "visual_acceptance_review", "neighbor_protection"],
            "deliveryBoundary": {"mayClaimComplete": False, "mayExecuteCad": False},
        },
    )
    return run_dir


def _write_passing_evidence(run_dir: Path) -> None:
    _write_json(run_dir / "cad_reports" / "validation_report.json", {"status": "pass"})
    _write_json(run_dir / "cad_reports" / "dry_run_report.json", {"status": "pass"})
    _write_json(
        run_dir / "cad_reports" / "readback_summary.json",
        {
            "status": "ok",
            "created_handles_readback": "ok",
            "targetLayer": "CODEX_PREVIEW",
            "savedCurrentDwg": False,
        },
    )
    _write_json(
        run_dir / "agent_outputs" / "visual_acceptance_output.json",
        {
            "status": "pass",
            "visualAcceptanceDecision": "pass",
            "blockingReasons": [],
            "lookHereFirst": ["茶几位置", "中文标注"],
        },
    )
    _write_json(run_dir / "cad_reports" / "neighbor_protection.json", {"status": "pass"})


class ReviewerHostRuntimeTests(unittest.TestCase):
    def test_ready_closeout_writes_delivery_review_and_final_report(self) -> None:
        from core.orchestrator.reviewer_host_runtime import run_reviewer_host_closeout_runtime

        with temporary_artifact_dir("reviewer_host_ready") as root:
            run_dir = _prepare_run_package(root)
            _write_passing_evidence(run_dir)

            result = run_reviewer_host_closeout_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

            self.assertEqual(result["deliveryReview"]["deliveryDecision"], "ready_to_ask_user_review")
            self.assertEqual(result["deliveryReview"]["openingLine"], "可验收")
            self.assertTrue(result["closeoutDecision"]["can_deliver"])
            self.assertFalse(result["modelReview"]["modelInvoked"])
            self.assertTrue((run_dir / "agent_outputs" / "pipeline_delivery.json").is_file())
            final_report = (run_dir / "final_report.md").read_text(encoding="utf-8")
            self.assertIn("可验收", final_report)
            self.assertIn("截图只作视觉辅助", final_report)
            self.assertEqual(load_run_state(run_dir)["status"], "ready_for_delivery")

    def test_missing_readback_blocks_and_allows_no_completion_claims(self) -> None:
        from core.orchestrator.reviewer_host_runtime import run_reviewer_host_closeout_runtime

        with temporary_artifact_dir("reviewer_host_missing_readback") as root:
            run_dir = _prepare_run_package(root)
            _write_passing_evidence(run_dir)
            (run_dir / "cad_reports" / "readback_summary.json").unlink()

            result = run_reviewer_host_closeout_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

            self.assertEqual(result["deliveryReview"]["deliveryDecision"], "not_verified")
            self.assertEqual(result["deliveryReview"]["openingLine"], "暂不交付")
            self.assertEqual(result["deliveryReview"]["finalResponseAllowedClaims"], [])
            self.assertIn("created_handles_readback missing", result["deliveryReview"]["blockingReasons"])
            self.assertEqual(load_run_state(run_dir)["status"], "blocked")

    def test_screenshot_only_never_replaces_cad_readback(self) -> None:
        from core.orchestrator.reviewer_host_runtime import run_reviewer_host_closeout_runtime

        with temporary_artifact_dir("reviewer_host_screenshot_only") as root:
            run_dir = _prepare_run_package(root)
            _write_passing_evidence(run_dir)
            (run_dir / "cad_reports" / "readback_summary.json").unlink()
            (run_dir / "screenshots" / "preview.png").write_bytes(b"fake png")

            result = run_reviewer_host_closeout_runtime(run_dir, config=CodexCliReviewConfig(enabled=False))

            self.assertEqual(result["deliveryReview"]["status"], "fail")
            self.assertIn("截图只作视觉辅助", result["deliveryReview"]["evidenceDoesNotProve"])
            self.assertIn("created_handles_readback", result["deliveryReview"]["evidenceMissing"])


if __name__ == "__main__":
    unittest.main()
