from __future__ import annotations

import unittest

from core.verification.cad_validation_evidence import cad_validation_evidence_gate_failure
from core.verification.evidence_contract import (
    EVIDENCE_CAD_CAPABILITY_VERIFIED,
    EVIDENCE_DEFERRED_CAD_READBACK,
    EVIDENCE_READBACK_GEOMETRY_VERIFIED,
    GEOMETRY_VERIFIED_BY_READBACK,
    NON_CAD_GEOMETRY_ACCURACY,
)


class CadValidationEvidenceTests(unittest.TestCase):
    def test_no_cad_pass_rejects_geometry_verified_summary(self) -> None:
        error = cad_validation_evidence_gate_failure(
            {
                "status": "pass",
                "include_cad": False,
                "block_alpha_only": False,
                "evidence_summary": {
                    "non_cad_only": False,
                    "readback_geometry_verified_count": 1,
                    "cad_capability_verified_count": 0,
                },
                "steps": [],
            }
        )
        self.assertIn("non_cad_only", error)

    def test_cad_pass_requires_readback_and_capability_evidence(self) -> None:
        error = cad_validation_evidence_gate_failure(
            {
                "status": "pass",
                "include_cad": True,
                "block_alpha_only": False,
                "evidence_summary": {"non_cad_only": False},
                "steps": [
                    {
                        "id": "inspect_readback",
                        "status": "pass",
                        "evidence_state": EVIDENCE_DEFERRED_CAD_READBACK,
                        "geometry_accuracy": NON_CAD_GEOMETRY_ACCURACY,
                    },
                    {
                        "id": "cad_capability_probe",
                        "status": "pass",
                        "evidence_state": EVIDENCE_CAD_CAPABILITY_VERIFIED,
                    },
                ],
                "block_alpha": {},
            }
        )
        self.assertIn("inspect_readback", error)

    def test_cad_pass_accepts_verified_sub_reports(self) -> None:
        error = cad_validation_evidence_gate_failure(
            {
                "status": "pass",
                "include_cad": True,
                "block_alpha_only": False,
                "evidence_summary": {
                    "non_cad_only": False,
                    "readback_geometry_verified_count": 1,
                    "cad_capability_verified_count": 1,
                },
                "steps": [
                    {
                        "id": "inspect_readback",
                        "status": "pass",
                        "evidence_state": EVIDENCE_READBACK_GEOMETRY_VERIFIED,
                        "geometry_accuracy": GEOMETRY_VERIFIED_BY_READBACK,
                    },
                    {
                        "id": "cad_capability_probe",
                        "status": "pass",
                        "evidence_state": EVIDENCE_CAD_CAPABILITY_VERIFIED,
                    },
                ],
                "block_alpha": {"step_id": "block_alpha_readback", "geometry_verified": True},
            }
        )
        self.assertEqual(error, "")


if __name__ == "__main__":
    unittest.main()
