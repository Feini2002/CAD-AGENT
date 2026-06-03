from __future__ import annotations

import json
import subprocess
import sys
import unittest

from tests.helpers import PROJECT_ROOT, temporary_artifact_dir


class TrainingQueueRunnerTests(unittest.TestCase):
    def training_programs(self) -> list[dict]:
        from scripts import build_capability_map_data

        return build_capability_map_data.build_data()["trainingPrograms"]

    def test_cad_foundation_preset_contains_the_first_ten_visible_items(self) -> None:
        from core.training.queue_runner import CAD_FOUNDATION_FIRST_10, build_training_queue

        queue = build_training_queue(self.training_programs(), preset="cad-foundation-first-10")

        self.assertEqual(CAD_FOUNDATION_FIRST_10, [item["capabilityId"] for item in queue["items"]])
        self.assertEqual(queue["items"][0]["name"], "基础图元绘制")
        self.assertEqual(queue["items"][9]["name"], "捕捉与正交极轴")
        self.assertTrue(all(item["status"] == "pending" for item in queue["items"]))

    def test_first_supervised_step_writes_state_and_pauses_for_human_review(self) -> None:
        from core.training.queue_runner import run_training_queue_step

        with temporary_artifact_dir("training_queue") as root:
            state_path = root / "queue_state.json"

            report = run_training_queue_step(self.training_programs(), state_path=state_path)

            self.assertEqual(report["status"], "paused_for_human")
            self.assertEqual(report["currentItem"]["capabilityId"], "cad-primitives")
            self.assertIn("请在 Codex 对话框", report["humanMessage"])
            self.assertIn("基础图元绘制", report["humanMessage"])
            self.assertIn("--decision pass", report["nextCommand"])
            self.assertTrue(state_path.is_file())

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "paused_for_human")
            self.assertEqual(state["currentIndex"], 0)
            self.assertEqual(state["items"][0]["status"], "paused_for_human")
            self.assertIn("reviewChecklist", state["items"][0])

    def test_passing_current_item_advances_to_next_pending_item(self) -> None:
        from core.training.queue_runner import run_training_queue_step

        with temporary_artifact_dir("training_queue") as root:
            state_path = root / "queue_state.json"
            run_training_queue_step(self.training_programs(), state_path=state_path)

            report = run_training_queue_step(
                self.training_programs(),
                state_path=state_path,
                decision="pass",
                feedback="基础图元落图和回读检查通过。",
            )

            self.assertEqual(report["status"], "paused_for_human")
            self.assertEqual(report["currentItem"]["capabilityId"], "cad-selection-edit")
            self.assertIn("选择与基础编辑", report["humanMessage"])

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["currentIndex"], 1)
            self.assertEqual(state["items"][0]["status"], "completed")
            self.assertEqual(state["items"][0]["decision"], "pass")
            self.assertEqual(state["items"][1]["status"], "paused_for_human")

    def test_failing_current_item_blocks_queue_with_feedback_prompt(self) -> None:
        from core.training.queue_runner import run_training_queue_step

        with temporary_artifact_dir("training_queue") as root:
            state_path = root / "queue_state.json"
            run_training_queue_step(self.training_programs(), state_path=state_path)

            report = run_training_queue_step(
                self.training_programs(),
                state_path=state_path,
                decision="fail",
                feedback="圆和矩形位置不对。",
            )

            self.assertEqual(report["status"], "blocked")
            self.assertIn("圆和矩形位置不对", report["humanMessage"])
            self.assertIn("记反馈", report["humanMessage"])

            state = json.loads(state_path.read_text(encoding="utf-8"))
            self.assertEqual(state["status"], "blocked")
            self.assertEqual(state["items"][0]["status"], "blocked")
            self.assertEqual(state["items"][0]["decision"], "fail")

    def test_training_queue_cli_writes_json_report(self) -> None:
        with temporary_artifact_dir("training_queue_cli") as root:
            state_path = root / "queue_state.json"
            command = [
                sys.executable,
                str(PROJECT_ROOT / "scripts" / "run_training_queue.py"),
                "--state",
                str(state_path),
            ]

            completed = subprocess.run(
                command,
                cwd=PROJECT_ROOT,
                text=True,
                encoding="utf-8",
                errors="replace",
                capture_output=True,
            )

            self.assertEqual(completed.returncode, 0, completed.stderr)
            report = json.loads(completed.stdout)
            self.assertEqual(report["status"], "paused_for_human")
            self.assertEqual(report["currentItem"]["capabilityId"], "cad-primitives")
            self.assertTrue(state_path.is_file())

    def test_training_queue_runs_post_sync_after_pass_decision(self) -> None:
        from core.training.queue_runner import run_training_queue_step
        from scripts.run_training_queue import run_training_queue

        with temporary_artifact_dir("training_queue_post_sync") as root:
            state_path = root / "queue_state.json"
            run_training_queue_step(self.training_programs(), state_path=state_path)
            calls: list[dict] = []

            def sync_func(**kwargs: object) -> dict:
                calls.append(dict(kwargs))
                return {"status": "pass", "agent_check": {"status": "pass"}}

            report = run_training_queue(
                state_path=state_path,
                preset="cad-foundation-first-10",
                mode="supervised",
                decision="pass",
                feedback="本项通过。",
                reset=False,
                post_sync=True,
                sync_func=sync_func,
            )

            self.assertEqual(report["status"], "paused_for_human")
            self.assertEqual(report["postTrainingSync"]["status"], "pass")
            self.assertEqual(len(calls), 1)
            self.assertTrue(calls[0]["skip_coverage"])

    def test_training_queue_runs_artifact_retention_after_post_sync_pass(self) -> None:
        from core.training.queue_runner import run_training_queue_step
        from scripts.run_training_queue import run_training_queue

        with temporary_artifact_dir("training_queue_artifact_retention") as root:
            state_path = root / "queue_state.json"
            run_training_queue_step(self.training_programs(), state_path=state_path)
            retention_calls: list[dict] = []

            def sync_func(**kwargs: object) -> dict:
                return {"status": "pass", "agent_check": {"status": "pass"}}

            def artifact_retention_func(**kwargs: object) -> dict:
                retention_calls.append(dict(kwargs))
                return {
                    "status": "pass",
                    "write": False,
                    "archivePlannedCount": 2,
                    "archivedCount": 0,
                }

            report = run_training_queue(
                state_path=state_path,
                preset="cad-foundation-first-10",
                mode="supervised",
                decision="pass",
                feedback="本项通过。",
                reset=False,
                post_sync=True,
                sync_func=sync_func,
                artifact_retention_func=artifact_retention_func,
            )

            self.assertEqual(report["postTrainingArtifactRetention"]["status"], "pass")
            self.assertEqual(report["postTrainingArtifactRetention"]["archivePlannedCount"], 2)
            self.assertEqual(len(retention_calls), 1)
            self.assertFalse(retention_calls[0]["write"])

    def test_training_queue_runs_full_post_sync_when_queue_completes(self) -> None:
        from core.training.queue_runner import build_training_queue, write_queue_state
        from scripts.run_training_queue import run_training_queue

        with temporary_artifact_dir("training_queue_final_sync") as root:
            state_path = root / "queue_state.json"
            state = build_training_queue(self.training_programs(), preset="cad-foundation-first-10")
            for item in state["items"][:-1]:
                item["status"] = "completed"
                item["decision"] = "pass"
            state["currentIndex"] = len(state["items"]) - 1
            state["status"] = "paused_for_human"
            state["items"][-1]["status"] = "paused_for_human"
            write_queue_state(state_path, state)
            calls: list[dict] = []

            def sync_func(**kwargs: object) -> dict:
                calls.append(dict(kwargs))
                return {"status": "pass", "agent_check": {"status": "pass"}}

            report = run_training_queue(
                state_path=state_path,
                preset="cad-foundation-first-10",
                mode="supervised",
                decision="pass",
                feedback="全部通过。",
                reset=False,
                post_sync=True,
                sync_func=sync_func,
            )

            self.assertEqual(report["status"], "completed")
            self.assertEqual(report["postTrainingSync"]["status"], "pass")
            self.assertEqual(len(calls), 1)
            self.assertFalse(calls[0]["skip_coverage"])


if __name__ == "__main__":
    unittest.main()
