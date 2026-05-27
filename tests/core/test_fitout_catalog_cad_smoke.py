from __future__ import annotations

import unittest

from core.verification.fake_cad_driver import FakeCadDriver
from core.verification.fitout_catalog_cad_smoke import (
    build_fitout_catalog_draw_plan,
    run_fitout_catalog_cad_smoke,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class FitoutCatalogCadSmokeTests(unittest.TestCase):
    def test_build_plan_validates(self) -> None:
        plan = build_fitout_catalog_draw_plan(
            catalog_object_id="desk",
            catalog_row={
                "core_object_type": "desk",
                "default_size": {"width": 1400, "depth": 700, "height": 750},
            },
            display_name="办公桌",
        )
        self.assertEqual(plan["intent"], "draw_object")
        self.assertEqual(plan["object"]["type"], "desk")

    def test_fake_cad_smoke_single_catalog_row(self) -> None:
        output_dir = artifact_path("fitout_catalog_cad_smoke", "desk")
        report = run_fitout_catalog_cad_smoke(
            root=PROJECT_ROOT,
            output_dir=output_dir,
            no_cad=False,
            driver=FakeCadDriver(),
            catalog_object_ids=["desk"],
        )
        self.assertEqual(report["geometry_verified_catalog_object_count"], 1)
        self.assertEqual(report["catalog_objects"][0]["status"], "pass")


if __name__ == "__main__":
    unittest.main()
