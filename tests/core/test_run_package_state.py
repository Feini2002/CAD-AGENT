from __future__ import annotations

from pathlib import Path
import unittest

from tests.helpers import temporary_artifact_dir


class RunPackageStateTests(unittest.TestCase):
    def test_create_run_package_writes_resumable_structure(self) -> None:
        from core.orchestrator.run_package_state import RUN_STATES, create_run_package, load_run_state

        with temporary_artifact_dir("run_package_state") as root:
            state = create_run_package(
                "../Run Package 01",
                user_request={"text": "draw a preview only"},
                context_pack={"rules": ["no_cad_write"]},
                root_dir=root,
            )

            run_dir = Path(state["runDir"])
            self.assertTrue(run_dir.resolve().is_relative_to(root.resolve()))
            self.assertNotIn("..", run_dir.name)
            for filename in [
                "user_request.json",
                "context_pack.json",
                "task_contract.json",
                "dispatch_plan.json",
                "state.json",
                "final_report.md",
            ]:
                self.assertTrue((run_dir / filename).is_file(), filename)
            for dirname in ["agent_outputs", "cad_reports", "screenshots", "model_traces"]:
                self.assertTrue((run_dir / dirname).is_dir(), dirname)

            resumed = load_run_state(run_dir)
            self.assertEqual(resumed["status"], "created")
            self.assertEqual(resumed["currentStage"], "created")
            self.assertEqual(list(resumed["stages"].keys()), RUN_STATES)
            for stage in RUN_STATES:
                stage_state = resumed["stages"][stage]
                self.assertIn("inputFiles", stage_state)
                self.assertIn("outputFiles", stage_state)
                self.assertIn("status", stage_state)
                self.assertIn("blockingReason", stage_state)

    def test_advance_run_state_records_stage_io_and_can_resume(self) -> None:
        from core.orchestrator.run_package_state import advance_run_state, create_run_package, load_run_state

        with temporary_artifact_dir("run_package_resume") as root:
            state = create_run_package(
                "resume demo",
                user_request={"text": "collect context"},
                root_dir=root,
            )
            run_dir = Path(state["runDir"])

            advance_run_state(
                run_dir,
                "context_collected",
                input_files=["user_request.json"],
                output_files=["context_pack.json"],
            )

            resumed = load_run_state(run_dir)
            self.assertEqual(resumed["status"], "context_collected")
            self.assertEqual(resumed["currentStage"], "context_collected")
            stage_state = resumed["stages"]["context_collected"]
            self.assertEqual(stage_state["status"], "completed")
            self.assertEqual(stage_state["inputFiles"], ["user_request.json"])
            self.assertEqual(stage_state["outputFiles"], ["context_pack.json"])
            self.assertEqual(stage_state["blockingReason"], "")
            self.assertEqual(resumed["events"][-1]["stage"], "context_collected")

    def test_blocked_state_requires_and_persists_blocking_reason(self) -> None:
        from core.orchestrator.run_package_state import advance_run_state, create_run_package, load_run_state

        with temporary_artifact_dir("run_package_blocked") as root:
            state = create_run_package("blocked demo", user_request={"text": "needs review"}, root_dir=root)
            run_dir = Path(state["runDir"])

            with self.assertRaises(ValueError):
                advance_run_state(run_dir, "blocked")

            advance_run_state(
                run_dir,
                "blocked",
                input_files=["dispatch_plan.json"],
                blocking_reason="visual review is missing",
            )

            resumed = load_run_state(run_dir)
            self.assertEqual(resumed["status"], "blocked")
            self.assertEqual(resumed["stages"]["blocked"]["status"], "blocked")
            self.assertEqual(resumed["stages"]["blocked"]["blockingReason"], "visual review is missing")

    def test_invalid_stage_is_rejected(self) -> None:
        from core.orchestrator.run_package_state import advance_run_state, create_run_package

        with temporary_artifact_dir("run_package_invalid_stage") as root:
            state = create_run_package("invalid stage demo", user_request={"text": "hello"}, root_dir=root)

            with self.assertRaises(ValueError):
                advance_run_state(Path(state["runDir"]), "made_up_stage")


if __name__ == "__main__":
    unittest.main()
