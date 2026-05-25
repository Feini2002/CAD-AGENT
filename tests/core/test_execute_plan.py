from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.execution.execute_plan import execute_plan_file
from core.cad_io.autocad_com import AutoCADComDriver
from tests.helpers import artifact_path


class RecordingDriver:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def draw_rectangle(self, **kwargs: object) -> None:
        self.calls.append(("draw_rectangle", kwargs))

    def draw_text(self, **kwargs: object) -> None:
        self.calls.append(("draw_text", kwargs))

    def add_dimension(self, **kwargs: object) -> None:
        self.calls.append(("add_dimension", kwargs))


class HandleRecordingDriver(RecordingDriver):
    def __init__(self) -> None:
        super().__init__()
        self.next_handle = 1

    def _handle(self) -> str:
        handle = f"H{self.next_handle}"
        self.next_handle += 1
        return handle

    def draw_rectangle(self, **kwargs: object) -> dict[str, str]:
        super().draw_rectangle(**kwargs)
        return {"handle": self._handle()}

    def draw_text(self, **kwargs: object) -> dict[str, str]:
        super().draw_text(**kwargs)
        return {"handle": self._handle()}

    def add_dimension(self, **kwargs: object) -> dict[str, str]:
        super().add_dimension(**kwargs)
        return {"handle": self._handle()}


class ExecutePlanTests(unittest.TestCase):
    def test_draws_preview_cabinet_rectangle_label_and_dimensions(self) -> None:
        plan = {
            "version": "0.1",
            "domain": "generic",
            "intent": "draw_object",
            "object": {
                "type": "cabinet",
                "name": "测试柜",
                "width": 1800,
                "depth": 600,
            },
            "placement": {
                "mode": "absolute",
                "base_point": [0, 0, 0],
            },
            "drawing": {
                "layer": "CODEX_PREVIEW",
                "include_label": True,
                "include_dimensions": True,
            },
            "confidence": 1.0,
            "needs_confirmation": False,
        }

        plan_path = artifact_path("execute_plan", "plan.json")
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        driver = RecordingDriver()
        result = execute_plan_file(plan_path, driver=driver)

        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["layer"], "CODEX_PREVIEW")
        self.assertEqual(result["object_name"], "测试柜")
        self.assertEqual(result["object_size"], [1800, 600])
        self.assertEqual(
            driver.calls,
            [
                (
                    "draw_rectangle",
                    {
                        "corner1": [0, 0, 0],
                        "corner2": [1800, 600, 0],
                        "layer": "CODEX_PREVIEW",
                        "color": "yellow",
                    },
                ),
                (
                    "draw_text",
                    {
                        "text": "测试柜",
                        "position": [900, 300, 0],
                        "height": 120,
                        "layer": "CODEX_PREVIEW",
                        "color": "yellow",
                    },
                ),
                (
                    "add_dimension",
                    {
                        "start_point": [0, 0, 0],
                        "end_point": [1800, 0, 0],
                        "text_position": [900, -180, 0],
                        "layer": "CODEX_PREVIEW",
                        "color": "yellow",
                    },
                ),
                (
                    "add_dimension",
                    {
                        "start_point": [0, 0, 0],
                        "end_point": [0, 600, 0],
                        "text_position": [-180, 300, 0],
                        "layer": "CODEX_PREVIEW",
                        "color": "yellow",
                    },
                ),
            ],
        )

    def test_rejects_unconfirmed_plan_by_default(self) -> None:
        plan = {
            "version": "0.1",
            "domain": "generic",
            "intent": "draw_object",
            "object": {
                "type": "cabinet",
                "name": "Needs Review",
                "width": 1800,
                "depth": 600,
            },
            "placement": {
                "mode": "absolute",
                "base_point": [0, 0, 0],
            },
            "drawing": {
                "layer": "CODEX_PREVIEW",
                "include_label": False,
                "include_dimensions": False,
            },
            "confidence": 0.5,
            "needs_confirmation": True,
        }
        plan_path = artifact_path("execute_plan", "needs_confirmation.json")
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "needs confirmation"):
            execute_plan_file(plan_path, driver=RecordingDriver())

    def test_execution_summary_collects_created_handles_when_driver_returns_them(self) -> None:
        plan = {
            "version": "0.1",
            "domain": "generic",
            "intent": "draw_object",
            "object": {"type": "cabinet", "name": "Handle Cabinet", "width": 1800, "depth": 600},
            "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
            "drawing": {"layer": "CODEX_PREVIEW", "include_label": True, "include_dimensions": True},
            "confidence": 1.0,
            "needs_confirmation": False,
        }
        plan_path = artifact_path("execute_plan", "handles.json")
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        result = execute_plan_file(plan_path, driver=HandleRecordingDriver())

        self.assertEqual(result["created_handles"], ["H1", "H2", "H3", "H4"])

    def test_autocad_driver_methods_return_created_handles_from_com_entities(self) -> None:
        class FakeEntity:
            def __init__(self, handle: str) -> None:
                self.Handle = handle

        class FakeModelSpace:
            def __init__(self) -> None:
                self.next_handle = 1

            def _entity(self) -> FakeEntity:
                entity = FakeEntity(f"C{self.next_handle}")
                self.next_handle += 1
                return entity

            def AddLine(self, *_: object) -> FakeEntity:
                return self._entity()

            def AddText(self, *_: object) -> FakeEntity:
                return self._entity()

            def AddDimAligned(self, *_: object) -> FakeEntity:
                return self._entity()

        driver = object.__new__(AutoCADComDriver)
        driver.model_space = FakeModelSpace()
        driver._apply_common = lambda entity, **kwargs: None  # type: ignore[method-assign]

        self.assertEqual(
            driver.draw_rectangle(corner1=[0, 0, 0], corner2=[100, 50, 0]),
            {"handles": ["C1", "C2", "C3", "C4"]},
        )
        self.assertEqual(
            driver.draw_text(text="T", position=[0, 0, 0], height=10),
            {"handle": "C5"},
        )
        self.assertEqual(
            driver.add_dimension(start_point=[0, 0, 0], end_point=[100, 0, 0]),
            {"handle": "C6"},
        )


if __name__ == "__main__":
    unittest.main()
