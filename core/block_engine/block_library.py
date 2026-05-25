"""Block library metadata loading and selection helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIBRARY = PROJECT_ROOT / "libraries" / "blocks" / "block_library.example.json"


def load_block_library(path: Path = DEFAULT_LIBRARY) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        library = json.load(file)
    if not isinstance(library, dict):
        raise ValueError("Block library must be a JSON object.")
    return library


def select_blocks(
    library: dict[str, Any],
    *,
    category: str | None = None,
    domain: str | None = None,
    max_width: float | int | None = None,
    max_depth: float | int | None = None,
) -> list[dict[str, Any]]:
    blocks = library.get("blocks", [])
    if not isinstance(blocks, list):
        return []

    result: list[dict[str, Any]] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        if category and block.get("category") != category:
            continue
        if domain and block.get("domain") not in {domain, "generic"}:
            continue
        size = block.get("size", {})
        if max_width is not None and size.get("width", 0) > max_width:
            continue
        if max_depth is not None and size.get("depth", 0) > max_depth:
            continue
        result.append(block)
    return result


def fallback_object_spec(category: str, *, width: float | int, depth: float | int) -> dict[str, Any]:
    from core.object_engine.parametric_objects import create_object_spec

    return create_object_spec(category, width=width, depth=depth)
