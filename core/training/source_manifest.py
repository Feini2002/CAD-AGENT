"""Training fact-source manifest helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_MANIFEST_RELATIVE_PATH = Path("docs") / "training" / "training-sources.json"


def load_training_source_manifest(root: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    """Load the training fact-source manifest, returning an empty manifest if absent."""
    path = manifest_path or root / DEFAULT_MANIFEST_RELATIVE_PATH
    if not path.exists():
        return {"schemaVersion": 1, "sources": []}
    return json.loads(path.read_text(encoding="utf-8"))


def training_sources(
    root: Path,
    *,
    manifest_path: Path | None = None,
    role: str | None = None,
    kind: str | None = None,
    active_only: bool = True,
) -> list[dict[str, Any]]:
    manifest = load_training_source_manifest(root, manifest_path)
    rows: list[dict[str, Any]] = []
    for row in manifest.get("sources", []):
        if active_only and row.get("status", "active") != "active":
            continue
        if role is not None and row.get("role") != role:
            continue
        if kind is not None and row.get("kind") != kind:
            continue
        rows.append(dict(row))
    return rows


def training_source_paths(
    root: Path,
    *,
    manifest_path: Path | None = None,
    role: str | None = None,
    kind: str | None = None,
    active_only: bool = True,
) -> list[Path]:
    paths: list[Path] = []
    for source in training_sources(
        root,
        manifest_path=manifest_path,
        role=role,
        kind=kind,
        active_only=active_only,
    ):
        source_path = str(source.get("path", "")).strip()
        if not source_path:
            continue
        path = Path(source_path)
        paths.append(path if path.is_absolute() else root / path)
    return paths


def display_training_sources(root: Path, manifest_path: Path | None = None) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for source in training_sources(root, manifest_path=manifest_path, active_only=False):
        row = dict(source)
        source_path = str(row.get("path", "")).strip()
        row["exists"] = bool(source_path and (root / source_path).is_file())
        rows.append(row)
    return rows
