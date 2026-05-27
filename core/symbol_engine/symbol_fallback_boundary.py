"""P4 symbol glyph fallback tier boundary contract (SYMBOL-08)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.symbol_engine.fallback_policy import (
    FALLBACK_MODE_TO_TIER,
    FALLBACK_RENDER_TIERS,
    TIER_RANK,
    TIER_TO_CAD_INTENT,
    detect_silent_degradation,
    resolve_symbol_render_resolution,
)
from core.verification.capability_registry import index_capability_rows, load_capability_registry, validate_capability_registry

SYMBOL_08_PACKAGE_ID = "SYMBOL-08-GLYPH-FALLBACK-BOUNDARY"

SYMBOL_08_BOUNDARY_DOC = "docs/verification/symbol_08_glyph_fallback_boundary.md"
SYMBOL_FALLBACK_BENCHMARK_PATH = "examples/benchmarks/symbol_fallback_policy_benchmark.json"
SYMBOL_FALLBACK_POLICY_MODULE = "core/symbol_engine/fallback_policy.py"
SYMBOL_FALLBACK_POLICY_TESTS = "tests/core/test_symbol_fallback_policy.py"

# Four executable render tiers (block → glyph → component → bbox); deferred is structured exit.
GLYPH_FALLBACK_TIERS = ("block", "symbol_glyph", "component_preview", "bbox_placeholder")

SYMBOL_08_REGISTRY_BENCHMARK_IDS = (
    "benchmark.symbol_fallback_policy_01.desk_symbol_glyph",
    "benchmark.symbol_fallback_policy_01.desk_elevation_component_preview",
    "benchmark.symbol_fallback_policy_01.counter_deferred",
)

VPROOF_35_PACKAGE_ID = "V-PROOF-35-FALLBACK-TIER-ROWS"
VPROOF_35_REGISTRY_TIER_IDS = (
    "symbol.fallback_tier.block",
    "symbol.fallback_tier.symbol_glyph",
    "symbol.fallback_tier.component_preview",
    "symbol.fallback_tier.bbox_placeholder",
    "symbol.fallback_tier.deferred_unsupported_symbol",
)


def assert_symbol_glyph_fallback_boundary_contract(*, project_root: Path) -> None:
    """Raise when SYMBOL-08 fallback tier artifacts or invariants are missing."""

    root = project_root.resolve()

    boundary = root / SYMBOL_08_BOUNDARY_DOC
    if not boundary.is_file():
        raise AssertionError(f"missing SYMBOL-08 boundary doc: {SYMBOL_08_BOUNDARY_DOC}")

    for rel in (
        SYMBOL_FALLBACK_POLICY_MODULE,
        SYMBOL_FALLBACK_POLICY_TESTS,
        SYMBOL_FALLBACK_BENCHMARK_PATH,
    ):
        if not (root / rel).is_file():
            raise AssertionError(f"missing SYMBOL-08 artifact: {rel}")

    # Tier order and CAD intent mapping must stay stable for V-PROOF-35 / D-SYMBOL-07.
    if list(FALLBACK_RENDER_TIERS) != [
        "block",
        "symbol_glyph",
        "component_preview",
        "bbox_placeholder",
        "deferred",
    ]:
        raise AssertionError("FALLBACK_RENDER_TIERS order changed")

    for tier in GLYPH_FALLBACK_TIERS:
        if tier not in TIER_RANK:
            raise AssertionError(f"missing tier rank for {tier!r}")
        intent = TIER_TO_CAD_INTENT.get(tier)
        if tier != "bbox_placeholder" and intent is None:
            raise AssertionError(f"missing CAD intent for tier {tier!r}")

    required_modes = (
        "block_preferred",
        "symbol_readable",
        "fallback_component_preview",
        "fallback_bbox_placeholder",
        "deferred_unsupported_symbol",
    )
    for mode in required_modes:
        if mode not in FALLBACK_MODE_TO_TIER:
            raise AssertionError(f"missing fallback mode mapping: {mode!r}")

    registry = load_capability_registry(
        root / "examples/capability_proof/cad_capability_registry.json",
        project_root=root,
    )
    index = index_capability_rows(registry)
    for capability_id in SYMBOL_08_REGISTRY_BENCHMARK_IDS:
        if capability_id not in index:
            raise AssertionError(f"missing registry benchmark row: {capability_id}")
    for capability_id in VPROOF_35_REGISTRY_TIER_IDS:
        row = index.get(capability_id)
        if row is None:
            raise AssertionError(f"missing V-PROOF-35 fallback tier row: {capability_id}")
        if row.get("claim_level") in {"verified", "showcase"}:
            raise AssertionError(f"{capability_id} must not claim geometry proof without CAD readback")

    schema_errors = validate_capability_registry(registry)
    if schema_errors:
        raise AssertionError(f"registry validation failed: {schema_errors[:3]}")

    suite = json.loads((root / SYMBOL_FALLBACK_BENCHMARK_PATH).read_text(encoding="utf-8"))
    if suite.get("suite_id") != "symbol-fallback-policy-01":
        raise AssertionError(f"unexpected benchmark suite_id: {suite.get('suite_id')!r}")
    if len(suite.get("cases", [])) != 3:
        raise AssertionError("symbol_fallback_policy_benchmark must have 3 cases")

    _assert_benchmark_cases_resolve_without_silent_degradation(root=root, suite=suite)


def _assert_benchmark_cases_resolve_without_silent_degradation(
    *,
    root: Path,
    suite: dict[str, Any],
) -> None:
    for case in suite.get("cases", []):
        if not isinstance(case, dict):
            raise AssertionError("benchmark case must be an object")
        case_id = str(case.get("case_id", ""))
        if case.get("object_spec_path"):
            spec = json.loads((root / str(case["object_spec_path"])).read_text(encoding="utf-8"))
            overrides = case.get("object_spec_overrides")
            if isinstance(overrides, dict):
                spec = {**spec, **overrides}
        elif isinstance(case.get("object_spec"), dict):
            spec = case["object_spec"]
        else:
            raise AssertionError(f"case {case_id!r} missing object_spec")

        report = resolve_symbol_render_resolution(spec)
        expected = case.get("expected", {})
        if str(report.get("selected_render_path", "")) != str(expected.get("selected_render_path", "")):
            raise AssertionError(
                f"{case_id}: selected_render_path expected {expected.get('selected_render_path')!r}, "
                f"got {report.get('selected_render_path')!r}"
            )
        if bool(report.get("silent_degradation")):
            raise AssertionError(f"{case_id}: silent_degradation must be false")
        errors = detect_silent_degradation(report)
        if errors:
            raise AssertionError(f"{case_id}: silent degradation errors: {errors}")

        if not isinstance(report.get("tier_assessments"), list) or len(report["tier_assessments"]) != 5:
            raise AssertionError(f"{case_id}: expected 5 tier assessments")


def symbol_fallback_boundary_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    suite = json.loads((root / SYMBOL_FALLBACK_BENCHMARK_PATH).read_text(encoding="utf-8"))
    return {
        "package_id": SYMBOL_08_PACKAGE_ID,
        "docs_present": (root / SYMBOL_08_BOUNDARY_DOC).is_file(),
        "tier_count": len(FALLBACK_RENDER_TIERS),
        "glyph_fallback_tier_count": len(GLYPH_FALLBACK_TIERS),
        "benchmark_case_count": len(suite.get("cases", [])),
        "registry_benchmark_row_count": len(SYMBOL_08_REGISTRY_BENCHMARK_IDS),
        "vproof_35_package_id": VPROOF_35_PACKAGE_ID,
        "vproof_35_registry_tier_count": len(VPROOF_35_REGISTRY_TIER_IDS),
    }
