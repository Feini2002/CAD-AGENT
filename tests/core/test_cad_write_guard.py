from __future__ import annotations

import unittest

from core.safety.policy import PREVIEW_LAYER
from core.safety.write_guard import CadWriteGuard, CadWriteGuardViolation, run_negative_write_guard_checks
from core.verification.fake_cad_driver import FakeCadDriver


class CadWriteGuardTests(unittest.TestCase):
    def test_blocks_formal_layer_write_on_fake_driver(self) -> None:
        driver = FakeCadDriver()
        with self.assertRaises(CadWriteGuardViolation):
            driver.draw_line(start_point=[0, 0, 0], end_point=[1, 0, 0], layer="WALL")
        self.assertEqual(len(driver.entities), 0)

    def test_blocks_save_delete_and_overwrite_helpers(self) -> None:
        driver = FakeCadDriver()
        with self.assertRaises(CadWriteGuardViolation):
            driver.save_document()
        with self.assertRaises(CadWriteGuardViolation):
            driver.overwrite_document()
        with self.assertRaises(CadWriteGuardViolation):
            driver.delete_entity_by_handle("H101")

    def test_negative_write_guard_checks_pass_on_fake_driver(self) -> None:
        driver = FakeCadDriver()
        driver.draw_line(start_point=[0, 0, 0], end_point=[100, 0, 0], layer=PREVIEW_LAYER)
        report = run_negative_write_guard_checks(driver)
        self.assertEqual(report["status"], "pass")
        self.assertGreaterEqual(report["blocked_attempt_count"], 3)
        self.assertTrue(all(check["status"] == "pass" for check in report["checks"]))

    def test_preview_layer_write_allowed(self) -> None:
        driver = FakeCadDriver()
        result = driver.draw_line(start_point=[0, 0, 0], end_point=[50, 0, 0], layer=PREVIEW_LAYER)
        self.assertTrue(result["handle"])
        self.assertEqual(len(driver.entities), 1)
