"""Structured block selection with fallback object specs."""

from __future__ import annotations

from typing import Any

from core.block_engine.block_library import fallback_object_spec, select_blocks


def _score_block(block: dict[str, Any], *, domain: str | None, tags: list[str]) -> tuple[float, list[str]]:
    score = 0.5
    reasons: list[str] = ["category matched"]
    if domain and block.get("domain") == domain:
        score += 0.25
        reasons.append("domain matched")
    elif block.get("domain") == "generic":
        score += 0.1
        reasons.append("generic block accepted")
    block_tags = set(block.get("tags", []))
    matched_tags = sorted(block_tags.intersection(tags))
    if matched_tags:
        score += min(0.15, 0.05 * len(matched_tags))
        reasons.append(f"tags matched: {matched_tags}")
    if block.get("rotation_allowed"):
        score += 0.05
        reasons.append("rotation allowed")
    return min(score, 1.0), reasons


def select_block_candidate(
    library: dict[str, Any],
    *,
    category: str,
    domain: str | None = None,
    tags: list[str] | None = None,
    max_width: float | int | None = None,
    max_depth: float | int | None = None,
    min_clearance: float | int | None = None,
) -> dict[str, Any]:
    tags = tags or []
    candidates = select_blocks(
        library,
        category=category,
        domain=domain,
        tags=tags,
        max_width=max_width,
        max_depth=max_depth,
        selectable_only=True,
    )
    if min_clearance is not None:
        candidates = [block for block in candidates if block.get("clearance_mm", 0) >= min_clearance]
    if not candidates:
        return {
            "status": "fallback",
            "selected_block": None,
            "score": 0,
            "reasons": ["no matching block found"],
            "warnings": ["Using parametric OBJECT_SPEC fallback."],
            "fallback_object_spec": fallback_object_spec(category, width=max_width or 1000, depth=max_depth or 500),
        }
    scored = [(_score_block(block, domain=domain, tags=tags), block) for block in candidates]
    scored.sort(key=lambda item: item[0][0], reverse=True)
    (score, reasons), block = scored[0]
    return {
        "status": "selected",
        "selected_block": block,
        "score": score,
        "reasons": reasons,
        "warnings": [],
        "fallback_object_spec": None,
    }
