from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.verification.capability_coverage import build_capability_coverage_trend_report
from core.verification.capability_registry import validate_capability_registry
from core.verification.trend_dashboard import (
    DASHBOARD_ROLLUP_CAPABILITY_ID,
    VPROOF_71_BOUNDARY_DOC,
    VPROOF_71_PACKAGE_ID,
    assert_vproof_71_trend_dashboard_contract,
    build_capability_trend_dashboard,
    build_trend_dashboard_registry_rows,
    load_trend_dashboard_sources,
    merge_trend_dashboard_registry_rows,
    run_vproof_71_trend_dashboard_sync,
    validate_capability_trend_dashboard,
)
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


def _minimal_coverage_trend_path(output_dir: Path) -> Path:
    coverage = {
        "version": "0.1",
        "status": "pass",
        "generated_at": "2026-05-28T00:00:00Z",
        "summary": {
            "total_count": 10,
            "verified_count": 4,
            "showcase_count": 1,
            "cad_proof_coverage_percent": 50.0,
            "cad_strength_headline_percent": 12.5,
            "highest_proven_ladder_level": "L3",
        },
    }
    coverage_path = output_dir / "cad_capability_coverage.json"
    coverage_path.write_text(json.dumps(coverage, indent=2), encoding="utf-8")
    trend = build_capability_coverage_trend_report(
        coverage_report=coverage,
        coverage_report_path=coverage_path,
        project_root=PROJECT_ROOT,
    )
    trend_path = output_dir / "evidence_trend" / "capability_coverage_trend.json"
    trend_path.parent.mkdir(parents=True, exist_ok=True)
    trend_path.write_text(json.dumps(trend, indent=2), encoding="utf-8")
    return trend_path


class Vproof71TrendDashboardTests(unittest.TestCase):
    def test_build_dashboard_with_fixture_sources(self) -> None:
        output_dir = artifact_path("vproof_71", "dashboard_fixture")
        output_dir.mkdir(parents=True, exist_ok=True)
        trend_path = _minimal_coverage_trend_path(output_dir)
        rel_trend = str(trend_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        rel_coverage = str((output_dir / "cad_capability_coverage.json").relative_to(PROJECT_ROOT)).replace(
            "\\", "/"
        )

        sources = {
            "version": "0.1",
            "coverage_report_path": rel_coverage,
            "panels": [
                {
                    "panel_id": "capability_coverage",
                    "source_kind": "capability_coverage",
                    "required": True,
                    "trend_report_paths": [rel_trend],
                    "coverage_report_path": rel_coverage,
                },
                {
                    "panel_id": "local_cad_regression",
                    "source_kind": "local_cad_regression",
                    "required": False,
                    "trend_report_paths": ["missing/local_cad_regression_trend.json"],
                },
            ],
        }

        dashboard = build_capability_trend_dashboard(
            project_root=PROJECT_ROOT,
            sources=sources,
            output_dir=output_dir,
        )
        self.assertEqual(dashboard["status"], "pass")
        self.assertEqual(validate_capability_trend_dashboard(dashboard, project_root=PROJECT_ROOT), [])
        self.assertEqual(dashboard["coverage_headline"]["cad_strength_headline_percent"], 12.5)

    def test_boundary_doc_states_claim_limits(self) -> None:
        text = (PROJECT_ROOT / VPROOF_71_BOUNDARY_DOC).read_text(encoding="utf-8")
        for phrase in (
            "V-PROOF-71",
            "trend.dashboard.rollup",
            "LCAD-11",
            "claim_level",
            "smoke",
            "不得声称",
            "geometry_verified",
            "cad_strength_headline_percent",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_registry_rows_count(self) -> None:
        rows = build_trend_dashboard_registry_rows(output_root="output/validation_runs/vproof-71-fixture")
        self.assertEqual(len(rows), 4)
        self.assertEqual(rows[0]["capability_id"], DASHBOARD_ROLLUP_CAPABILITY_ID)

    def test_sync_dry_run_with_fixture(self) -> None:
        output_dir = artifact_path("vproof_71", "sync_dry_run")
        output_dir.mkdir(parents=True, exist_ok=True)
        _minimal_coverage_trend_path(output_dir)
        rel_trend = str((output_dir / "evidence_trend" / "capability_coverage_trend.json").relative_to(PROJECT_ROOT))
        rel_coverage = str((output_dir / "cad_capability_coverage.json").relative_to(PROJECT_ROOT))
        sources_path = output_dir / "trend_dashboard_sources.json"
        sources_path.write_text(
            json.dumps(
                {
                    "coverage_report_path": rel_coverage,
                    "panels": [
                        {
                            "panel_id": "capability_coverage",
                            "source_kind": "capability_coverage",
                            "required": True,
                            "trend_report_paths": [rel_trend],
                            "coverage_report_path": rel_coverage,
                        }
                    ],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        summary = run_vproof_71_trend_dashboard_sync(
            project_root=PROJECT_ROOT,
            output_dir=output_dir,
            sources_path=sources_path,
            dry_run=True,
            refresh_coverage=False,
        )
        self.assertEqual(summary["package_id"], VPROOF_71_PACKAGE_ID)
        self.assertEqual(summary["dashboard_status"], "pass")
        self.assertEqual(summary["writeback_rejected_count"], 0)

    def test_merge_registry_validates(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        merge_trend_dashboard_registry_rows(registry, build_trend_dashboard_registry_rows(output_root="fixture"))
        self.assertEqual(validate_capability_registry(registry), [])

    def test_canonical_sources_file_loads(self) -> None:
        sources = load_trend_dashboard_sources(project_root=PROJECT_ROOT)
        panel_ids = {panel["panel_id"] for panel in sources["panels"]}
        self.assertIn("capability_coverage", panel_ids)

    def test_live_registry_contract_when_rows_present(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples/capability_proof/cad_capability_registry.json").read_text(encoding="utf-8")
        )
        index = {row["capability_id"]: row for row in registry.get("capabilities", [])}
        if DASHBOARD_ROLLUP_CAPABILITY_ID not in index:
            self.skipTest("registry rows not synced yet")
        assert_vproof_71_trend_dashboard_contract(project_root=PROJECT_ROOT)


if __name__ == "__main__":
    unittest.main()
