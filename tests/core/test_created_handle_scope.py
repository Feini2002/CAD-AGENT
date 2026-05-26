from __future__ import annotations

import unittest
from pathlib import Path

from core.verification.created_handle_scope import (
    analyze_created_handle_scope,
    created_handle_scope_check,
    created_handle_scope_ok,
)
from core.verification.verification_report import build_verification_report
from tests.bootstrap import PROJECT_ROOT


class CreatedHandleScopeTests(unittest.TestCase):
    def test_analyze_scope_counts_hits_misses_and_extras(self) -> None:
        entities = [
            {"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW"},
            {"handle": "H2", "type": "line", "layer": "CODEX_PREVIEW"},
            {"handle": "HX", "type": "line", "layer": "CODEX_PREVIEW"},
        ]
        scope = analyze_created_handle_scope(input_handles=["H1", "H2", "H9"], readback_entities=entities)
        self.assertEqual(scope["input_handle_count"], 3)
        self.assertEqual(scope["hit_count"], 2)
        self.assertEqual(scope["miss_count"], 1)
        self.assertEqual(scope["extra_entity_count"], 1)
        self.assertFalse(created_handle_scope_ok(scope))
        self.assertEqual(created_handle_scope_check(scope)["status"], "fail")

    def test_verification_report_records_created_handle_scope(self) -> None:
        entities = [
            {"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 0, 0], "end_point": [1800, 0, 0]},
            {"handle": "H2", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 0, 0], "end_point": [1800, 600, 0]},
            {"handle": "H3", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [1800, 600, 0], "end_point": [0, 600, 0]},
            {"handle": "H4", "type": "line", "layer": "CODEX_PREVIEW", "start_point": [0, 600, 0], "end_point": [0, 0, 0]},
            {"handle": "H5", "type": "text", "layer": "CODEX_PREVIEW", "text": "测试柜", "position": [900, 300, 0]},
            {"handle": "H6", "type": "dimension", "layer": "CODEX_PREVIEW"},
            {"handle": "H7", "type": "dimension", "layer": "CODEX_PREVIEW"},
        ]
        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            created_handles=["H1", "H2", "H3", "H4", "H5", "H6", "H7"],
        )
        scope = report["actual"]["created_handle_scope"]
        self.assertEqual(scope["miss_count"], 0)
        self.assertEqual(scope["extra_entity_count"], 0)
        self.assertEqual(report["status"], "geometry_verified")

    def test_missing_created_handle_fails_scope_and_geometry_verified(self) -> None:
        entities = [{"handle": "H1", "type": "line", "layer": "CODEX_PREVIEW"}]
        report = build_verification_report(
            plan_path=PROJECT_ROOT / "examples" / "plans" / "draw_test_cabinet.json",
            entities=entities,
            created_handles=["H1", "H2"],
        )
        scope = report["actual"]["created_handle_scope"]
        self.assertEqual(scope["miss_count"], 1)
        self.assertNotEqual(report["status"], "geometry_verified")
        checks = {check["name"]: check for check in report["checks"]}
        self.assertEqual(checks["created_handles_scope"]["status"], "fail")
