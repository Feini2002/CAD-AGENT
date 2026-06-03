from __future__ import annotations

import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from tests.helpers import temporary_artifact_dir


class StrictBlockScaleDriver:
    def __init__(self) -> None:
        from core.verification.fake_cad_driver import FakeCadDriver

        self._driver = FakeCadDriver()

    def __getattr__(self, name: str):
        return getattr(self._driver, name)

    def insert_block_alpha(self, **kwargs):
        scale = list(kwargs.get("scale") or [1, 1, 1])
        if not (len(scale) == 3 and scale[0] == scale[1] == scale[2]):
            raise ValueError("insert_block_alpha alpha only supports uniform scale.")
        return self._driver.insert_block_alpha(**kwargs)


class RecordingHatchDriver:
    def __init__(self) -> None:
        from core.verification.fake_cad_driver import FakeCadDriver

        self._driver = FakeCadDriver()
        self.hatches: list[dict] = []

    def __getattr__(self, name: str):
        return getattr(self._driver, name)

    def draw_hatch(self, **kwargs):
        self.hatches.append(dict(kwargs))
        return self._driver.draw_hatch(**kwargs)


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += float(seconds)


class LaggingDrawDriver:
    def __init__(self, clock: FakeClock, lag_seconds: float) -> None:
        from core.verification.fake_cad_driver import FakeCadDriver

        self._driver = FakeCadDriver()
        self._clock = clock
        self._lag_seconds = lag_seconds
        self._lagged = False

    def __getattr__(self, name: str):
        return getattr(self._driver, name)

    def draw_rectangle(self, **kwargs):
        if not self._lagged:
            self._clock.now += self._lag_seconds
            self._lagged = True
        return self._driver.draw_rectangle(**kwargs)


