from __future__ import annotations

import json
import types
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.execution.execute_plan import execute_plan_file
from core.cad_io.autocad_com import CONTROLLED_BLOCK_NAME, PREVIEW_LAYER, AutoCADComDriver
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

    def insert_block_alpha(self, **kwargs: object) -> dict[str, str]:
        self.calls.append(("insert_block_alpha", kwargs))
        return {"handle": "BLOCK-H1"}


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
        self.assertEqual(result["safety"]["layer"], "CODEX_PREVIEW")
        self.assertFalse(result["safety"]["saved_dwg"])

    def test_insert_block_alpha_records_fake_driver_call_without_touching_cad(self) -> None:
        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        driver = RecordingDriver()

        result = execute_plan_file(plan_path, driver=driver)

        self.assertEqual(result["status"], "executed")
        self.assertEqual(result["intent"], "insert_block_alpha")
        self.assertEqual(result["entities"], {"insert_block_alpha": 1})
        self.assertEqual(result["geometry_accuracy"], "not_verified_without_cad_readback")
        self.assertEqual(result["created_handles"], ["BLOCK-H1"])
        self.assertEqual(len(driver.calls), 1)
        self.assertEqual(driver.calls[0][0], "insert_block_alpha")
        self.assertEqual(driver.calls[0][1]["block_name"], "CODEX_TEST_BLOCK_001")
        self.assertEqual(driver.calls[0][1]["layer"], "CODEX_PREVIEW")

    def test_insert_block_alpha_autocad_driver_matches_execute_plan_contract(self) -> None:
        class FakeBlockReference:
            Handle = "BR-EXEC"

        class FakeBlockRecord:
            def __init__(self) -> None:
                self.entities = []
                width = 900.0
                depth = 450.0
                corners = [
                    (0.0, 0.0, 0.0),
                    (width, 0.0, 0.0),
                    (width, depth, 0.0),
                    (0.0, depth, 0.0),
                ]
                for index, (start, end) in enumerate(
                    [
                        (corners[0], corners[1]),
                        (corners[1], corners[2]),
                        (corners[2], corners[3]),
                        (corners[3], corners[0]),
                    ],
                    start=1,
                ):
                    self.entities.append(
                        types.SimpleNamespace(
                            Handle=f"DEF-{index}",
                            ObjectName="AcDbLine",
                            Layer="0",
                            StartPoint=start,
                            EndPoint=end,
                        )
                    )

            @property
            def Count(self) -> int:
                return len(self.entities)

            def Item(self, index: int) -> object:
                return self.entities[index]

            def AddLine(self, *_: object) -> FakeBlockReference:
                return FakeBlockReference()

        class FakeBlocks:
            def __init__(self) -> None:
                self.names = {CONTROLLED_BLOCK_NAME}
                self.record = FakeBlockRecord()

            def Item(self, name: str) -> object:
                if name not in self.names:
                    raise KeyError(name)
                return self.record

            def Add(self, *_: object) -> FakeBlockRecord:
                raise AssertionError("should reuse existing block definition")

        class FakeModelSpace:
            def InsertBlock(self, *_args: object, **_kwargs: object) -> FakeBlockReference:
                return FakeBlockReference()

        class FakeLayers:
            def Item(self, _layer: str) -> object:
                return object()

        driver = object.__new__(AutoCADComDriver)
        driver.doc = types.SimpleNamespace(Blocks=FakeBlocks(), Layers=FakeLayers())
        driver.model_space = FakeModelSpace()
        driver._point = lambda values: ("point", tuple(float(value) for value in values))  # type: ignore[method-assign]
        driver._handle = AutoCADComDriver._handle  # type: ignore[method-assign]
        driver.ensure_layer = lambda layer: None  # type: ignore[method-assign]
        driver._apply_common = lambda entity, **kwargs: None  # type: ignore[method-assign]

        plan_path = PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json"
        result = execute_plan_file(plan_path, driver=driver)

        self.assertEqual(result["created_handles"], ["BR-EXEC"])
        self.assertEqual(result["layer"], PREVIEW_LAYER)

    def test_insert_block_alpha_rejects_formal_layer_during_execution(self) -> None:
        plan = {
            "version": "0.1",
            "domain": "generic",
            "intent": "insert_block_alpha",
            "object": {
                "type": "block_reference",
                "name": "Controlled Test Block",
                "block_id": "controlled-test-block-001",
                "cad_identity": {"block_name": "CODEX_TEST_BLOCK_001"},
            },
            "placement": {"mode": "absolute", "base_point": [0, 0, 0], "rotation": 0, "scale": [1, 1, 1]},
            "drawing": {"layer": "A-FURN"},
            "confidence": 1.0,
            "needs_confirmation": False,
        }
        plan_path = artifact_path("execute_plan", "block_alpha_formal_layer.json")
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Invalid CAD_PLAN"):
            execute_plan_file(plan_path, driver=RecordingDriver())

    def test_large_object_label_height_is_capped_for_readable_previews(self) -> None:
        plan = {
            "version": "0.1",
            "domain": "residential",
            "intent": "draw_object",
            "object": {"type": "bed", "name": "Bed", "width": 2400, "depth": 1900},
            "placement": {"mode": "absolute", "base_point": [0, 0, 0]},
            "drawing": {"layer": "CODEX_PREVIEW", "include_label": True, "include_dimensions": False},
            "confidence": 1.0,
            "needs_confirmation": False,
        }
        plan_path = artifact_path("execute_plan", "large_label.json")
        plan_path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")

        driver = RecordingDriver()
        execute_plan_file(plan_path, driver=driver)

        text_call = next(kwargs for name, kwargs in driver.calls if name == "draw_text")
        self.assertEqual(text_call["height"], 160)

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

            def AddCircle(self, *_: object) -> FakeEntity:
                return self._entity()

            def AddArc(self, *_: object) -> FakeEntity:
                return self._entity()

            def AddLightWeightPolyline(self, *_: object) -> FakeEntity:
                return self._entity()

        driver = object.__new__(AutoCADComDriver)
        driver.model_space = FakeModelSpace()
        driver._apply_common = lambda entity, **kwargs: None  # type: ignore[method-assign]
        driver._point = lambda values: tuple(values)  # type: ignore[method-assign]
        driver._point2d_array = lambda points: tuple(float(value) for point in points for value in point[:2])  # type: ignore[method-assign]

        self.assertEqual(
            driver.draw_rectangle(corner1=[0, 0, 0], corner2=[100, 50, 0]),
            {"handles": ["C1", "C2", "C3", "C4"]},
        )
        self.assertEqual(
            driver.draw_line(start_point=[0, 0, 0], end_point=[100, 50, 0]),
            {"handle": "C5"},
        )
        self.assertEqual(
            driver.draw_circle(center=[25, 25, 0], radius=12),
            {"handle": "C6"},
        )
        self.assertEqual(
            driver.draw_arc(center=[50, 25, 0], radius=15, start_angle=0, end_angle=90),
            {"handle": "C7"},
        )
        self.assertEqual(
            driver.draw_polyline(points=[[0, 0, 0], [40, 0, 0], [40, 20, 0]], closed=True),
            {"handle": "C8"},
        )
        self.assertEqual(
            driver.draw_text(text="T", position=[0, 0, 0], height=10),
            {"handle": "C9"},
        )
        self.assertEqual(
            driver.add_dimension(start_point=[0, 0, 0], end_point=[100, 0, 0]),
            {"handle": "C10"},
        )


if __name__ == "__main__":
    unittest.main()
