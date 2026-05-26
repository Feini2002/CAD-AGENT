from __future__ import annotations

import sys
import types
import unittest
from math import pi
from unittest.mock import patch

from core.cad_io.autocad_com import (
    CONTROLLED_BLOCK_DEFINITION_LAYER,
    CONTROLLED_BLOCK_MIN_SIZE,
    CONTROLLED_BLOCK_NAME,
    PREVIEW_LAYER,
    AutoCADComDriver,
    BlockAlphaInsertionError,
    block_definition_failure,
)


class AutoCADComDriverConnectionTests(unittest.TestCase):
    def test_existing_only_connection_error_preserves_com_detail(self) -> None:
        fake_win32com = types.ModuleType("win32com")
        fake_client = types.ModuleType("win32com.client")

        def get_active_object(_prog_id: str) -> object:
            raise RuntimeError("COM detail: invalid class string")

        fake_client.GetActiveObject = get_active_object  # type: ignore[attr-defined]
        fake_win32com.client = fake_client  # type: ignore[attr-defined]

        with patch.dict(sys.modules, {"win32com": fake_win32com, "win32com.client": fake_client}):
            with self.assertRaisesRegex(
                RuntimeError,
                "No active AutoCAD\\.Application instance is available.*COM detail: invalid class string",
            ):
                AutoCADComDriver(connect_existing_only=True)

    def test_existing_only_connection_tries_versioned_autocad_progids(self) -> None:
        fake_win32com = types.ModuleType("win32com")
        fake_client = types.ModuleType("win32com.client")
        calls: list[str] = []

        class FakeDocument:
            ModelSpace = object()

        class FakeApp:
            ActiveDocument = FakeDocument()

        def get_active_object(prog_id: str) -> object:
            calls.append(prog_id)
            if prog_id == "AutoCAD.Application.25":
                return FakeApp()
            raise RuntimeError(f"{prog_id} unavailable")

        fake_client.GetActiveObject = get_active_object  # type: ignore[attr-defined]
        fake_win32com.client = fake_client  # type: ignore[attr-defined]

        with patch.dict(sys.modules, {"win32com": fake_win32com, "win32com.client": fake_client}):
            driver = AutoCADComDriver(connect_existing_only=True)

        self.assertIsInstance(driver.app, FakeApp)
        self.assertIn("AutoCAD.Application", calls)
        self.assertIn("AutoCAD.Application.25", calls)

    def test_point_values_are_converted_to_autocad_float_array_variants(self) -> None:
        class FakeClient:
            def VARIANT(self, variant_type: int, value: tuple[float, ...]) -> tuple[str, int, tuple[float, ...]]:
                return ("variant", variant_type, value)

        driver = object.__new__(AutoCADComDriver)
        driver._win32com = FakeClient()
        driver._pythoncom = types.SimpleNamespace(VT_ARRAY=0x2000, VT_R8=5)

        self.assertEqual(
            driver._point([1, 2.5, 0]),
            ("variant", 0x2000 | 5, (1.0, 2.5, 0.0)),
        )

    def test_draw_methods_pass_converted_points_to_modelspace(self) -> None:
        class FakeEntity:
            Handle = "H"
            Closed = False

        class FakeModelSpace:
            def __init__(self) -> None:
                self.calls: list[tuple[str, object, object, object]] = []

            def AddLine(self, start: object, end: object) -> FakeEntity:
                self.calls.append(("line", start, end, None))
                return FakeEntity()

            def AddText(self, text: str, position: object, height: object) -> FakeEntity:
                self.calls.append(("text", text, position, height))
                return FakeEntity()

            def AddDimAligned(self, start: object, end: object, text_position: object) -> FakeEntity:
                self.calls.append(("dimension", start, end, text_position))
                return FakeEntity()

            def AddCircle(self, center: object, radius: object) -> FakeEntity:
                self.calls.append(("circle", center, radius, None))
                return FakeEntity()

            def AddArc(self, center: object, radius: object, start_angle: object, end_angle: object) -> FakeEntity:
                self.calls.append(("arc", center, radius, (start_angle, end_angle)))
                return FakeEntity()

            def AddLightWeightPolyline(self, coordinates: object) -> FakeEntity:
                self.calls.append(("polyline", coordinates, None, None))
                return FakeEntity()

        driver = object.__new__(AutoCADComDriver)
        driver.model_space = FakeModelSpace()
        driver._apply_common = lambda entity, **kwargs: None  # type: ignore[method-assign]
        driver._point = lambda values: ("point", tuple(float(value) for value in values))  # type: ignore[method-assign]
        driver._point2d_array = lambda points: ("point2d_array", tuple(float(value) for point in points for value in point[:2]))  # type: ignore[method-assign]

        driver.draw_rectangle(corner1=[0, 0, 0], corner2=[100, 50, 0])
        driver.draw_line(start_point=[0, 0, 0], end_point=[100, 50, 0])
        driver.draw_circle(center=[25, 25, 0], radius=12)
        driver.draw_arc(center=[50, 25, 0], radius=15, start_angle=0, end_angle=90)
        polyline = driver.draw_polyline(points=[[0, 0, 0], [40, 0, 0], [40, 20, 0]], closed=True)
        driver.draw_text(text="T", position=[1, 2, 0], height=10)
        driver.add_dimension(start_point=[0, 0, 0], end_point=[100, 0, 0], text_position=[50, -10, 0])

        self.assertEqual(driver.model_space.calls[0], ("line", ("point", (0.0, 0.0, 0.0)), ("point", (100.0, 0.0, 0.0)), None))
        self.assertIn(("line", ("point", (0.0, 0.0, 0.0)), ("point", (100.0, 50.0, 0.0)), None), driver.model_space.calls)
        self.assertIn(("circle", ("point", (25.0, 25.0, 0.0)), 12, None), driver.model_space.calls)
        arc_call = next(call for call in driver.model_space.calls if call[0] == "arc")
        self.assertEqual(arc_call[1], ("point", (50.0, 25.0, 0.0)))
        self.assertEqual(arc_call[2], 15)
        self.assertAlmostEqual(arc_call[3][0], 0.0)
        self.assertAlmostEqual(arc_call[3][1], pi / 2)
        self.assertIn(("polyline", ("point2d_array", (0.0, 0.0, 40.0, 0.0, 40.0, 20.0)), None, None), driver.model_space.calls)
        self.assertEqual(polyline, {"handle": "H"})
        self.assertIn(("text", "T", ("point", (1.0, 2.0, 0.0)), 10), driver.model_space.calls)
        self.assertIn(
            (
                "dimension",
                ("point", (0.0, 0.0, 0.0)),
                ("point", (100.0, 0.0, 0.0)),
                ("point", (50.0, -10.0, 0.0)),
            ),
            driver.model_space.calls,
        )


