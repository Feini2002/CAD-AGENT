#!/usr/bin/env python
"""Write examples/capability_proof/cad_capability_registry.json from repo inventories."""

from __future__ import annotations

import json
import sys

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT

from core.schemas.registry import get_schema_path
from core.schemas.validator import validate_value
from core.verification.capability_registry_contract import validate_registry_claim_contracts
from core.verification.capability_registry_seed import build_seed_registry, write_seed_registry


def main() -> int:
    path = write_seed_registry()
    registry = build_seed_registry()
    schema = json.loads(get_schema_path("cad_capability_registry").read_text(encoding="utf-8"))
    schema_errors = validate_value(registry, schema)
    contract_errors = validate_registry_claim_contracts(registry)
    count = len(registry["capabilities"])
    print(f"Wrote {path} ({count} capabilities)")
    if schema_errors:
        print("SCHEMA ERRORS:")
        for error in schema_errors:
            print(f"  - {error}")
    if contract_errors:
        print("CONTRACT ERRORS:")
        for error in contract_errors:
            print(f"  - {error}")
    if schema_errors or contract_errors:
        return 1
    if count < 200:
        print(f"WARNING: expected >= 200 rows, got {count}")
        return 1
    print("VALID SEED REGISTRY")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
