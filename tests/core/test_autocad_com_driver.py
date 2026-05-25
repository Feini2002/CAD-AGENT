from __future__ import annotations

import sys
import types
import unittest
from math import pi
from unittest.mock import patch

from core.cad_io.autocad_com import AutoCADComDriver


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


if __name__ == "__main__":
    unittest.main()