class ControlledBlockDefinitionTests(unittest.TestCase):
    def _driver_with_blocks(
        self,
        *,
        existing: set[str] | None = None,
        create_raises: Exception | None = None,
        invalid_existing_definition: bool = False,
        add_line_raises: Exception | None = None,
    ) -> AutoCADComDriver:
        existing = existing or set()

        class FakeEntity:
            def __init__(self, handle: str, start: object | None = None, end: object | None = None) -> None:
                self.Handle = handle
                self.Layer = ""
                self.ObjectName = "AcDbLine"
                self.StartPoint = start
                self.EndPoint = end

        class FakeBlockRecord:
            def __init__(self, *, existing_valid: bool = False, existing_invalid: bool = False) -> None:
                self.lines: list[tuple[object, object]] = []
                self._line_count = 0
                self.deleted = False
                self.entities: list[FakeEntity] = []
                if existing_valid or existing_invalid:
                    width, depth = CONTROLLED_BLOCK_MIN_SIZE
                    if existing_invalid:
                        width = 123.0
                    corners = [
                        (0.0, 0.0, 0.0),
                        (width, 0.0, 0.0),
                        (width, depth, 0.0),
                        (0.0, depth, 0.0),
                    ]
                    edges = [
                        (corners[0], corners[1]),
                        (corners[1], corners[2]),
                        (corners[2], corners[3]),
                        (corners[3], corners[0]),
                    ]
                    for index, (start, end) in enumerate(edges, start=1):
                        entity = FakeEntity(f"EX{index}", start, end)
                        entity.Layer = CONTROLLED_BLOCK_DEFINITION_LAYER
                        self.entities.append(entity)

            def AddLine(self, start: object, end: object) -> FakeEntity:
                if add_line_raises is not None:
                    raise add_line_raises
                self.lines.append((start, end))
                self._line_count += 1
                entity = FakeEntity(f"BL{self._line_count}", start, end)
                self.entities.append(entity)
                return entity

            @property
            def Count(self) -> int:
                return len(self.entities)

            def Item(self, index: int) -> FakeEntity:
                return self.entities[index]

            def Delete(self) -> None:
                self.deleted = True

        class FakeBlocks:
            def __init__(self) -> None:
                self.names = set(existing)
                self.created: list[tuple[object, str]] = []
                self.last_record: FakeBlockRecord | None = None
                self.existing_record = FakeBlockRecord(
                    existing_valid=CONTROLLED_BLOCK_NAME in self.names and not invalid_existing_definition,
                    existing_invalid=CONTROLLED_BLOCK_NAME in self.names and invalid_existing_definition,
                )

            def Item(self, name: str) -> object:
                if name not in self.names:
                    raise KeyError(name)
                return self.existing_record

            def Add(self, origin: object, name: str) -> FakeBlockRecord:
                if create_raises is not None:
                    raise create_raises
                self.created.append((origin, name))
                self.names.add(name)
                record = FakeBlockRecord()
                self.last_record = record
                return record

        driver = object.__new__(AutoCADComDriver)
        driver.doc = types.SimpleNamespace(Blocks=FakeBlocks())
        driver._point = lambda values: ("point", tuple(float(value) for value in values))  # type: ignore[method-assign]
        driver._handle = AutoCADComDriver._handle  # type: ignore[method-assign]
        return driver

    def test_block_definition_failure_payload_is_structured(self) -> None:
        payload = block_definition_failure(block_name="X", message="missing")
        self.assertEqual(payload["status"], "definition_missing")
        self.assertEqual(payload["failure_category"], "definition_missing")
        self.assertEqual(payload["block_name"], "X")

    def test_ensure_controlled_block_definition_reuses_existing(self) -> None:
        driver = self._driver_with_blocks(existing={CONTROLLED_BLOCK_NAME})
        result = driver.ensure_controlled_block_definition()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["source"], "existing")
        self.assertEqual(result["block_name"], CONTROLLED_BLOCK_NAME)
        self.assertEqual(driver.doc.Blocks.created, [])

    def test_ensure_controlled_block_definition_creates_minimal_geometry(self) -> None:
        driver = self._driver_with_blocks()
        result = driver.ensure_controlled_block_definition()
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["source"], "created")
        self.assertEqual(result["definition_layer"], CONTROLLED_BLOCK_DEFINITION_LAYER)
        self.assertEqual(len(result["definition_handles"]), 4)
        self.assertEqual(driver.doc.Blocks.created[0][1], CONTROLLED_BLOCK_NAME)
        record = driver.doc.Blocks.last_record
        assert record is not None
        self.assertEqual(len(record.lines), 4)
        from core.cad_io.autocad_com import _controlled_block_footprint_mm

        width, depth = _controlled_block_footprint_mm()
        expected_edges = {
            ((0.0, 0.0, 0.0), (width, 0.0, 0.0)),
            ((width, 0.0, 0.0), (width, depth, 0.0)),
            ((width, depth, 0.0), (0.0, depth, 0.0)),
            ((0.0, depth, 0.0), (0.0, 0.0, 0.0)),
        }
        actual_edges = {
            (start[1], end[1])
            for start, end in record.lines
        }
        self.assertEqual(actual_edges, expected_edges)

    def test_ensure_controlled_block_definition_returns_definition_missing_when_create_fails(self) -> None:
        driver = self._driver_with_blocks(create_raises=RuntimeError("COM blocked"))
        result = driver.ensure_controlled_block_definition()
        self.assertEqual(result["status"], "definition_missing")
        self.assertEqual(result["failure_category"], "definition_missing")
        self.assertIn("COM blocked", result["message"])

    def test_ensure_controlled_block_definition_honors_allow_create_false(self) -> None:
        driver = self._driver_with_blocks()
        result = driver.ensure_controlled_block_definition(allow_create=False)
        self.assertEqual(result["status"], "definition_missing")
        self.assertIn("not present", result["message"])

    def test_ensure_controlled_block_definition_rejects_uncontrolled_name(self) -> None:
        driver = self._driver_with_blocks(existing={"PROJECT_REAL_BLOCK"})
        result = driver.ensure_controlled_block_definition("PROJECT_REAL_BLOCK")
        self.assertEqual(result["status"], "definition_missing")
        self.assertEqual(result["failure_category"], "controlled_block_mismatch")
        self.assertEqual(driver.doc.Blocks.created, [])

    def _driver_with_insert_block(self, *, existing: set[str] | None = None) -> AutoCADComDriver:
        driver = self._driver_with_blocks(existing=existing)

        class FakeBlockReference:
            def __init__(self) -> None:
                self.Handle = "BR1"
                self.Layer = ""
                self.deleted = False

            def Delete(self) -> None:
                self.deleted = True

        class FakeModelSpace:
            def __init__(self) -> None:
                self.insert_calls: list[dict[str, object]] = []

            def InsertBlock(
                self,
                insertion_point: object,
                name: str,
                xscale: float,
                yscale: float,
                zscale: float,
                rotation: float,
            ) -> FakeBlockReference:
                self.insert_calls.append(
                    {
                        "insertion_point": insertion_point,
                        "name": name,
                        "xscale": xscale,
                        "yscale": yscale,
                        "zscale": zscale,
                        "rotation": rotation,
                    }
                )
                return FakeBlockReference()

        class FakeLayers:
            def Item(self, _layer: str) -> object:
                return object()

            def Add(self, _layer: str) -> object:
                return object()

        driver.model_space = FakeModelSpace()
        driver.doc.Layers = FakeLayers()  # type: ignore[attr-defined]
        driver.ensure_layer = lambda layer: None  # type: ignore[method-assign]
        driver._apply_common = lambda entity, **kwargs: setattr(entity, "Layer", kwargs.get("layer", ""))  # type: ignore[method-assign]
        return driver

    def test_insert_block_alpha_inserts_on_preview_layer(self) -> None:
        driver = self._driver_with_insert_block(existing={CONTROLLED_BLOCK_NAME})
        result = driver.insert_block_alpha(
            block_id="controlled-test-block-001",
            block_name=CONTROLLED_BLOCK_NAME,
            base_point=[1200, 800, 0],
            rotation=90,
            scale=[2, 2, 2],
            layer=PREVIEW_LAYER,
        )
        self.assertEqual(result["handle"], "BR1")
        self.assertEqual(result["block_name"], CONTROLLED_BLOCK_NAME)
        self.assertEqual(result["block_definition_source"], "existing")
        self.assertEqual(result["layer"], PREVIEW_LAYER)
        call = driver.model_space.insert_calls[0]
        self.assertEqual(call["name"], CONTROLLED_BLOCK_NAME)
        self.assertEqual(call["xscale"], 2.0)
        self.assertAlmostEqual(call["rotation"], pi / 2)

    def test_insert_block_alpha_creates_definition_when_missing(self) -> None:
        driver = self._driver_with_insert_block()
        result = driver.insert_block_alpha(
            block_id="controlled-test-block-001",
            block_name=CONTROLLED_BLOCK_NAME,
            base_point=[0, 0, 0],
            rotation=0,
            scale=[1, 1, 1],
            layer=PREVIEW_LAYER,
        )
        self.assertEqual(result["block_definition_source"], "created")
        self.assertEqual(driver.doc.Blocks.created[0][1], CONTROLLED_BLOCK_NAME)
        self.assertEqual(len(driver.model_space.insert_calls), 1)

    def test_insert_block_alpha_rejects_non_preview_layer(self) -> None:
        driver = self._driver_with_insert_block(existing={CONTROLLED_BLOCK_NAME})
        with self.assertRaisesRegex(ValueError, "only allows layer=CODEX_PREVIEW"):
            driver.insert_block_alpha(
                block_id="controlled-test-block-001",
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=[0, 0, 0],
                layer="A-FURN",
            )

    def test_insert_block_alpha_rejects_non_uniform_scale(self) -> None:
        driver = self._driver_with_insert_block(existing={CONTROLLED_BLOCK_NAME})
        with self.assertRaisesRegex(ValueError, "uniform scale"):
            driver.insert_block_alpha(
                block_id="controlled-test-block-001",
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=[0, 0, 0],
                scale=[1, 2, 1],
                layer=PREVIEW_LAYER,
            )

    def test_insert_block_alpha_rejects_uncontrolled_identity(self) -> None:
        driver = self._driver_with_insert_block(existing={"PROJECT_REAL_BLOCK"})
        with self.assertRaisesRegex(ValueError, "controlled-test-block-001"):
            driver.insert_block_alpha(
                block_id="project-block-999",
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=[0, 0, 0],
                layer=PREVIEW_LAYER,
            )
        with self.assertRaisesRegex(ValueError, "CODEX_TEST_BLOCK_001"):
            driver.insert_block_alpha(
                block_id="controlled-test-block-001",
                block_name="PROJECT_REAL_BLOCK",
                base_point=[0, 0, 0],
                layer=PREVIEW_LAYER,
            )
        self.assertEqual(driver.model_space.insert_calls, [])

    def test_insert_block_alpha_raises_definition_missing_when_create_blocked(self) -> None:
        driver = self._driver_with_insert_block()
        with self.assertRaises(BlockAlphaInsertionError) as ctx:
            driver.ensure_controlled_block_definition = (  # type: ignore[method-assign]
                lambda block_name=None, **kwargs: block_definition_failure(
                    block_name=str(block_name or CONTROLLED_BLOCK_NAME),
                    message="blocked",
                )
            )
            driver.insert_block_alpha(
                block_id="controlled-test-block-001",
                block_name=CONTROLLED_BLOCK_NAME,
                base_point=[0, 0, 0],
                layer=PREVIEW_LAYER,
            )
        self.assertEqual(ctx.exception.payload["failure_category"], "definition_missing")


if __name__ == "__main__":
    unittest.main()
