from __future__ import annotations

import json
import unittest

from core.verification.cad_session_guard import (
    PREVIEW_LAYER,
    blocked_snapshot,
    build_session_guard_report,
    capture_active_document_snapshot,
    compare_active_document_snapshots,
    write_session_guard_report,
)
from core.verification.fake_cad_driver import FakeCadEntity, FakeCadDriver
from tests.helpers import temporary_artifact_dir


class CadSessionGuardTests(unittest.TestCase):
    def test_blocked_snapshot_before_connect(self) -> None:
        snapshot = blocked_snapshot(phase="before_connect", reason="cad_not_connected")
        self.assertEqual(snapshot["status"], "blocked")
        self.assertEqual(snapshot["phase"], "before_connect")
        self.assertEqual(snapshot["blocked_reason"], "cad_not_connected")

    def test_capture_snapshot_records_document_and_preview_counts(self) -> None:
        driver = FakeCadDriver()
        driver.draw_line(start_point=[0, 0, 0], end_point=[100, 0, 0], layer=PREVIEW_LAYER)
        driver.entities["H900"] = FakeCadEntity(
            handle="H900",
            object_name="AcDbLine",
            layer="WALL",
            StartPoint=[0, 0, 0],
            EndPoint=[0, 100, 0],
        )

        snapshot = capture_active_document_snapshot(driver, phase="after_connect")

        self.assertEqual(snapshot["status"], "captured")
        self.assertEqual(snapshot["document"]["name"], "sample-active.dwg")
        self.assertTrue(snapshot["document"]["fingerprint"])
        self.assertEqual(snapshot["preview_layer_entity_count"], 1)
        self.assertEqual(snapshot["modelspace_summary"]["entity_count"], 2)
        self.assertEqual(snapshot["open_document_count"], 1)

    def test_compare_detects_document_identity_change(self) -> None:
        before = capture_active_document_snapshot(FakeCadDriver(), phase="after_connect")
        after = capture_active_document_snapshot(FakeCadDriver(), phase="after_write")
        after["document"] = {"name": "other.dwg", "full_name": r"C:\other.dwg", "fingerprint": "changed"}

        comparison = compare_active_document_snapshots(before, after)

        self.assertEqual(comparison["status"], "document_changed")
        checks = {check["name"]: check for check in comparison["checks"]}
        self.assertEqual(checks["active_document_identity_stable"]["status"], "fail")

    def test_session_guard_blocks_when_multiple_documents_open(self) -> None:
        driver = FakeCadDriver(open_document_count=2)
        after_connect = capture_active_document_snapshot(driver, phase="after_connect")
        report = build_session_guard_report(
            before_connect=blocked_snapshot(phase="before_connect", reason="cad_not_connected"),
            after_connect=after_connect,
        )

        self.assertEqual(report["status"], "blocked")
        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual(checks["multi_document_uncertain"]["status"], "fail")

    def test_session_guard_consistent_after_preview_writes(self) -> None:
        driver = FakeCadDriver()
        after_connect = capture_active_document_snapshot(driver, phase="after_connect")
        driver.draw_rectangle(
            corner1=[10, 10, 0],
            corner2=[110, 60, 0],
            layer=PREVIEW_LAYER,
        )
        after_write = capture_active_document_snapshot(driver, phase="after_write")
        report = build_session_guard_report(
            before_connect=blocked_snapshot(phase="before_connect", reason="cad_not_connected"),
            after_connect=after_connect,
            after_write=after_write,
        )

        self.assertEqual(report["status"], "consistent")
        self.assertEqual(report["comparison"]["preview_layer_entity_delta"], 4)
        self.assertTrue(all(check["status"] != "fail" for check in report["checks"]))

    def test_write_session_guard_report(self) -> None:
        report = build_session_guard_report(
            before_connect=blocked_snapshot(phase="before_connect", reason="cad_not_connected"),
            after_connect=blocked_snapshot(phase="after_connect", reason="cad_connection_failed"),
        )
        with temporary_artifact_dir("cad_session_guard") as output_dir:
            write_session_guard_report(output_dir, report)
            saved = json.loads((output_dir / "active_document_snapshot.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "blocked")
