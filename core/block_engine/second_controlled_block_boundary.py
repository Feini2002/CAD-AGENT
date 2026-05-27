"""RBLOCK-05: second controlled test block metadata boundary."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.block_engine.block_library import load_block_library, object_spec_to_block_reference, validate_block_library
from core.plan_engine.block_alpha_plan import (
    CONTROLLED_BLOCK_ALLOWLIST,
    CONTROLLED_BLOCK_ID,
    CONTROLLED_BLOCK_NAME,
    validate_insert_block_alpha,
)
from core.schemas.validator import validate_json

DEFAULT_MANIFEST_REL = "examples/capability_proof/second_controlled_block_manifest.json"
RBLOCK_05_PACKAGE_ID = "RBLOCK-05-SECOND-CONTROLLED-BLOCK"
RBLOCK_05_BOUNDARY_DOC = "docs/verification/rblock_05_second_controlled_block.md"

SECOND_CONTROLLED_BLOCK_ID = "controlled-test-block-002"
SECOND_CONTROLLED_BLOCK_NAME = "CODEX_TEST_BLOCK_002"
SECOND_CONTROLLED_FOOTPRINT = {"width": 600, "depth": 300}


def default_manifest_path(root: Path) -> Path:
    return root / DEFAULT_MANIFEST_REL


def load_second_controlled_block_manifest(path: Path) -> dict[str, Any]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError(f"{path} must be a JSON object")
    if manifest.get("manifest_id") != "second-controlled-block-01":
        raise ValueError(f"unexpected manifest_id: {manifest.get('manifest_id')!r}")
    return manifest


def _library_block(library: dict[str, Any], block_id: str) -> dict[str, Any] | None:
    for block in library.get("blocks", []):
        if isinstance(block, dict) and block.get("block_id") == block_id:
            return block
    return None


def assert_insert_block_alpha_accepts_second_controlled_block() -> None:
    """V-PROOF-41 widens insert_block_alpha to the second controlled test block only."""

    probe_plan = {
        "intent": "insert_block_alpha",
        "object": {
            "type": "block_reference",
            "block_id": SECOND_CONTROLLED_BLOCK_ID,
            "name": "Second Controlled Probe",
            "cad_identity": {"block_name": SECOND_CONTROLLED_BLOCK_NAME},
        },
        "placement": {"mode": "absolute", "base_point": [0, 0, 0], "rotation": 0, "scale": [1, 1, 1]},
        "drawing": {"layer": "CODEX_PREVIEW"},
    }
    errors = validate_insert_block_alpha(probe_plan)
    if errors:
        raise AssertionError(f"insert_block_alpha must accept controlled-test-block-002 after V-PROOF-41: {errors}")
    if CONTROLLED_BLOCK_ALLOWLIST.get(SECOND_CONTROLLED_BLOCK_ID) != SECOND_CONTROLLED_BLOCK_NAME:
        raise AssertionError("insert_block_alpha allowlist must bind block-002 to CODEX_TEST_BLOCK_002")


def assert_second_controlled_block_contract(*, project_root: Path) -> None:
    """Raise when RBLOCK-05 second controlled block metadata is missing or inconsistent."""

    root = project_root.resolve()
    from core.block_engine.block_alpha_boundary import assert_block_alpha_boundary_contract

    assert_block_alpha_boundary_contract(project_root=root)

    if not (root / RBLOCK_05_BOUNDARY_DOC).is_file():
        raise AssertionError(f"missing RBLOCK-05 boundary doc: {RBLOCK_05_BOUNDARY_DOC}")

    manifest_path = default_manifest_path(root)
    if not manifest_path.is_file():
        raise AssertionError(f"missing manifest: {DEFAULT_MANIFEST_REL}")

    manifest = load_second_controlled_block_manifest(manifest_path)
    library_path = root / str(manifest["library_path"])
    schema_path = root / str(manifest["schema_path"])
    sidecar_path = root / str(manifest["sidecar_path"])

    schema_errors = validate_json(schema_path, library_path)
    if schema_errors:
        raise AssertionError("block library schema errors: " + "; ".join(schema_errors[:3]))

    raw_library = json.loads(library_path.read_text(encoding="utf-8"))
    semantic_errors = validate_block_library(raw_library)
    if semantic_errors:
        raise AssertionError("block library semantic errors: " + "; ".join(semantic_errors[:3]))

    library = load_block_library(library_path)
    primary = _library_block(library, str(manifest["primary_controlled_block_id"]))
    second = _library_block(library, SECOND_CONTROLLED_BLOCK_ID)
    if primary is None:
        raise AssertionError(f"missing primary controlled block: {manifest['primary_controlled_block_id']}")
    if second is None:
        raise AssertionError(f"missing second controlled block: {SECOND_CONTROLLED_BLOCK_ID}")

    cad_name = str(second.get("cad_identity", {}).get("block_name", ""))
    if cad_name != SECOND_CONTROLLED_BLOCK_NAME:
        raise AssertionError(f"second block cad_identity.block_name must be {SECOND_CONTROLLED_BLOCK_NAME!r}")

    footprint = second.get("footprint_2d", {})
    if footprint.get("width") != SECOND_CONTROLLED_FOOTPRINT["width"]:
        raise AssertionError("second controlled block footprint width must be 600mm")
    if footprint.get("depth") != SECOND_CONTROLLED_FOOTPRINT["depth"]:
        raise AssertionError("second controlled block footprint depth must be 300mm")

    primary_name = str(primary.get("cad_identity", {}).get("block_name", ""))
    if primary_name != CONTROLLED_BLOCK_NAME:
        raise AssertionError(f"primary block must remain {CONTROLLED_BLOCK_NAME!r}")

    if not sidecar_path.is_file():
        raise AssertionError(f"missing sidecar metadata: {manifest['sidecar_path']}")

    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    if sidecar.get("block_id") != SECOND_CONTROLLED_BLOCK_ID:
        raise AssertionError("sidecar block_id mismatch")
    sidecar_name = str(sidecar.get("cad_identity", {}).get("block_name", ""))
    if sidecar_name != SECOND_CONTROLLED_BLOCK_NAME:
        raise AssertionError("sidecar cad_identity.block_name mismatch")

    selection = object_spec_to_block_reference(
        {
            "object_id": "probe-002",
            "type": "test_fixture",
            "name": "Probe",
            "size": {"width": 600, "depth": 300},
            "preferred_block_refs": [SECOND_CONTROLLED_BLOCK_ID],
        },
        library,
    )
    if selection.get("status") != "selected":
        raise AssertionError("object_spec_to_block_reference must select metadata_only block-002 by ref")
    if selection["block_reference"]["block_id"] != SECOND_CONTROLLED_BLOCK_ID:
        raise AssertionError("block_reference must point to controlled-test-block-002")

    assert_insert_block_alpha_accepts_second_controlled_block()


def second_controlled_block_status_summary(*, project_root: Path) -> dict[str, Any]:
    manifest = load_second_controlled_block_manifest(default_manifest_path(project_root))
    library = load_block_library(project_root / str(manifest["library_path"]))
    controlled_ids = [
        str(block.get("block_id"))
        for block in library.get("blocks", [])
        if isinstance(block, dict)
        and str(block.get("source", {}).get("type")) == "controlled_test_block"
    ]
    return {
        "package_id": RBLOCK_05_PACKAGE_ID,
        "manifest_id": manifest.get("manifest_id"),
        "controlled_test_block_count": len(controlled_ids),
        "second_block_id": SECOND_CONTROLLED_BLOCK_ID,
        "insert_block_alpha_allowlist": list(manifest.get("insert_block_alpha_allowlist_block_ids", [])),
    }
