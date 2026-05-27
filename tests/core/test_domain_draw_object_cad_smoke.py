"""Tests for domain draw_object CAD smoke manifest."""

from __future__ import annotations

import unittest
from pathlib import Path

from core.path_safety import find_project_root
from core.verification.domain_draw_object_cad_smoke import (
    DOMAIN_DRAW_DOMAINS,
    run_domain_draw_object_cad_smoke,
)


PROJECT_ROOT = find_project_root(Path(__file__))


class DomainDrawObjectCadSmokeTests(unittest.TestCase):
    def test_no_cad_deferred_for_all_domains(self) -> None:
        report = run_domain_draw_object_cad_smoke(root=PROJECT_ROOT, no_cad=True)
        self.assertEqual(report["domain_count"], len(DOMAIN_DRAW_DOMAINS))
        self.assertFalse(report["geometry_verified"])
        for row in report["domains"]:
            self.assertEqual(row["cad_execution_status"], "deferred")


if __name__ == "__main__":
    unittest.main()
