import unittest

from core.safety.policy import PREVIEW_LAYER
from core.training.foundation_panel_drawings import draw_foundation_item
from core.training.streaming_demo import (
    StreamingCadDemoConfig,
    StreamingCadDemoRecorder,
)
from core.verification.fake_cad_driver import FakeCadDriver


class ZoomRecordingDriver:
    def __init__(self) -> None:
        self.refresh_count = 0
        self.zoom_calls: list[dict] = []

    def refresh_view(self) -> None:
        self.refresh_count += 1

    def zoom_to_handles(self, *, handles, layer, padding_ratio):
        self.zoom_calls.append(
            {
                "handles": list(handles),
                "layer": layer,
                "padding_ratio": padding_ratio,
            }
        )
        return {"status": "zoomed_to_handles"}


class FailingStreamingDriver:
    def refresh_view(self) -> None:
        raise RuntimeError("refresh exploded")

    def zoom_to_handles(self, handles, *, layer, padding_ratio):
        raise RuntimeError("zoom exploded")


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += float(seconds)


class BatchCountingDriver(FakeCadDriver):
    def __init__(self) -> None:
        super().__init__()
        self.batch_calls = 0
        self.primitive_calls_outside_batch = 0
        self._inside_batch = False

    def execute_operation_batch(self, operations, *, layer=PREVIEW_LAYER, batch_name=""):
        self.batch_calls += 1
        self._inside_batch = True
        try:
            return super().execute_operation_batch(
                operations,
                layer=layer,
                batch_name=batch_name,
            )
        finally:
            self._inside_batch = False

    def _count_outside_batch(self) -> None:
        if not self._inside_batch:
            self.primitive_calls_outside_batch += 1

    def draw_line(self, **kwargs):
        self._count_outside_batch()
        return super().draw_line(**kwargs)

    def draw_rectangle(self, **kwargs):
        self._count_outside_batch()
        return super().draw_rectangle(**kwargs)

    def draw_circle(self, **kwargs):
        self._count_outside_batch()
        return super().draw_circle(**kwargs)

    def draw_arc(self, **kwargs):
        self._count_outside_batch()
        return super().draw_arc(**kwargs)

    def draw_polyline(self, **kwargs):
        self._count_outside_batch()
        return super().draw_polyline(**kwargs)

    def draw_text(self, **kwargs):
        self._count_outside_batch()
        return super().draw_text(**kwargs)

    def add_dimension(self, **kwargs):
        self._count_outside_batch()
        return super().add_dimension(**kwargs)

    def draw_hatch(self, **kwargs):
        self._count_outside_batch()
        return super().draw_hatch(**kwargs)


