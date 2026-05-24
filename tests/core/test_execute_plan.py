from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.execution.execute_plan import execute_plan_file


class RecordingDriver:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def draw_rectangle(self, **kwargs: object) -> None:
        self.calls.append(("draw_rectangle", kwargs))

    def draw_text(self, **kwargs: object) -> None:
        self.calls.append(("draw_text", kwargs))

    def add_dimension(self, **kwargs: object) -> None:
        self.calls.append(("add_dimension", kwargs))


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

        with tempfile.TemporaryDirectory() as temp_dir:
            plan_path = Path(temp_dir) / "plan.json"
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


if __name__ == "__main__":
    unittest.main()
