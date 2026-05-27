from __future__ import annotations

import unittest
from pathlib import Path

from core.verification.demand_case_cad_smoke import load_demand_case_cad_manifest, run_demand_case_cad_smoke
from tests.bootstrap import PROJECT_ROOT


class DemandCaseCadSmokeTests(unittest.TestCase):
    def test_manifest_has_ten_cases(self) -> None:
        path = PROJECT_ROOT / "examples" / "capability_proof" / "demand_case_cad_manifest.json"
        manifest = load_demand_case_cad_manifest(path)
        self.assertEqual(len(manifest["cases"]), 10)

    def test_no_cad_deferred(self) -> None:
        report = run_demand_case_cad_smoke(
            root=PROJECT_ROOT,
            no_cad=True,
            skip_benchmark=True,
        )
        self.assertFalse(report.get("geometry_verified", True))


if __name__ == "__main__":
    unittest.main()
