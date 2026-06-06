from __future__ import annotations

import json
from pathlib import Path
import unittest

from tests.helpers import temporary_artifact_dir


A1_FRAME = {
    "handle": "A1_TABLE_FRAME",
    "layer": "CODEX_PREVIEW",
    "bbox": {"min": [0.0, 0.0], "max": [100.0, 100.0]},
    "entityType": "LWPOLYLINE",
    "zone": "A1",
}
A2_BAD_TEXT = {
    "handle": "A2_BAD_TEXT",
    "layer": "CODEX_PREVIEW",
    "bbox": {"min": [200.0, 20.0], "max": [240.0, 40.0]},
    "entityType": "TEXT",
    "zone": "A2",
}
A1_ZONE = {
    "zoneId": "A1",
    "bbox": {"min": [-20.0, -20.0], "max": [140.0, 140.0]},
}
A2_ZONE = {
    "zoneId": "A2",
    "bbox": {"min": [180.0, -20.0], "max": [280.0, 140.0]},
}


def _reasons(report: dict[str, object]) -> str:
    return "; ".join(str(item) for item in report.get("blockingReasons", []))


class DeleteScopeAndNeighborGateTests(unittest.TestCase):
    def test_cleanup_without_handles_or_bbox_blocks_delete(self) -> None:
        from core.orchestrator.delete_neighbor_gates import build_delete_scope_gate

        report = build_delete_scope_gate(
            {
                "operation": "cleanup",
                "sourceSpec": "whole_codex_preview",
                "targetLayer": "CODEX_PREVIEW",
                "victimEntities": [A1_FRAME],
            }
        )

        self.assertEqual(report["status"], "fail")
        self.assertFalse(report["mayExecuteCad"])
        self.assertIn("delete scope missing", _reasons(report))
        self.assertIn("global source whole_codex_preview forbidden", _reasons(report))

    def test_scoped_delete_reports_victim_preview_and_passes(self) -> None:
        from core.orchestrator.delete_neighbor_gates import build_delete_scope_gate

        report = build_delete_scope_gate(
            {
                "operation": "delete_replace",
                "targetHandles": ["A2_BAD_TEXT"],
                "targetLayer": "CODEX_PREVIEW",
                "victimEntities": [A2_BAD_TEXT],
                "protectedZones": [A1_ZONE],
                "adjacentZones": [A2_ZONE],
            }
        )

        self.assertEqual(report["status"], "pass")
        self.assertTrue(report["mayExecuteCad"])
        self.assertEqual(report["victimSetPreview"][0]["handle"], "A2_BAD_TEXT")
        self.assertEqual(report["victimSetPreview"][0]["zone"], "A2")
        self.assertIn("victim_set_preview=1", report["checked"])

    def test_victim_inside_protected_zone_blocks_local_repair_delete(self) -> None:
        from core.orchestrator.delete_neighbor_gates import build_delete_scope_gate

        report = build_delete_scope_gate(
            {
                "operation": "delete_replace",
                "targetHandles": ["A1_TABLE_FRAME"],
                "targetLayer": "CODEX_PREVIEW",
                "victimEntities": [A1_FRAME],
                "protectedZones": [A1_ZONE],
                "adjacentZones": [A2_ZONE],
            }
        )

        self.assertEqual(report["status"], "fail")
        self.assertFalse(report["mayExecuteCad"])
        self.assertIn("victim A1_TABLE_FRAME intersects protected zone A1", _reasons(report))

    def test_nearby_placement_without_occupied_bbox_check_blocks(self) -> None:
        from core.orchestrator.delete_neighbor_gates import build_neighbor_protection_gate

        report = build_neighbor_protection_gate(
            {
                "operation": "nearby_place",
                "targetBbox": {"min": [110.0, 0.0], "max": [160.0, 40.0]},
            }
        )

        self.assertEqual(report["status"], "fail")
        self.assertIn("occupied bbox check missing", _reasons(report))

    def test_nearby_placement_collision_blocks(self) -> None:
        from core.orchestrator.delete_neighbor_gates import build_neighbor_protection_gate

        report = build_neighbor_protection_gate(
            {
                "operation": "nearby_place",
                "targetBbox": {"min": [90.0, 20.0], "max": [150.0, 60.0]},
                "occupiedBboxes": [A1_FRAME],
            }
        )

        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["collisions"][0]["handle"], "A1_TABLE_FRAME")
        self.assertIn("target bbox collides with occupied bbox A1_TABLE_FRAME", _reasons(report))

    def test_neighbor_diff_blocks_missing_a1_frame_after_a2_repair(self) -> None:
        from core.orchestrator.delete_neighbor_gates import build_neighbor_protection_gate

        report = build_neighbor_protection_gate(
            {
                "operation": "delete_replace",
                "neighborBefore": [A1_FRAME],
                "neighborAfter": [],
            }
        )

        self.assertEqual(report["status"], "fail")
        self.assertEqual(report["neighborDiff"]["missingHandles"], ["A1_TABLE_FRAME"])
        self.assertIn("neighbor A1_TABLE_FRAME missing after execution", _reasons(report))

    def test_gate_writers_emit_closeout_report_files(self) -> None:
        from core.orchestrator.delete_neighbor_gates import (
            DELETE_SCOPE_GATE_FILE,
            NEIGHBOR_PROTECTION_FILE,
            write_delete_scope_gate,
            write_neighbor_protection_gate,
        )

        with temporary_artifact_dir("delete_neighbor_gate_writers") as root:
            run_dir = Path(root) / "output" / "runs" / "demo"
            delete_report = write_delete_scope_gate(
                run_dir,
                {
                    "operation": "delete_replace",
                    "targetHandles": ["A2_BAD_TEXT"],
                    "targetLayer": "CODEX_PREVIEW",
                    "victimEntities": [A2_BAD_TEXT],
                    "protectedZones": [A1_ZONE],
                },
            )
            neighbor_report = write_neighbor_protection_gate(
                run_dir,
                {
                    "operation": "nearby_place",
                    "targetBbox": {"min": [130.0, 0.0], "max": [170.0, 40.0]},
                    "occupiedBboxes": [A1_FRAME],
                },
            )

            delete_path = run_dir / "cad_reports" / DELETE_SCOPE_GATE_FILE
            neighbor_path = run_dir / "cad_reports" / NEIGHBOR_PROTECTION_FILE
            self.assertTrue(delete_path.is_file())
            self.assertTrue(neighbor_path.is_file())
            self.assertEqual(json.loads(delete_path.read_text(encoding="utf-8"))["status"], delete_report["status"])
            self.assertEqual(json.loads(neighbor_path.read_text(encoding="utf-8"))["status"], neighbor_report["status"])


if __name__ == "__main__":
    unittest.main()
