from __future__ import annotations

import json
import unittest

from tests.bootstrap import PROJECT_ROOT

from core.schemas.registry import get_schema_path
from core.schemas.validator import validate_json, validate_value
from core.verification.capability_registry_contract import validate_registry_claim_contracts


class CadCapabilityRegistrySchemaTests(unittest.TestCase):
    def test_minimal_example_validates(self) -> None:
        schema_path = get_schema_path("cad_capability_registry")
        example_path = PROJECT_ROOT / "examples" / "capability_proof" / "minimal_cad_capability_registry.json"
        self.assertEqual(validate_json(schema_path, example_path), [])

    def test_minimal_example_satisfies_claim_contracts(self) -> None:
        example_path = PROJECT_ROOT / "examples" / "capability_proof" / "minimal_cad_capability_registry.json"
        registry = json.loads(example_path.read_text(encoding="utf-8"))
        self.assertEqual(validate_registry_claim_contracts(registry), [])

    def test_invalid_fixture_fails_schema(self) -> None:
        fixture_path = PROJECT_ROOT / "tests" / "fixtures" / "invalid_models" / "cad_capability_registry.invalid.json"
        fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
        schema = json.loads(get_schema_path(fixture["model_type"]).read_text(encoding="utf-8"))
        errors = validate_value(fixture["data"], schema)
        self.assertTrue(errors)
        self.assertTrue(any("claim_level" in error for error in errors))

    def test_schema_allows_verified_without_evidence_object(self) -> None:
        schema = json.loads(get_schema_path("cad_capability_registry").read_text(encoding="utf-8"))
        row = {
            "capability_id": "intent.draw_object.rectangle",
            "display_name": "Missing evidence",
            "category": "intent",
            "claim_level": "verified",
            "ladder_level": "L1",
        }
        errors = validate_value(
            {
                "version": "0.1",
                "registry_id": "contract-check",
                "capabilities": [row],
            },
            schema,
        )
        self.assertEqual(errors, [])

    def test_claim_level_contract_rejects_verified_without_evidence(self) -> None:
        registry = json.loads(
            (PROJECT_ROOT / "examples" / "capability_proof" / "minimal_cad_capability_registry.json").read_text(
                encoding="utf-8"
            )
        )
        registry["capabilities"].append(
            {
                "capability_id": "primitive.line",
                "display_name": "Line primitive",
                "category": "primitive",
                "claim_level": "verified",
                "ladder_level": "L1",
            }
        )
        errors = validate_registry_claim_contracts(registry)
        self.assertTrue(any("evidence" in error for error in errors))

    def test_claim_level_contract_requires_deferred_reason(self) -> None:
        errors = validate_registry_claim_contracts(
            {
                "version": "0.1",
                "registry_id": "deferred-check",
                "capabilities": [
                    {
                        "capability_id": "object.desk",
                        "display_name": "Desk",
                        "category": "object",
                        "claim_level": "deferred",
                        "ladder_level": "L0",
                    }
                ],
            }
        )
        self.assertTrue(any("deferred_reason" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
