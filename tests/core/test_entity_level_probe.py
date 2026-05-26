from __future__ import annotations

import unittest

from core.verification.entity_level_evidence import (
    FAILURE_HATCH_UNVERIFIED,
    PREVIEW_LAYER,
    assess_entity_level_evidence,
    build_hatch_deferred_entry,
    compare_polyline_entity,
    entity_level_evidence_allows_probe_pass,
    layer_mapping_check,
)
from core.verification.evidence_contract import (
    ENTITY_CONTRACTS,
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE,
    SCREENSHOT_NOT_APPLICABLE,
    apply_capability_probe_contract,
    validate_capability_probe_evidence,
)


class EntityLevelEvidenceTests(unittest.TestCase):
    def test_layer_mapping_preview_pass(self) -> None:
        check = layer_mapping_check(
            write_layer=PREVIEW_LAYER,
            layer_role="preview",
            readback_layer=PREVIEW_LAYER,
        )
        self.assertEqual(check["status"], "pass")

    def test_polyline_entity_comparison_pass(self) -> None:
        write = {
            "points": [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0]],
            "closed": True,
            "layer": PREVIEW_LAYER,
            "layer_role": "preview",
        }
        entity = {
            "type": "polyline",
            "points": [[0.0, 0.0], [100.0, 0.0], [100.0, 100.0]],
            "closed": True,
            "layer": PREVIEW_LAYER,
        }
        checks = compare_polyline_entity(write, entity)
        self.assertTrue(all(check["status"] == "pass" for check in checks))

    def test_hatch_deferred_entry(self) -> None:
        entry = build_hatch_deferred_entry(
            {
                "pattern": "ANSI31",
                "boundary_points": [[0, 0], [100, 0], [100, 100]],
                "layer": PREVIEW_LAYER,
                "layer_role": "preview",
            }
        )
        self.assertEqual(entry["primitive"], "hatch")
        self.assertEqual(entry["status"], "deferred")
        self.assertEqual(entry["failure_category"], FAILURE_HATCH_UNVERIFIED)

    def test_assess_entity_level_evidence_polyline_and_hatch(self) -> None:
        write_records = [
            {
                "primitive": "polyline",
                "handle": "H200",
                "write": {
                    "points": [[10.0, 10.0], [20.0, 20.0]],
                    "closed": False,
                    "layer": PREVIEW_LAYER,
                    "layer_role": "preview",
                },
            },
            build_hatch_deferred_entry(
                {
                    "pattern": "ANSI31",
                    "boundary_points": [[0, 0], [50, 0]],
                    "layer": PREVIEW_LAYER,
                    "layer_role": "preview",
                }
            ),
        ]
        entities = {
            "H200": {
                "handle": "H200",
                "type": "polyline",
                "points": [[10.0, 10.0], [20.0, 20.0]],
                "closed": False,
                "layer": PREVIEW_LAYER,
            }
        }
        evidence = assess_entity_level_evidence(write_records=write_records, entities_by_handle=entities)
        self.assertTrue(entity_level_evidence_allows_probe_pass(evidence))
        polyline_entry = next(item for item in evidence if item["primitive"] == "polyline")
        self.assertEqual(polyline_entry["status"], "pass")

    def test_entity_contracts_include_hatch_deferred(self) -> None:
        hatch = ENTITY_CONTRACTS["hatch"]
        self.assertEqual(hatch["implementation_status"], "deferred")

    def test_validate_capability_probe_requires_entity_evidence(self) -> None:
        report = apply_capability_probe_contract(
            {
                "status": "cad_capability_verified",
                "entity_evidence": [],
            }
        )
        self.assertEqual(report["evidence_state"], EVIDENCE_CAD_CAPABILITY_VERIFIED)
        self.assertEqual(report["geometry_accuracy"], GEOMETRY_VERIFIED_BY_CAPABILITY_PROBE)
        self.assertEqual(report["screenshot_role"], SCREENSHOT_NOT_APPLICABLE)
        self.assertIn("entity_evidence incomplete", validate_capability_probe_evidence(report))


if __name__ == "__main__":
    unittest.main()
