"""Load and validate commercial_fitout Scene Product Alpha scope fixtures."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.agents.scene_boundary_scan import scan_agent_tree
from core.schemas.validator import validate_value

PROJECT_ROOT = Path(__file__).resolve().parents[2]
AGENT_ROOT = PROJECT_ROOT / "agents" / "commercial_fitout"
DEFAULT_SCOPE_PATH = AGENT_ROOT / "subscenes.json"
SCOPE_DOC_PATH = AGENT_ROOT / "SCOPE.md"
SCOPE_SCHEMA_PATH = PROJECT_ROOT / "core" / "schemas" / "commercial_fitout_scope.schema.json"

PRIMARY_SUBSCENE_IDS = frozenset({"open_office", "meeting_room", "reception"})
REQUIRED_NOT_CLAIM = "full_construction_documents"


def load_commercial_fitout_scope(path: Path | None = None) -> dict[str, Any]:
    scope_path = path or DEFAULT_SCOPE_PATH
    return json.loads(scope_path.read_text(encoding="utf-8"))


def validate_commercial_fitout_scope(scope: dict[str, Any]) -> list[str]:
    schema = json.loads(SCOPE_SCHEMA_PATH.read_text(encoding="utf-8"))
    return validate_value(scope, schema)


def assert_scope_contract(scope: dict[str, Any] | None = None) -> None:
    """Raise AssertionError when scope fixture or agent tree violates C-CFIT-01 contract."""

    data = scope or load_commercial_fitout_scope()
    errors = validate_commercial_fitout_scope(data)
    if errors:
        raise AssertionError("commercial_fitout scope invalid: " + "; ".join(errors))

    primary = set(data.get("primary_subscenes", []))
    if primary != PRIMARY_SUBSCENE_IDS:
        raise AssertionError(f"primary_subscenes must be {sorted(PRIMARY_SUBSCENE_IDS)!r}, got {sorted(primary)!r}")

    not_claim = set(data.get("delivery_commitments", {}).get("explicitly_not", []))
    if REQUIRED_NOT_CLAIM not in not_claim:
        raise AssertionError(f"delivery_commitments.explicitly_not must include {REQUIRED_NOT_CLAIM!r}")

    subscene_ids = {item["subscene_id"] for item in data.get("subscenes", []) if isinstance(item, dict)}
    if subscene_ids != PRIMARY_SUBSCENE_IDS:
        raise AssertionError(f"subscenes must cover {sorted(PRIMARY_SUBSCENE_IDS)!r}, got {sorted(subscene_ids)!r}")

    if not SCOPE_DOC_PATH.is_file():
        raise AssertionError(f"missing scope document: {SCOPE_DOC_PATH}")

    violations = scan_agent_tree(AGENT_ROOT)
    if violations:
        detail = "; ".join(f"{v.relative_path}:{v.rule_id}" for v in violations)
        raise AssertionError(f"commercial_fitout boundary scan failed: {detail}")
