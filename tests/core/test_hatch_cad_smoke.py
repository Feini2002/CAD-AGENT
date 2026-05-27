from __future__ import annotations

import unittest

from core.safety.policy import PREVIEW_LAYER
from core.verification.fake_cad_driver import FakeCadDriver, FakeCadEntity
from tests.helpers import artifact_path


class VerifiedHatchFakeDriver(FakeCadDriver):
    def draw_hatch(self, *, boundary_points, pattern="ANSI31", layer=None, layer_role="preview", **_):
        resolved_layer = layer or PREVIEW_LAYER
        self._assert_layer(resolved_layer, layer_role=layer_role)
        boundary_handle = self._handle()
        hatch_handle = self._handle()
        coordinates = [coordinate for point in boundary_points for coordinate in point[:2]]
        self.entities[boundary_handle] = FakeCadEntity(
            handle=boundary_handle,
            object_name="AcDbPolyline",
            layer=resolved_layer,
            Coordinates=coordinates,
            Closed=True,
        )
        self.entities[hatch_handle] = FakeCadEntity(
            handle=hatch_handle,
            object_name="AcDbHatch",
            layer=resolved_layer,
            PatternName=pattern,
            bbox={"min": [0.0, 0.0], "max": [100.0, 80.0]},
        )
        return {
            "handle": hatch_handle,
            "handles": [hatch_handle],
            "boundary_handles": [boundary_handle],
            "created_handles": [boundary_handle, hatch_handle],
            "pattern": pattern,
            "layer": resolved_layer,
        }


class HatchCadSmokeTests(unittest.TestCase):
    def test_hatch_smoke_verifies_hatch_and_boundary_readback(self) -> None:
        from core.verification.hatch_cad_smoke import run_hatch_cad_smoke

        output_dir = artifact_path("hatch_cad_smoke", "verified")
        report = run_hatch_cad_smoke(
            output_dir=output_dir,
            driver_factory=VerifiedHatchFakeDriver,
        )

        self.assertEqual(report["status"], "geometry_verified")
        self.assertEqual(report["evidence_state"], "readback_geometry_verified")
        self.assertTrue(report["geometry_verified"])
        self.assertEqual(report["created_handle_count"], 2)
        self.assertEqual(report["actual"]["type_counts"], {"hatch": 1, "polyline": 1})
        self.assertEqual(report["actual"]["hatch_pattern"], "ANSI31")
        self.assertTrue((output_dir / "hatch_cad_smoke_report.json").is_file())


if __name__ == "__main__":
    unittest.main()
