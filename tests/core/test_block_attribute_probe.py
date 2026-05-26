from __future__ import annotations

import json
import unittest
from pathlib import Path

from core.plan_engine.validate_plan import validate_plan
from core.verification.block_alpha_validation import build_block_alpha_readback_report
from core.verification.block_attribute_probe import (
    check_block_attribute_readback,
    merge_block_readback_checks,
    plan_expects_attribute_readback,
)
from core.verification.evidence_contract import EVIDENCE_DEFERRED_CAD_READBACK, EVIDENCE_READBACK_GEOMETRY_VERIFIED
from core.verification.geometry_checks import check_block_reference_readback, expected_block_reference_from_plan
from core.verification.inspect_dwg import normalize_com_entity
from tests.bootstrap import PROJECT_ROOT


class _FakeAttribute:
    def __init__(self, tag: str, text: str) -> None:
        self.TagString = tag
        self.TextString = text


class _FakeBlockReference:
    ObjectName = "AcDbBlockReference"
    Layer = "CODEX_PREVIEW"
    Handle = "BR-ATTR"
    EffectiveName = "CODEX_TEST_BLOCK_001"
    InsertionPoint = [1200.0, 800.0, 0.0]
    Rotation = 0.0
    XScaleFactor = 1.0
    YScaleFactor = 1.0
    ZScaleFactor = 1.0

    def __init__(self, attributes: list[_FakeAttribute] | None = None) -> None:
        self._attributes = attributes or []

    def GetAttributes(self) -> list[_FakeAttribute]:
        return self._attributes

    def GetBoundingBox(self) -> tuple[list[float], list[float]]:
        return [1200.0, 800.0, 0.0], [2100.0, 1250.0, 0.0]


class BlockAttributeProbeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base_plan = json.loads(
            (PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json").read_text(encoding="utf-8")
        )
        self.probe_plan = json.loads(
            (PROJECT_ROOT / "examples/plans/insert_block_alpha_attribute_probe.json").read_text(encoding="utf-8")
        )

    def test_beta_cad_block_02_probe_plan_validates(self) -> None:
        self.assertEqual(validate_plan(self.probe_plan), [])
        self.assertTrue(plan_expects_attribute_readback(self.probe_plan))

    def test_beta_cad_block_02_rejects_attributes_without_probe_flag(self) -> None:
        plan = json.loads(json.dumps(self.base_plan))
        plan["object"]["attributes"] = {"ROOM": "A"}
        errors = validate_plan(plan)
        self.assertTrue(any("attribute_readback_probe" in error for error in errors))

    def test_beta_cad_block_02_no_attributes_plan_does_not_run_attribute_check(self) -> None:
        expected = expected_block_reference_from_plan(self.base_plan)
        entity = {"handle": "BR1", "type": "block_reference", **expected}
        assessment = check_block_attribute_readback(self.base_plan, entity)
        self.assertEqual(assessment["status"], "not_run")

        geometry_checks = check_block_reference_readback(self.base_plan, entity)
        checks, geometry_verified, _ = merge_block_readback_checks(geometry_checks, assessment)
        self.assertTrue(geometry_verified)
        self.assertTrue(all(check.get("status") == "pass" for check in geometry_checks))

    def test_beta_cad_block_02_missing_attributes_deferred_not_geometry_verified(self) -> None:
        expected = expected_block_reference_from_plan(self.probe_plan)
        entity = {"handle": "BR1", "type": "block_reference", **expected}
        assessment = check_block_attribute_readback(self.probe_plan, entity)
        self.assertEqual(assessment["status"], "deferred")
        self.assertTrue(assessment["blocks_geometry_verified"])

        geometry_checks = check_block_reference_readback(self.probe_plan, entity)
        checks, geometry_verified, evidence_state = merge_block_readback_checks(geometry_checks, assessment)
        self.assertFalse(geometry_verified)
        self.assertEqual(evidence_state, EVIDENCE_DEFERRED_CAD_READBACK)
        deferred = next(check for check in checks if check.get("name") == "attribute_readback")
        self.assertEqual(deferred.get("failure_category"), "attribute_unverified")

    def test_beta_cad_block_02_matching_attributes_allow_geometry_verified(self) -> None:
        expected = expected_block_reference_from_plan(self.probe_plan)
        entity = {
            "handle": "BR1",
            "type": "block_reference",
            **expected,
            "attributes": {"ROOM": "OFFICE-A", "DESK_ID": "D-01"},
        }
        assessment = check_block_attribute_readback(self.probe_plan, entity)
        self.assertEqual(assessment["status"], "pass")

        geometry_checks = check_block_reference_readback(self.probe_plan, entity)
        checks, geometry_verified, _ = merge_block_readback_checks(geometry_checks, assessment)
        self.assertTrue(geometry_verified)

    def test_beta_cad_block_02_readback_report_no_false_positive_without_probe_plan(self) -> None:
        expected = expected_block_reference_from_plan(self.base_plan)
        entity = {"handle": "BR1", "type": "block_reference", **expected}
        report = build_block_alpha_readback_report(
            plan_path=PROJECT_ROOT / "examples/plans/insert_block_alpha_test.json",
            entities=[entity],
            created_handles=["BR1"],
        )
        self.assertEqual(report["status"], "geometry_verified")
        self.assertEqual(report["evidence_state"], EVIDENCE_READBACK_GEOMETRY_VERIFIED)
        attr = report.get("attribute_readback", {})
        self.assertEqual(attr.get("status"), "not_run")

    def test_beta_cad_block_02_readback_report_defers_when_attributes_missing(self) -> None:
        expected = expected_block_reference_from_plan(self.probe_plan)
        entity = {"handle": "BR1", "type": "block_reference", **expected}
        report = build_block_alpha_readback_report(
            plan_path=PROJECT_ROOT / "examples/plans/insert_block_alpha_attribute_probe.json",
            entities=[entity],
            created_handles=["BR1"],
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["evidence_state"], EVIDENCE_DEFERRED_CAD_READBACK)
        self.assertEqual(report["attribute_readback"]["status"], "deferred")

    def test_beta_cad_block_02_inspect_dwg_normalizes_block_attributes(self) -> None:
        entity = normalize_com_entity(
            _FakeBlockReference([_FakeAttribute("ROOM", "OFFICE-A"), _FakeAttribute("DESK_ID", "D-01")])
        )
        self.assertEqual(entity["attributes"], {"ROOM": "OFFICE-A", "DESK_ID": "D-01"})


if __name__ == "__main__":
    unittest.main()