class CadFoundationRemainingTrainingTests(unittest.TestCase):
    def training_programs(self) -> list[dict]:
        from scripts import build_capability_map_data

        return build_capability_map_data.build_data()["trainingPrograms"]

    def test_remaining_foundation_batch_writes_promotable_acceptance_report(self) -> None:
        from core.training.foundation_batch_training import (
            FOUNDATION_REMAINING_21_IDS,
            run_foundation_remaining_training_batch,
        )
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("cad_foundation_remaining_training") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual([item["capabilityId"] for item in report["items"]], FOUNDATION_REMAINING_21_IDS)
            self.assertEqual(report["queueId"], "cad-foundation-remaining-21")
            self.assertEqual(report["created_handle_count"], report["readback_count"])
            self.assertGreater(report["created_handle_count"], len(FOUNDATION_REMAINING_21_IDS))
            self.assertEqual(report["missing_handles"], [])
            self.assertEqual(report["visual_self_check"]["status"], "pass")

            checks = {check["name"]: check for check in report["checks"]}
            self.assertEqual(checks["all_items_generated"]["status"], "pass")
            self.assertEqual(checks["persistent_handle_readback"]["status"], "pass")
            self.assertEqual(checks["preview_layer_only"]["status"], "pass")
            self.assertEqual(checks["dwg_not_saved"]["status"], "pass")
            self.assertEqual(checks["chinese_labels"]["status"], "pass")
            self.assertIn("latin_terms=0", checks["chinese_labels"]["message"])

            for artifact_name in ("training_plan", "dry_run", "execution_summary", "report"):
                artifact_path = root / report["artifacts"][artifact_name]
                self.assertTrue(artifact_path.is_file(), artifact_path)

            report_path = root / report["artifacts"]["report"]
            persisted = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(persisted["items"][0]["capabilityId"], "cad-polyline-width-cleanup")
            self.assertEqual(persisted["items"][-1]["capabilityId"], "cad-safe-undo-rollback")

    def test_block_training_panels_use_uniform_block_scale(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch

        with temporary_artifact_dir("cad_foundation_remaining_uniform_scale") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=StrictBlockScaleDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
            )

            self.assertEqual(report["status"], "pass", report.get("blockedReason"))

    def test_streaming_mode_is_disabled_by_default_for_remaining_batch(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.verification.fake_cad_driver import FakeCadDriver

        sleeps: list[float] = []
        with temporary_artifact_dir("cad_foundation_remaining_streaming_disabled") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
                sleep_fn=sleeps.append,
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertFalse(report["streamingMode"]["enabled"])
            self.assertEqual(report["streamingMode"]["event_count"], 0)
            self.assertEqual(sleeps, [])

    def test_run_remaining_training_accepts_stream_demo_config(self) -> None:
        from scripts.run_cad_foundation_remaining_training import run_remaining_training

        sleeps: list[float] = []
        with temporary_artifact_dir("cad_foundation_remaining_streaming_cli") as root:
            report = run_remaining_training(
                output_dir=root,
                fake_cad=True,
                timeout_seconds=30,
                post_sync=False,
                capture_preview=False,
                stream_demo=True,
                stream_item_delay_seconds=0.3,
                stream_operation_delay_seconds=0.05,
                stream_operation_budget=1,
                stream_zoom_each_item=True,
                sleep_fn=sleeps.append,
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["postTrainingSync"]["status"], "skipped")
            streaming = report["streamingMode"]
            self.assertTrue(streaming["enabled"])
            self.assertEqual(streaming["itemDelaySeconds"], 0.3)
            self.assertEqual(streaming["operationDelaySeconds"], 0.05)
            self.assertEqual(streaming["operationBudgetPerItem"], 1)
            self.assertIn(0.3, sleeps)
            self.assertIn(0.05, sleeps)

    def test_run_remaining_training_runs_artifact_retention_after_full_pass_sync(self) -> None:
        from scripts.run_cad_foundation_remaining_training import run_remaining_training

        sync_calls: list[dict] = []
        retention_calls: list[dict] = []

        def sync_func(**kwargs: object) -> dict:
            sync_calls.append(dict(kwargs))
            return {"status": "pass", "agent_check": {"status": "pass"}}

        def artifact_retention_func(**kwargs: object) -> dict:
            retention_calls.append(dict(kwargs))
            return {
                "status": "pass",
                "write": False,
                "archivePlannedCount": 3,
                "archivedCount": 0,
            }

        with temporary_artifact_dir("cad_foundation_remaining_retention") as root:
            report = run_remaining_training(
                output_dir=root,
                fake_cad=True,
                timeout_seconds=30,
                post_sync=True,
                capture_preview=False,
                sync_func=sync_func,
                artifact_retention_func=artifact_retention_func,
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["postTrainingSync"]["status"], "pass")
            self.assertEqual(report["postTrainingArtifactRetention"]["status"], "pass")
            self.assertEqual(report["postTrainingArtifactRetention"]["archivePlannedCount"], 3)
            self.assertEqual(len(sync_calls), 1)
            self.assertEqual(len(retention_calls), 1)
            self.assertFalse(retention_calls[0]["write"])

    @patch("core.training.foundation_batch_training.prepare_autocad_for_capture", create=True)
    def test_capture_preview_records_task_scoped_visual_preview_payload(self, mock_capture) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.verification.fake_cad_driver import FakeCadDriver

        def capture(output: Path, **kwargs: object) -> dict[str, object]:
            output.write_bytes(b"fake-png")
            return {
                "status": "captured",
                "output": str(output),
                "mode": "autocad_window_printwindow",
                "occlusion_safe": True,
                "focus": {"status": "zoomed_to_bbox", "source": "execution_summary.created_handles", "handle_count": 4},
            }

        mock_capture.side_effect = capture

        with temporary_artifact_dir("cad_foundation_remaining_task_scoped_preview") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=True,
                selected_capability_ids=["cad-array-copy-pattern"],
                scope_reason="用户只修复 10 项中的 1 项，需要精准截图当前项",
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["visualPreview"]["role"], "visual_aid_only")
            self.assertEqual(report["visualPreview"]["status"], "captured")
            self.assertEqual(report["visualPreview"]["focus"]["source"], "execution_summary.created_handles")
            self.assertEqual(report["screenshotDecision"]["focusSource"], "execution_summary.created_handles")
            self.assertTrue(report["screenshotDecision"]["shouldCapture"])
            self.assertTrue(report["visualPreview"]["screenshotDecision"]["visualAidOnly"])
            self.assertTrue((root / report["visual_self_check"]["preview_path"]).is_file())
            mock_capture.assert_called_once()
            self.assertTrue(mock_capture.call_args.kwargs["execution_summary"].is_file())

    def test_hybrid_streaming_mode_records_item_operation_and_zoom_events_for_remaining_batch(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.training.streaming_demo import StreamingCadDemoConfig
        from core.verification.fake_cad_driver import FakeCadDriver

        sleeps: list[float] = []
        with temporary_artifact_dir("cad_foundation_remaining_streaming_hybrid") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
                streaming_config=StreamingCadDemoConfig.hybrid(
                    item_delay_seconds=0.4,
                    operation_delay_seconds=0.1,
                    operation_budget_per_item=2,
                    zoom_each_item=True,
                ),
                sleep_fn=sleeps.append,
            )

            self.assertEqual(report["status"], "pass", report)
            streaming = report["streamingMode"]
            self.assertTrue(streaming["enabled"])
            self.assertEqual(streaming["mode"], "hybrid")
            self.assertEqual(streaming["item_delay_count"], 21)
            self.assertGreaterEqual(streaming["operation_delay_count"], 21)
            self.assertIn(0.4, sleeps)
            self.assertIn(0.1, sleeps)
            self.assertEqual(report["created_handle_count"], report["readback_count"])

            item_complete_events = [event for event in streaming["events"] if event["event"] == "item_complete"]
            self.assertEqual(len(item_complete_events), 21)
            self.assertTrue(
                all(event["zoom"]["status"] == "zoomed_to_handles" for event in item_complete_events),
                item_complete_events,
            )
            persisted_report = json.loads((root / report["artifacts"]["report"]).read_text(encoding="utf-8"))
            persisted_summary = json.loads((root / report["artifacts"]["execution_summary"]).read_text(encoding="utf-8"))
            self.assertTrue(persisted_report["streamingMode"]["enabled"])
            self.assertTrue(persisted_summary["streamingMode"]["enabled"])
            self.assertGreater(persisted_report["streamingMode"]["event_count"], 0)
            self.assertGreater(persisted_summary["streamingMode"]["event_count"], 0)
            self.assertIn("delaySecondsTotal", persisted_report["streamingMode"])
            self.assertIn("delaySecondsTotal", persisted_summary["streamingMode"])
            draw_steps = [step for step in persisted_summary["watchdog"] if step["step"].startswith("draw:")]
            self.assertTrue(draw_steps)
            self.assertTrue(all("demoDelaySeconds" in step for step in draw_steps))
            self.assertTrue(all("netElapsedSeconds" in step for step in draw_steps))

    def test_operation_demo_delay_does_not_trip_draw_watchdog(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.training.streaming_demo import StreamingCadDemoConfig
        from core.verification.fake_cad_driver import FakeCadDriver

        clock = FakeClock()
        with temporary_artifact_dir("cad_foundation_remaining_streaming_watchdog") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                timeout_seconds=1,
                capture_preview=False,
                selected_capability_ids=["cad-array-copy-pattern"],
                scope_reason="focused streaming watchdog regression",
                streaming_config=StreamingCadDemoConfig.hybrid(
                    item_delay_seconds=0.0,
                    operation_delay_seconds=2.0,
                    operation_budget_per_item=1,
                    zoom_each_item=False,
                ),
                sleep_fn=clock.sleep,
                clock_fn=clock.monotonic,
            )

            self.assertEqual(report["status"], "pass", report)
            draw_steps = [step for step in report["watchdog"] if step["step"] == "draw:cad-array-copy-pattern"]
            self.assertEqual(len(draw_steps), 1)
            self.assertEqual(draw_steps[0]["demoDelaySeconds"], 2.0)
            self.assertLessEqual(draw_steps[0]["netElapsedSeconds"], draw_steps[0]["elapsedSeconds"])
            self.assertEqual(draw_steps[0]["status"], "pass")

    def test_streaming_delays_are_recorded_without_changing_watchdog_success(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.training.streaming_demo import StreamingCadDemoConfig
        from core.verification.fake_cad_driver import FakeCadDriver

        sleeps: list[float] = []
        with temporary_artifact_dir("cad_foundation_remaining_streaming_zero_delay") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                timeout_seconds=30,
                capture_preview=False,
                streaming_config=StreamingCadDemoConfig.hybrid(
                    item_delay_seconds=0.0,
                    operation_delay_seconds=0.0,
                    operation_budget_per_item=2,
                    zoom_each_item=False,
                ),
                sleep_fn=sleeps.append,
            )

            self.assertEqual(report["status"], "pass", report)
            streaming = report["streamingMode"]
            self.assertTrue(streaming["enabled"])
            self.assertEqual(streaming["operation_delay_count"], 0)
            self.assertEqual(streaming["item_delay_count"], 0)

            checks = {check["name"]: check for check in report["checks"]}
            self.assertEqual(checks["watchdog_no_timeout"]["status"], "pass")
            self.assertEqual(checks["streaming_demo_mode"]["status"], "pass")
            self.assertIn("streaming_events=", checks["streaming_demo_mode"]["message"])
            self.assertEqual(sleeps, [])

    def test_real_draw_time_still_times_out_after_measured_demo_delay_is_subtracted(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.training.streaming_demo import StreamingCadDemoConfig

        clock = FakeClock()
        with temporary_artifact_dir("cad_foundation_remaining_streaming_real_timeout") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=LaggingDrawDriver(clock, lag_seconds=2.5),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                timeout_seconds=1,
                capture_preview=False,
                selected_capability_ids=["cad-array-copy-pattern"],
                scope_reason="focused streaming true timeout regression",
                streaming_config=StreamingCadDemoConfig.hybrid(
                    item_delay_seconds=0.0,
                    operation_delay_seconds=2.0,
                    operation_budget_per_item=1,
                    zoom_each_item=False,
                ),
                sleep_fn=clock.sleep,
                clock_fn=clock.monotonic,
            )

            self.assertEqual(report["status"], "blocked", report)
            checks = {check["name"]: check for check in report["checks"]}
            self.assertEqual(checks["watchdog_no_timeout"]["status"], "fail")
            draw_steps = [step for step in report["watchdog"] if step["step"] == "draw:cad-array-copy-pattern"]
            self.assertEqual(len(draw_steps), 1)
            self.assertEqual(draw_steps[0]["demoDelaySeconds"], 2.0)
            self.assertGreater(draw_steps[0]["netElapsedSeconds"], 1.0)
            self.assertEqual(draw_steps[0]["status"], "timeout")

    def test_remaining_foundation_visible_labels_do_not_mix_english_terms(self) -> None:
        from core.safety.policy import PREVIEW_LAYER
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.verification.fake_cad_driver import FakeCadDriver

        driver = FakeCadDriver()
        with temporary_artifact_dir("cad_foundation_remaining_chinese_labels") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=driver,
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
            )

            self.assertEqual(report["status"], "pass", report)
            text_values = [
                str(entity.get("text", ""))
                for entity in driver.snapshot_modelspace(layer=PREVIEW_LAYER)
                if entity.get("type") == "text"
            ]
            text_values.extend(str(item.get("title", "")) for item in report["items"])
            offenders = {
                text: re.findall(r"[A-Za-z]{2,}(?:[-_/][A-Za-z0-9]+)?", text)
                for text in text_values
                if re.search(r"[A-Za-z]{2,}", text)
            }
            self.assertEqual(offenders, {}, offenders)

    def test_retraining_uses_moved_previous_handles_as_parking_anchor(self) -> None:
        from core.safety.policy import PREVIEW_LAYER
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.verification.fake_cad_driver import FakeCadDriver

        def move_entity(entity, dx: float, dy: float) -> None:
            for attr in ("StartPoint", "EndPoint", "InsertionPoint", "Center"):
                point = getattr(entity, attr, None)
                if isinstance(point, list) and len(point) >= 2:
                    point[0] = float(point[0]) + dx
                    point[1] = float(point[1]) + dy
            coordinates = getattr(entity, "Coordinates", None)
            if isinstance(coordinates, list):
                for index in range(0, len(coordinates), 2):
                    coordinates[index] = float(coordinates[index]) + dx
                    coordinates[index + 1] = float(coordinates[index + 1]) + dy
            bbox = getattr(entity, "bbox", None)
            if isinstance(bbox, dict):
                bbox["min"][0] = float(bbox["min"][0]) + dx
                bbox["min"][1] = float(bbox["min"][1]) + dy
                bbox["max"][0] = float(bbox["max"][0]) + dx
                bbox["max"][1] = float(bbox["max"][1]) + dy

        driver = FakeCadDriver()
        with temporary_artifact_dir("cad_foundation_remaining_parking_anchor") as root:
            first_report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=driver,
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
            )
            first_handles = json.loads((root / first_report["artifacts"]["execution_summary"]).read_text(encoding="utf-8"))[
                "created_handles"
            ]
            for handle in first_handles:
                move_entity(driver.entities[handle], 10000.0, 2000.0)

            driver.draw_rectangle(
                corner1=[90000.0, 5000.0, 0.0],
                corner2=[91000.0, 4000.0, 0.0],
                layer=PREVIEW_LAYER,
            )
            second_report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=driver,
                output_dir=root,
                generated_at="2026-06-01T00:01:00Z",
                capture_preview=False,
            )

            self.assertEqual(second_report["status"], "pass", second_report)
            self.assertEqual(second_report["parking_anchor"]["source"], "previous_handles")
            self.assertLess(second_report["batch_bbox"]["min"][0], 30000.0)

    def test_hatch_boundary_training_uses_common_patterns_and_scale_comparison(self) -> None:
        from core.training.foundation_panel_drawings import draw_foundation_item

        program = next(item for item in self.training_programs() if item["capabilityId"] == "cad-hatch-boundary")
        driver = RecordingHatchDriver()
        draw_foundation_item(driver, program, 1, [0.0, 0.0, 0.0])

        self.assertGreaterEqual(len(driver.hatches), 6)
        self.assertLessEqual(len(driver.hatches), 10)
        patterns = {str(hatch.get("pattern")) for hatch in driver.hatches}
        self.assertGreaterEqual({"ANSI31", "ANSI32", "ANSI37", "AR-CONC", "BRICK", "GRAVEL", "EARTH"}, patterns)
        ansi31_scales = sorted(float(hatch.get("scale", 1.0)) for hatch in driver.hatches if hatch.get("pattern") == "ANSI31")
        self.assertGreaterEqual(len(set(ansi31_scales)), 2)

    def test_lineweight_standard_draws_distinct_lineweights_and_linetypes(self) -> None:
        from core.safety.policy import PREVIEW_LAYER
        from core.training.foundation_panel_drawings import draw_foundation_item
        from core.verification.fake_cad_driver import FakeCadDriver

        program = next(item for item in self.training_programs() if item["capabilityId"] == "cad-layer-lineweight-standard")
        driver = FakeCadDriver()
        handles = draw_foundation_item(driver, program, 11, [0.0, 0.0, 0.0])

        entities = driver.snapshot_handles(handles=handles, layer=PREVIEW_LAYER)
        styled_lines = [
            entity
            for entity in entities
            if entity.get("type") == "line" and "lineweight" in entity and "linetype" in entity
        ]

        self.assertEqual(len(styled_lines), 3, styled_lines)
        self.assertEqual({int(entity["lineweight"]) for entity in styled_lines}, {70, 35, 13})
        self.assertEqual({str(entity["linetype"]).upper() for entity in styled_lines}, {"CONTINUOUS", "CENTER", "DASHED"})
        patterned_scales = {
            float(entity["linetype_scale"])
            for entity in styled_lines
            if str(entity["linetype"]).upper() in {"CENTER", "DASHED"}
        }
        self.assertEqual(patterned_scales, {25.0})

    def test_focused_lineweight_standard_report_records_style_evidence(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("cad_foundation_focused_lineweight_standard") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
                selected_capability_ids=["cad-layer-lineweight-standard"],
                scope_reason="用户反馈任务 22 线宽线型没有真实变化，旁边 focused 加强训练",
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["scope"]["mode"], "focused")
            self.assertEqual([item["capabilityId"] for item in report["items"]], ["cad-layer-lineweight-standard"])

            style_evidence = report["items"][0].get("styleEvidence", {})
            self.assertEqual(style_evidence.get("status"), "pass", style_evidence)
            self.assertEqual(style_evidence.get("lineweights"), [13, 35, 70])
            self.assertEqual(style_evidence.get("linetypes"), ["CENTER", "CONTINUOUS", "DASHED"])
            self.assertEqual(style_evidence.get("linetypeScales"), [1.0, 25.0])

            checks = {check["name"]: check for check in report["checks"]}
            self.assertEqual(checks["lineweight_linetype_standard"]["status"], "pass")

    def test_focused_retraining_only_generates_requested_foundation_item(self) -> None:
        from core.training.foundation_batch_training import run_foundation_remaining_training_batch
        from core.verification.fake_cad_driver import FakeCadDriver

        with temporary_artifact_dir("cad_foundation_focused_hatch") as root:
            report = run_foundation_remaining_training_batch(
                programs=self.training_programs(),
                driver=FakeCadDriver(),
                output_dir=root,
                generated_at="2026-06-01T00:00:00Z",
                capture_preview=False,
                selected_capability_ids=["cad-hatch-boundary"],
                scope_reason="用户点名任务 12 加深训练",
            )

            self.assertEqual(report["status"], "pass", report)
            self.assertEqual(report["scope"]["mode"], "focused")
            self.assertEqual(report["scope"]["requestedCapabilityIds"], ["cad-hatch-boundary"])
            self.assertEqual([item["capabilityId"] for item in report["items"]], ["cad-hatch-boundary"])
            self.assertEqual(report["items"][0]["title"], "12 填充与边界")

            checks = {check["name"]: check for check in report["checks"]}
            self.assertEqual(checks["all_items_generated"]["status"], "pass")
            self.assertEqual(checks["all_items_generated"]["message"], "1/1")

            queue_state = json.loads((root.parent / "queue_state.json").read_text(encoding="utf-8"))
            self.assertEqual(queue_state["mode"], "focused")
            self.assertEqual(queue_state["totalCount"], 1)

    def test_hatch_pattern_focus_limits_training_to_requested_pattern_and_scales(self) -> None:
        from core.training.foundation_panel_drawings import draw_foundation_item

        program = next(item for item in self.training_programs() if item["capabilityId"] == "cad-hatch-boundary")
        driver = RecordingHatchDriver()
        draw_foundation_item(
            driver,
            program,
            1,
            [0.0, 0.0, 0.0],
            options={"hatch_pattern_focus": "ANSI31", "hatch_scales": [0.25, 0.5, 1.0, 2.0]},
        )

        self.assertEqual(len(driver.hatches), 4)
        self.assertEqual({str(hatch.get("pattern")) for hatch in driver.hatches}, {"ANSI31"})
        self.assertEqual([float(hatch.get("scale")) for hatch in driver.hatches], [0.25, 0.5, 1.0, 2.0])

    def test_hatch_full_fill_focus_uses_solid_samples_and_labels(self) -> None:
        from core.safety.policy import PREVIEW_LAYER
        from core.training.foundation_panel_drawings import draw_foundation_item

        program = next(item for item in self.training_programs() if item["capabilityId"] == "cad-hatch-boundary")
        driver = RecordingHatchDriver()
        draw_foundation_item(
            driver,
            program,
            1,
            [0.0, 0.0, 0.0],
            options={"hatch_full_fill": True},
        )

        self.assertGreaterEqual(len(driver.hatches), 4)
        self.assertEqual({str(hatch.get("pattern", "")).upper() for hatch in driver.hatches}, {"SOLID"})
        self.assertEqual({float(hatch.get("scale", 1.0)) for hatch in driver.hatches}, {1.0})

        text_values = [
            str(entity.get("text", ""))
            for entity in driver.snapshot_modelspace(layer=PREVIEW_LAYER)
            if entity.get("type") == "text"
        ]
        self.assertTrue(any("全填充" in text for text in text_values), text_values)

        text_positions = [
            (str(entity.get("text", "")), entity.get("position", []))
            for entity in driver.snapshot_modelspace(layer=PREVIEW_LAYER)
            if entity.get("type") == "text"
        ]
        full_fill_label_ys = [
            float(position[1])
            for text, position in text_positions
            if "全填充" in text and isinstance(position, list) and len(position) >= 2
        ]
        check_label_y = next(
            float(position[1])
            for text, position in text_positions
            if text.startswith("已检查") and isinstance(position, list) and len(position) >= 2
        )
        self.assertGreaterEqual(min(full_fill_label_ys) - check_label_y, 90.0)


if __name__ == "__main__":
    unittest.main()