class StreamingCadDemoTests(unittest.TestCase):
    def test_fake_cad_driver_exposes_streaming_view_hooks(self) -> None:
        driver = FakeCadDriver()
        handle = driver.draw_circle(center=[10, 20, 0], radius=5, layer=PREVIEW_LAYER)[
            "handle"
        ]

        refresh = driver.refresh_view()
        zoom = driver.zoom_to_handles(
            handles=[handle],
            layer=PREVIEW_LAYER,
            padding_ratio=0.2,
        )

        self.assertEqual(refresh["status"], "pass")
        self.assertEqual(zoom["status"], "zoomed_to_handles")
        self.assertEqual(zoom["handle_count"], 1)
        self.assertEqual(zoom["layer"], PREVIEW_LAYER)

    def test_foundation_panel_drawer_records_streamed_operations_with_budget(self) -> None:
        sleeps: list[float] = []
        driver = FakeCadDriver()
        recorder = StreamingCadDemoRecorder(
            StreamingCadDemoConfig.hybrid(
                item_delay_seconds=0.0,
                operation_delay_seconds=0.2,
                operation_budget_per_item=3,
                zoom_each_item=False,
            ),
            driver=driver,
            sleep_fn=sleeps.append,
        )
        program = {
            "capabilityId": "cad-array-copy-pattern",
            "name": "array copy pattern",
            "focus": "array",
        }

        handles = draw_foundation_item(
            driver,
            program,
            3,
            [0.0, 0.0, 0.0],
            streaming_recorder=recorder,
        )

        summary = recorder.summary()
        operation_events = [
            event for event in summary["events"] if event["event"] == "operation"
        ]
        delayed_events = [event for event in operation_events if event["delayed"]]
        self.assertGreater(len(handles), 3)
        self.assertEqual(sleeps, [0.2, 0.2, 0.2])
        self.assertGreaterEqual(len(operation_events), 5)
        self.assertEqual(len(delayed_events), 3)
        self.assertEqual(delayed_events[0]["operation"], "rect")

    def test_foundation_panel_uses_one_batch_submission_per_item(self) -> None:
        driver = BatchCountingDriver()
        program = {
            "capabilityId": "cad-array-copy-pattern",
            "name": "阵列复制",
            "focus": "array",
        }

        handles = draw_foundation_item(
            driver,
            program,
            3,
            [0.0, 0.0, 0.0],
        )

        self.assertGreater(len(handles), 3)
        self.assertEqual(driver.batch_calls, 1)
        self.assertEqual(driver.primitive_calls_outside_batch, 0)

    def test_disabled_config_records_no_sleep_zoom_or_refresh(self) -> None:
        sleeps: list[float] = []
        driver = ZoomRecordingDriver()
        recorder = StreamingCadDemoRecorder(
            StreamingCadDemoConfig.disabled(),
            driver=driver,
            sleep_fn=sleeps.append,
        )

        recorder.start_item("foundation-line")
        recorder.after_operation("line", ["L1"])
        recorder.after_item(["L1"])

        summary = recorder.summary()
        self.assertFalse(summary["enabled"])
        self.assertEqual(summary["event_count"], 0)
        self.assertEqual(sleeps, [])
        self.assertEqual(driver.refresh_count, 0)
        self.assertEqual(driver.zoom_calls, [])

    def test_hybrid_config_delays_only_within_operation_budget(self) -> None:
        clock = FakeClock()
        driver = ZoomRecordingDriver()
        recorder = StreamingCadDemoRecorder(
            StreamingCadDemoConfig.hybrid(
                item_delay_seconds=0.5,
                operation_delay_seconds=0.2,
                operation_budget_per_item=2,
                zoom_each_item=False,
            ),
            driver=driver,
            sleep_fn=clock.sleep,
            clock_fn=clock.monotonic,
        )

        recorder.start_item("streaming-room")
        recorder.after_operation("circle", ["C1"])
        recorder.after_operation("circle", ["C2"])
        recorder.after_operation("circle", ["C1"])
        recorder.after_operation("hatch", ["H1"])
        recorder.after_item(["R1", "L1", "C1", "H1"])

        summary = recorder.summary()
        self.assertEqual(summary["event_count"], 6)
        self.assertEqual(summary["operation_delay_count"], 2)
        self.assertEqual(summary["item_delay_count"], 1)
        self.assertEqual(summary["operationDelaySecondsTotal"], 0.4)
        self.assertEqual(summary["itemDelaySecondsTotal"], 0.5)
        self.assertEqual(summary["delaySecondsTotal"], 0.9)
        self.assertEqual(summary["delayTelemetryBasis"], "measured_sleep")
        operation_events = [
            event for event in summary["events"] if event["event"] == "operation"
        ]
        self.assertEqual([event["actualDelaySeconds"] for event in operation_events], [0.2, 0.2, 0.0, 0.0])
        self.assertEqual([event["delayed"] for event in operation_events], [True, True, False, False])
        self.assertEqual(operation_events[0]["refresh"]["status"], "success")
        self.assertEqual(summary["refresh_count"], 3)

    def test_noop_sleep_does_not_add_measured_demo_delay(self) -> None:
        sleeps: list[float] = []
        clock = FakeClock()
        driver = ZoomRecordingDriver()
        recorder = StreamingCadDemoRecorder(
            StreamingCadDemoConfig.hybrid(
                item_delay_seconds=0.5,
                operation_delay_seconds=0.2,
                operation_budget_per_item=1,
                zoom_each_item=False,
            ),
            driver=driver,
            sleep_fn=sleeps.append,
            clock_fn=clock.monotonic,
        )

        recorder.after_operation("circle", ["C1"])
        recorder.after_item(["C1"])

        summary = recorder.summary()
        self.assertEqual(sleeps, [0.2, 0.5])
        self.assertEqual(summary["operationDelaySecondsTotal"], 0.0)
        self.assertEqual(summary["itemDelaySecondsTotal"], 0.0)
        self.assertEqual(summary["delaySecondsTotal"], 0.0)
        operation_event = next(event for event in summary["events"] if event["event"] == "operation")
        item_event = next(event for event in summary["events"] if event["event"] == "item_complete")
        self.assertEqual(operation_event["delaySeconds"], 0.2)
        self.assertEqual(operation_event["actualDelaySeconds"], 0.0)
        self.assertEqual(item_event["delaySeconds"], 0.5)
        self.assertEqual(item_event["actualDelaySeconds"], 0.0)

    def test_item_completion_zooms_to_created_handles_on_preview_layer(self) -> None:
        sleeps: list[float] = []
        driver = ZoomRecordingDriver()
        recorder = StreamingCadDemoRecorder(
            StreamingCadDemoConfig.hybrid(
                item_delay_seconds=0.1,
                operation_delay_seconds=0,
                zoom_each_item=True,
                zoom_padding_ratio=0.2,
            ),
            driver=driver,
            sleep_fn=sleeps.append,
        )

        recorder.after_item(["A1", "B2"])

        self.assertEqual(
            driver.zoom_calls,
            [
                {
                    "handles": ["A1", "B2"],
                    "layer": PREVIEW_LAYER,
                    "padding_ratio": 0.2,
                }
            ],
        )
        self.assertEqual(sleeps, [0.1])

        item_complete_events = [
            event
            for event in recorder.summary()["events"]
            if event["event"] == "item_complete"
        ]
        self.assertEqual(item_complete_events[0]["zoom"]["status"], "zoomed_to_handles")

    def test_item_completion_zooms_fake_cad_driver_handles(self) -> None:
        driver = FakeCadDriver()
        handle = driver.draw_circle(center=[10, 20, 0], radius=5, layer=PREVIEW_LAYER)[
            "handle"
        ]
        recorder = StreamingCadDemoRecorder(
            StreamingCadDemoConfig.hybrid(
                item_delay_seconds=0,
                operation_delay_seconds=0,
                zoom_each_item=True,
                zoom_padding_ratio=0.2,
            ),
            driver=driver,
        )

        recorder.after_item([handle])

        item_complete_events = [
            event
            for event in recorder.summary()["events"]
            if event["event"] == "item_complete"
        ]
        self.assertEqual(item_complete_events[0]["zoom"]["status"], "zoomed_to_handles")
        self.assertEqual(item_complete_events[0]["zoom"]["handle_count"], 1)

    def test_driver_refresh_and_zoom_failures_are_recorded_without_raising(self) -> None:
        sleeps: list[float] = []
        recorder = StreamingCadDemoRecorder(
            StreamingCadDemoConfig.hybrid(
                item_delay_seconds=0.1,
                operation_delay_seconds=0.2,
                operation_budget_per_item=1,
                zoom_each_item=True,
            ),
            driver=FailingStreamingDriver(),
            sleep_fn=sleeps.append,
        )

        recorder.after_operation("circle", ["C1"])
        recorder.after_item(["C1"])

        summary = recorder.summary()
        operation_events = [
            event for event in summary["events"] if event["event"] == "operation"
        ]
        item_complete_events = [
            event for event in summary["events"] if event["event"] == "item_complete"
        ]
        self.assertEqual(operation_events[0]["refresh"]["status"], "failed")
        self.assertIn("refresh exploded", operation_events[0]["refresh"]["error"])
        self.assertEqual(item_complete_events[0]["zoom"]["status"], "failed")
        self.assertIn("zoom exploded", item_complete_events[0]["zoom"]["error"])
        self.assertEqual(sleeps, [0.2, 0.1])


if __name__ == "__main__":
    unittest.main()
