from __future__ import annotations

import json
import unittest
from pathlib import Path
from typing import Any

from tests.helpers import artifact_path

from core.verification.cad_capability_probe import run_cad_capability_probe


class FakeCadEntity:
    def __init__(self, *, handle: str, object_name: str, layer: str, **attrs: object) -> None:
        self.Handle = handle
        self.ObjectName = object_name
        self.Layer = layer
        for name, value in attrs.items():
            setattr(self, name, value)


class FakeCadDriver:
    def __init__(self, *, missing_readback_handle: str | None = None) -> None:
        self.doc = type("Doc", (), {"Name": "sample-active.dwg"})()
        self.missing_readback_handle = missing_readback_handle
        self.entities: dict[str, FakeCadEntity] = {}
        self.layers: list[str] = []
        self.next_handle = 100

    def ensure_layer(self, layer: str) -> None:
        self.layers.append(layer)

    def _handle(self) -> str:
        self.next_handle += 1
        return f"H{self.next_handle}"

    def draw_rectangle(self, *, corner1: list[float | int], corner2: list[float | int], layer: str, **_: object) -> dict[str, list[str]]:
        x1, y1, z1 = corner1
        x2, y2, _z2 = corner2
        segments = [
            ([x1, y1, z1], [x2, y1, z1]),
            ([x2, y1, z1], [x2, y2, z1]),
            ([x2, y2, z1], [x1, y2, z1]),
            ([x1, y2, z1], [x1, y1, z1]),
        ]
        handles: list[str] = []
        for start, end in segments:
            handle = self._handle()
            self.entities[handle] = FakeCadEntity(
                handle=handle,
                object_name="AcDbLine",
                layer=layer,
                StartPoint=start,
                EndPoint=end,
            )
            handles.append(handle)
        return {"handles": handles}

    def draw_line(self, *, start_point: list[float | int], end_point: list[float | int], layer: str, **_: object) -> dict[str, str]:
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbLine",
            layer=layer,
            StartPoint=start_point,
            EndPoint=end_point,
        )
        return {"handle": handle}

    def draw_circle(self, *, center: list[float | int], radius: float | int, layer: str, **_: object) -> dict[str, str]:
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbCircle",
            layer=layer,
            Center=center,
            Radius=radius,
        )
        return {"handle": handle}

    def draw_arc(
        self,
        *,
        center: list[float | int],
        radius: float | int,
        start_angle: float | int,
        end_angle: float | int,
        layer: str,
        **_: object,
    ) -> dict[str, str]:
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbArc",
            layer=layer,
            Center=center,
            Radius=radius,
            StartAngle=start_angle,
            EndAngle=end_angle,
        )
        return {"handle": handle}

    def draw_polyline(self, *, points: list[list[float | int]], closed: bool, layer: str, **_: object) -> dict[str, str]:
        handle = self._handle()
        coordinates = [coordinate for point in points for coordinate in point[:2]]
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbPolyline",
            layer=layer,
            Coordinates=coordinates,
            Closed=closed,
        )
        return {"handle": handle}

    def draw_text(self, *, text: str, position: list[float | int], layer: str, **_: object) -> dict[str, str]:
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(
            handle=handle,
            object_name="AcDbText",
            layer=layer,
            TextString=text,
            InsertionPoint=position,
        )
        return {"handle": handle}

    def add_dimension(self, *, layer: str, **_: object) -> dict[str, str]:
        handle = self._handle()
        self.entities[handle] = FakeCadEntity(handle=handle, object_name="AcDbAlignedDimension", layer=layer)
        return {"handle": handle}

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, Any]]:
        from core.verification.inspect_dwg import normalize_com_entity

        entities = []
        for handle in handles:
            if handle == self.missing_readback_handle:
                continue
            entity = self.entities[handle]
            normalized = normalize_com_entity(entity)
            if layer is None or normalized["layer"] == layer:
                entities.append(normalized)
        return entities


class CadCapabilityProbeTests(unittest.TestCase):
    def test_probe_creates_preview_entities_and_verifies_handle_readback(self) -> None:
        output_dir = artifact_path("cad_capability_probe", "pass")

        report = run_cad_capability_probe(driver_factory=FakeCadDriver, output_dir=output_dir)

        self.assertEqual(report["status"], "cad_capability_verified")
        self.assertEqual(report["active_document"], "sample-active.dwg")
        self.assertEqual(report["layer"], "CODEX_PREVIEW")
        self.assertEqual(len(report["created_handles"]), 11)
        self.assertEqual(
            report["actual"]["type_counts"],
            {"arc": 1, "circle": 1, "dimension": 2, "line": 5, "polyline": 1, "text": 1},
        )
        self.assertTrue(all(check["status"] == "pass" for check in report["checks"]))
        self.assertTrue((output_dir / "cad_capability_probe.json").exists())

        saved = json.loads((output_dir / "cad_capability_probe.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "cad_capability_verified")

    def test_probe_fails_when_created_handle_is_not_read_back(self) -> None:
        report = run_cad_capability_probe(
            driver_factory=lambda: FakeCadDriver(missing_readback_handle="H103"),
            output_dir=artifact_path("cad_capability_probe", "missing_handle"),
        )

        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["failure_category"], "readback_failed")
        self.assertEqual(checks["handle_readback_count"]["status"], "fail")
        self.assertIn("H103", checks["handle_readback_count"]["message"])

    def test_probe_reports_connection_failure_as_external_blocker(self) -> None:
        def raise_connection_error() -> FakeCadDriver:
            raise RuntimeError("No active AutoCAD.Application instance is available.")

        report = run_cad_capability_probe(
            driver_factory=raise_connection_error,
            output_dir=artifact_path("cad_capability_probe", "connection_failure"),
        )

        self.assertEqual(report["status"], "external_blocker")
        self.assertEqual(report["failure_category"], "cad_connection_failed")
        self.assertIn("No active AutoCAD", report["error"])


if __name__ == "__main__":
    unittest.main()
