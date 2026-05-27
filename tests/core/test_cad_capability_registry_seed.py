from __future__ import annotations

import json
import unittest
from collections import Counter

from tests.bootstrap import PROJECT_ROOT

from core.schemas.registry import get_schema_path
from core.schemas.validator import validate_json, validate_value
from core.verification.capability_registry_contract import validate_registry_claim_contracts
from core.verification.capability_registry_seed import build_seed_registry


class CadCapabilityRegistrySeedTests(unittest.TestCase):
    def test_seed_registry_meets_volume_and_validates(self) -> None:
        registry = build_seed_registry()
        self.assertGreaterEqual(len(registry["capabilities"]), 200)

        schema_path = get_schema_path("cad_capability_registry")
        schema_errors = validate_value(registry, json.loads(schema_path.read_text(encoding="utf-8")))
        self.assertEqual(schema_errors, [], schema_errors)
        self.assertEqual(validate_registry_claim_contracts(registry), [])

    def test_seed_file_on_disk_matches_builder(self) -> None:
        path = PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json"
        self.assertTrue(path.is_file(), "Run scripts/build_cad_capability_registry_seed.py to materialize the seed file.")
        on_disk = json.loads(path.read_text(encoding="utf-8"))
        built = build_seed_registry()
        self.assertEqual(on_disk["registry_id"], built["registry_id"])
        built_ids = {str(row["capability_id"]) for row in built["capabilities"]}
        disk_ids = {str(row["capability_id"]) for row in on_disk["capabilities"]}
        renamed_seed_ids = {
            "symbol.spec.symbol_table_meeting_plan": "symbol.spec.surface_table_plan",
            "symbol.spec.symbol_monitor_plan": "symbol.spec.surface_monitor_plan",
            "symbol.spec.symbol_rug_plan": "symbol.spec.surface_rug_plan",
        }
        optional_vproof_spec_ids = {"symbol.spec.symbol_sofa_plan"}
        missing_on_disk: list[str] = []
        for capability_id in built_ids:
            if capability_id in disk_ids:
                continue
            alias = renamed_seed_ids.get(capability_id)
            if alias and alias in disk_ids:
                continue
            missing_on_disk.append(capability_id)
        self.assertEqual(missing_on_disk, [], f"disk registry missing seed ids: {missing_on_disk}")
        self.assertGreaterEqual(
            len(on_disk["capabilities"]),
            len(built["capabilities"]) - len(renamed_seed_ids) - len(optional_vproof_spec_ids),
        )

    def test_seed_claim_levels_are_mostly_non_verified(self) -> None:
        registry = build_seed_registry()
        counts = Counter(str(row.get("claim_level")) for row in registry["capabilities"])
        verified_like = counts.get("verified", 0) + counts.get("showcase", 0)
        self.assertEqual(verified_like, 0)
        self.assertGreater(counts.get("deferred", 0), 50)
        self.assertGreater(counts.get("smoke", 0), 30)
        self.assertGreater(counts.get("none", 0), 20)

    def test_seed_registry_json_file_validates(self) -> None:
        path = PROJECT_ROOT / "examples" / "capability_proof" / "cad_capability_registry.json"
        errors = validate_json(get_schema_path("cad_capability_registry"), path)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
