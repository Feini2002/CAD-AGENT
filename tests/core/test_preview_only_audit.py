from __future__ import annotations

import json
import unittest

from core.safety.policy import PREVIEW_LAYER
from core.verification.preview_only_audit import (
    attach_preview_only_audit,
    build_preview_only_audit,
    execution_summary_gate_failure,
    preview_only_audit_check,
    validate_preview_only_audit,
    with_legacy_safety_aliases,
)
from tests.helpers import temporary_artifact_dir


class PreviewOnlyAuditTests(unittest.TestCase):
    def test_build_preview_only_audit_defaults(self) -> None:
        audit = build_preview_only_audit()
        self.assertEqual(audit["layer"], PREVIEW_LAYER)
        self.assertFalse(audit["saved_dwg"])
        self.assertFalse(audit["deleted_entities"])
        self.assertFalse(audit["modified_formal_layers"])

    def test_validate_rejects_missing_and_invalid_fields(self) -> None:
        self.assertTrue(validate_preview_only_audit({"layer": PREVIEW_LAYER}))
        errors = validate_preview_only_audit({"layer": "WALL", "saved_dwg": False, "deleted_entities": False, "modified_formal_layers": False})
        self.assertTrue(any("layer must be" in error for error in errors))
        errors = validate_preview_only_audit(
            {
                "layer": PREVIEW_LAYER,
                "saved_dwg": True,
                "deleted_entities": False,
                "modified_formal_layers": False,
            }
        )
        self.assertTrue(any("saved_dwg" in error for error in errors))

    def test_legacy_aliases_preserve_backward_compatible_keys(self) -> None:
        merged = with_legacy_safety_aliases(build_preview_only_audit())
        self.assertTrue(merged["writes_only_preview_layer"])
        self.assertFalse(merged["saves_dwg"])

    def test_attach_preview_only_audit(self) -> None:
        summary = attach_preview_only_audit({"status": "executed", "created_handles": ["H1"]}, layer=PREVIEW_LAYER)
        self.assertEqual(summary["safety"]["layer"], PREVIEW_LAYER)
        self.assertEqual(preview_only_audit_check(summary["safety"])["status"], "pass")

    def test_execution_summary_gate_failure(self) -> None:
        with temporary_artifact_dir("preview_only_audit") as temp_dir:
            path = temp_dir / "execution_summary.json"
            path.write_text(
                json.dumps(
                    {
                        "status": "executed",
                        "layer": PREVIEW_LAYER,
                        "created_handles": ["H1"],
                        "safety": build_preview_only_audit(),
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.assertEqual(execution_summary_gate_failure(path=path), "")

            bad_path = temp_dir / "bad.json"
            bad_path.write_text(json.dumps({"status": "executed"}), encoding="utf-8")
            failure = execution_summary_gate_failure(path=bad_path)
            self.assertIn("$.safety", failure)

            stdout_failure = execution_summary_gate_failure(stdout=json.dumps({"status": "executed", "created_handles": ["H1"]}))
            self.assertIn("preview-only audit failed", stdout_failure)
