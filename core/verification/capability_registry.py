"""Load, validate, and persist CAD capability registry JSON (V-PROOF-02 / V-PROOF-03)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_root
from core.schemas.registry import get_schema_path
from core.schemas.validator import validate_value
from core.verification.capability_registry_contract import validate_registry_claim_contracts

DEFAULT_REGISTRY_PATH = Path("examples/capability_proof/cad_capability_registry.json")


@dataclass
class RegistryBundle:
    registry: dict[str, Any]
    path: Path
    project_root: Path
    index: dict[str, dict[str, Any]]

    def get_row(self, capability_id: str) -> dict[str, Any] | None:
        return self.index.get(capability_id)


def load_capability_registry(path: Path, *, project_root: Path) -> dict[str, Any]:
    registry_path = resolve_under_project_root(project_root, path, label="registry_path")
    if not registry_path.is_file():
        raise FileNotFoundError(f"Capability registry not found: {registry_path}")
    data = json.loads(registry_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Capability registry must be a JSON object.")
    return data


def validate_capability_registry(registry: dict[str, Any]) -> list[str]:
    schema = json.loads(get_schema_path("cad_capability_registry").read_text(encoding="utf-8"))
    errors = validate_value(registry, schema)
    errors.extend(validate_registry_claim_contracts(registry))
    return errors


def index_capability_rows(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in registry.get("capabilities", []):
        if isinstance(row, dict) and row.get("capability_id"):
            index[str(row["capability_id"])] = row
    return index


def load_registry_bundle(path: Path, *, project_root: Path) -> RegistryBundle:
    root = project_root.resolve()
    registry_path = resolve_under_project_root(root, path, label="registry_path")
    registry = load_capability_registry(registry_path, project_root=root)
    return RegistryBundle(
        registry=registry,
        path=registry_path,
        project_root=root,
        index=index_capability_rows(registry),
    )


def save_capability_registry(
    registry: dict[str, Any],
    path: Path,
    *,
    project_root: Path,
) -> list[str]:
    """Validate then write registry JSON. Returns validation errors (empty if saved)."""

    errors = validate_capability_registry(registry)
    if errors:
        return errors
    registry_path = resolve_under_project_root(project_root, path, label="registry_path")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return []
