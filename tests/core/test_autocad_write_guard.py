from __future__ import annotations

import unittest

from core.cad_io.autocad_com import AutoCADComDriver
from core.cad_io.preview_write_guard_mixin import PreviewWriteGuardMixin
from core.safety.policy import PREVIEW_LAYER
from core.safety.write_guard import CadWriteGuardViolation


class _GuardProbe(PreviewWriteGuardMixin):
    def __init__(self) -> None:
        self._init_preview_write_guard(preview_layer=PREVIEW_LAYER)


class _FakeComModelSpace:
    def __init__(self) -> None:
        self.add_line_count = 0
        self.add_hatch_count = 0

    def AddLine(self, start: object, end: object) -> object:
        self.add_line_count += 1
        return type("Entity", (), {"Handle": "H1"})()

    def AddHatch(self, *args: object, **kwargs: object) -> object:
        self.add_hatch_count += 1
        return type("Entity", (), {"Handle": "HATCH1"})()


class AutoCADWriteGuardTests(unittest.TestCase):
    def test_blocks_formal_layer_before_apply(self) -> None:
        probe = _GuardProbe()
        with self.assertRaises(CadWriteGuardViolation):
            probe._guard_preview_layer_write("WALL")

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

    def test_real_com_driver_hatch_returns_structured_deferred_without_com_write(self) -> None:
        driver = AutoCADComDriver.__new__(AutoCADComDriver)
        driver._init_preview_write_guard(preview_layer=PREVIEW_LAYER)
        driver.model_space = _FakeComModelSpace()

        result = driver.draw_hatch(
            boundary_points=[[0, 0], [100, 0], [100, 100], [0, 100]],
            pattern="ANSI31",
            layer=PREVIEW_LAYER,
            layer_role="preview",
        )

        self.assertEqual(result["primitive"], "hatch")
        self.assertEqual(result["status"], "deferred")
        self.assertEqual(result["failure_category"], "hatch_unverified")
        self.assertEqual(result["created_handles"], [])
        self.assertIs(result["geometry_verified"], False)
        self.assertEqual(driver.model_space.add_hatch_count, 0)


if __name__ == "__main__":
    unittest.main()
