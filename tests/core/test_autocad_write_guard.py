from __future__ import annotations

import unittest

from core.cad_io.autocad_com import AutoCADComDriver
from core.cad_io.preview_write_guard_mixin import PreviewWriteGuardMixin
from core.safety.policy import DIAGNOSTIC_LAYER, PREVIEW_LAYER
from core.safety.write_guard import CadWriteGuardViolation


class _GuardProbe(PreviewWriteGuardMixin):
    def __init__(self) -> None:
        self._init_preview_write_guard(preview_layer=PREVIEW_LAYER)


class _FakeComModelSpace:
    def __init__(self) -> None:
        self.add_line_count = 0
        self.add_hatch_count = 0
        self.add_text_count = 0
        self.add_polyline_count = 0
        self.hatches: list[object] = []

    def AddLine(self, start: object, end: object) -> object:
        self.add_line_count += 1
        return type("Entity", (), {"Handle": "H1"})()

    def AddText(self, text: str, position: object, height: float | int) -> object:
        self.add_text_count += 1
        return type("Entity", (), {"Handle": "T1", "Rotation": 0})()

    def AddHatch(self, *args: object, **kwargs: object) -> object:
        self.add_hatch_count += 1
        hatch = type(
            "HatchEntity",
            (),
            {
                "Handle": "HATCH1",
                "AppendOuterLoop": lambda self, loop: setattr(self, "outer_loop", loop),
                "Evaluate": lambda self: setattr(self, "evaluated", True),
            },
        )()
        self.hatches.append(hatch)
        return hatch

    def AddLightWeightPolyline(self, coordinates: object) -> object:
        self.add_polyline_count += 1
        return type("PolylineEntity", (), {"Handle": "PL1", "Closed": False})()


class AutoCADWriteGuardTests(unittest.TestCase):
    def test_blocks_formal_layer_before_apply(self) -> None:
        probe = _GuardProbe()
        with self.assertRaises(CadWriteGuardViolation):
            probe._guard_preview_layer_write("WALL")

    def test_diagnostic_layer_requires_diagnostic_role(self) -> None:
        probe = _GuardProbe()
        with self.assertRaises(CadWriteGuardViolation):
            probe._guard_preview_layer_write(DIAGNOSTIC_LAYER)

        probe._guard_preview_layer_write(DIAGNOSTIC_LAYER, layer_role="diagnostic")

        with self.assertRaises(CadWriteGuardViolation):
            probe._guard_preview_layer_write("WALL", layer_role="diagnostic")

    def test_blocks_save_and_delete(self) -> None:
        probe = _GuardProbe()
        with self.assertRaises(CadWriteGuardViolation):
            probe.save_document()
        with self.assertRaises(CadWriteGuardViolation):
            probe.delete_entity_by_handle("H1")

    def test_real_com_driver_blocks_formal_layer_before_addline(self) -> None:
        driver = AutoCADComDriver.__new__(AutoCADComDriver)
        driver._init_preview_write_guard(preview_layer=PREVIEW_LAYER)
        driver.model_space = _FakeComModelSpace()
        driver._point = lambda values: values  # type: ignore[method-assign]

        with self.assertRaises(CadWriteGuardViolation):
            driver.draw_line(
                start_point=[0, 0, 0],
                end_point=[100, 0, 0],
                layer="WALL",
            )

        self.assertEqual(driver.model_space.add_line_count, 0)

    def test_real_com_driver_blocks_formal_layer_before_hatch_write(self) -> None:
        driver = AutoCADComDriver.__new__(AutoCADComDriver)
        driver._init_preview_write_guard(preview_layer=PREVIEW_LAYER)
        driver.model_space = _FakeComModelSpace()

        with self.assertRaises(CadWriteGuardViolation):
            driver.draw_hatch(
                boundary_points=[[0, 0], [100, 0], [100, 100], [0, 100]],
                layer="WALL",
            )

        self.assertEqual(driver.model_space.add_hatch_count, 0)

    def test_real_com_driver_blocks_unmarked_diagnostic_text_before_write(self) -> None:
        driver = AutoCADComDriver.__new__(AutoCADComDriver)
        driver._init_preview_write_guard(preview_layer=PREVIEW_LAYER)
        driver.model_space = _FakeComModelSpace()
        driver._point = lambda values: values  # type: ignore[method-assign]

        with self.assertRaises(CadWriteGuardViolation):
            driver.draw_text(
                text="probe",
                position=[0, 0, 0],
                height=10,
                layer=DIAGNOSTIC_LAYER,
            )

        self.assertEqual(driver.model_space.add_text_count, 0)

    def test_real_com_driver_hatch_writes_closed_boundary_and_hatch(self) -> None:
        driver = AutoCADComDriver.__new__(AutoCADComDriver)
        driver._init_preview_write_guard(preview_layer=PREVIEW_LAYER)
        driver.model_space = _FakeComModelSpace()
        driver._point2d_array = lambda points: points  # type: ignore[method-assign]
        driver._apply_common = lambda entity, **kwargs: setattr(entity, "Layer", kwargs.get("layer"))  # type: ignore[method-assign]
        driver._win32com = type(
            "FakeClient",
            (),
            {"VARIANT": lambda self, variant_type, value: ("variant", variant_type, value)},
        )()
        driver._pythoncom = type("FakePythonCom", (), {"VT_ARRAY": 0x2000, "VT_DISPATCH": 9})()

        result = driver.draw_hatch(
            boundary_points=[[0, 0], [100, 0], [100, 100], [0, 100]],
            pattern="ANSI31",
            layer=PREVIEW_LAYER,
            layer_role="preview",
        )

        self.assertEqual(result["handle"], "HATCH1")
        self.assertEqual(result["boundary_handles"], ["PL1"])
        self.assertEqual(result["created_handles"], ["PL1", "HATCH1"])
        self.assertEqual(driver.model_space.add_polyline_count, 1)
        self.assertEqual(driver.model_space.add_hatch_count, 1)
        self.assertTrue(getattr(driver.model_space.hatches[0], "evaluated", False))


if __name__ == "__main__":
    unittest.main()
