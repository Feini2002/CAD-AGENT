"""Extended capability registry seed row builders."""

from __future__ import annotations

import json
from typing import Any

from core.capabilities.specs import CAPABILITIES
from core.composition_engine.templates import COMPOSITION_TEMPLATES
from core.verification.capability_registry_seed_common import (
    BENCHMARK_ROOT,
    PREVIEW_SAFETY,
    PROJECT_ROOT,
    _preview_cad_case,
    _slug,
    _source,
)

def _composition_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for composition_id, template in sorted(COMPOSITION_TEMPLATES.items()):
        domain = str(template.get("domain", "generic"))
        is_failure = "conflict" in composition_id or composition_id.endswith("_failure")
        claim_level = "smoke" if not is_failure else "deferred"
        row: dict[str, Any] = {
            "capability_id": f"composition.{_slug(composition_id)}",
            "display_name": str(template.get("name", composition_id)),
            "category": "micro_scene" if composition_id.startswith("fitout_") else "composition",
            "claim_level": claim_level,
            "ladder_level": "L3",
            "domain": domain,
            "composition_id": composition_id,
            "source_refs": [
                _source("documentation", "core/composition_engine/templates.py", composition_id),
            ],
        }
        if claim_level == "smoke":
            suite = (
                "examples/benchmarks/commercial_fitout_micro_scene_benchmark.json"
                if composition_id.startswith("fitout_")
                else "examples/benchmarks/interior_delivery_benchmark.json"
                if composition_id in {"bedroom_bed_rug", "dining_table_set", "office_desk_combo"}
                else "examples/benchmarks/office_alpha_benchmark.json"
            )
            row["cad_case"] = _preview_cad_case(
                case_kind="benchmark_case",
                requires_real_cad=False,
                benchmark_suite_path=suite,
                benchmark_case_id=composition_id,
            )
            row["notes"] = ["Non-CAD composition benchmark pass does not prove geometry_verified."]
        else:
            row["deferred_reason"] = "Failure / conflict composition is non-CAD blocked_expected only."
            row["cad_case"] = _preview_cad_case(case_kind="none", requires_real_cad=False)
        rows.append(row)
    return rows


def _symbol_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    archetypes = {
        "surface",
        "seating",
        "storage",
        "display",
        "workstation",
        "sleeping",
    }
    for archetype in sorted(archetypes):
        rows.append(
            {
                "capability_id": f"symbol.archetype.{_slug(archetype)}",
                "display_name": f"Symbol archetype {archetype}",
                "category": "symbol",
                "claim_level": "deferred",
                "ladder_level": "L2",
                "domain": "generic",
                "intent": "draw_symbol_glyph",
                "symbol_archetype": archetype,
                "deferred_reason": "Archetype glyph CAD matrix pending V-PROOF-30~32.",
                "cad_case": _preview_cad_case(case_kind="none", requires_real_cad=False),
                "source_refs": [_source("documentation", "docs/planning/任务清单.md", archetype)],
            }
        )
    for spec_path in sorted((PROJECT_ROOT / "examples" / "symbol_specs").glob("*.json")):
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
        symbol_id = str(spec.get("symbol_id", spec_path.stem))
        rows.append(
            {
                "capability_id": f"symbol.spec.{_slug(symbol_id)}",
                "display_name": f"Symbol spec {symbol_id}",
                "category": "symbol",
                "claim_level": "deferred",
                "ladder_level": "L2",
                "domain": "generic",
                "intent": "draw_symbol_glyph",
                "symbol_archetype": str(spec.get("archetype", "")),
                "deferred_reason": "Symbol spec CAD readability not yet registry-verified.",
                "cad_case": _preview_cad_case(
                    case_kind="cad_plan",
                    requires_real_cad=True,
                    plan_path=str(spec_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                ),
                "source_refs": [_source("cad_plan", str(spec_path.relative_to(PROJECT_ROOT)), symbol_id)],
            }
        )
    return rows


def _core_capability_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for capability_id in sorted(CAPABILITIES):
        spec = CAPABILITIES[capability_id]
        requires_cad = bool(spec.get("requires_cad", False))
        category = "workflow" if capability_id.startswith("workflow.") else "other"
        if capability_id.startswith("layout."):
            category = "blank_shell"
        elif capability_id.startswith("benchmark."):
            category = "other"
        elif capability_id.startswith("drawing_analysis."):
            category = "drawing_read"
        claim_level = "deferred" if requires_cad else "none"
        row: dict[str, Any] = {
            "capability_id": f"core.api.{_slug(capability_id)}",
            "display_name": str(spec.get("title", capability_id)),
            "category": category,
            "claim_level": claim_level,
            "ladder_level": "L0" if not requires_cad else "L1",
            "domain": "generic",
            "notes": [str(spec.get("summary", ""))],
            "source_refs": [_source("documentation", "core/capabilities/specs.py", capability_id)],
        }
        if requires_cad:
            row["deferred_reason"] = "Core API capability marked requires_cad; bind RCAD report in V-PROOF-03."
            row["cad_case"] = _preview_cad_case(case_kind="none", requires_real_cad=True)
        rows.append(row)
    return rows


def _scene_rows() -> list[dict[str, Any]]:
    registry_path = PROJECT_ROOT / "examples" / "orchestrator" / "scene_registry.json"
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for scene in registry.get("scenes", []):
        if not isinstance(scene, dict):
            continue
        scene_id = str(scene.get("scene_id", ""))
        maturity = str(scene.get("maturity", ""))
        ladder = "L0" if scene_id == "no_scene" else "L3" if maturity in {"scene_beta", "scene_product"} else "L2"
        rows.append(
            {
                "capability_id": f"scene.{_slug(scene_id)}",
                "display_name": str(scene.get("display_name", scene_id)),
                "category": "scene",
                "claim_level": "none",
                "ladder_level": ladder,
                "domain": "commercial_fitout" if scene_id == "commercial_fitout" else "generic",
                "scene_id": scene_id,
                "notes": [f"Scene maturity={maturity}; preferences-only unless benchmark row exists."],
                "source_refs": [_source("documentation", str(registry_path.relative_to(PROJECT_ROOT)), scene_id)],
            }
        )
    return rows


def _benchmark_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for suite_path in sorted(BENCHMARK_ROOT.glob("*.json")):
        suite = json.loads(suite_path.read_text(encoding="utf-8"))
        suite_id = str(suite.get("suite_id", suite_path.stem))
        rel_suite = str(suite_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
        for case in suite.get("cases", []):
            if not isinstance(case, dict):
                continue
            case_id = str(case.get("case_id", case.get("composition_id", case.get("object_type", "case"))))
            pipeline = str(case.get("pipeline", "non_cad"))
            requires_real_cad = pipeline not in {"non_cad", "composition_spec", "object_spec", "blank_shell"}
            claim_level = "smoke"
            tier = str(case.get("case_tier", ""))
            if tier == "failure" or str(case.get("expected", {}).get("pipeline_status")) == "blocked":
                claim_level = "deferred"
            row: dict[str, Any] = {
                "capability_id": f"benchmark.{_slug(suite_id)}.{_slug(case_id)}",
                "display_name": f"{suite_id} / {case_id}",
                "category": "micro_scene" if pipeline == "composition_spec" else "blank_shell" if pipeline == "blank_shell" else "other",
                "claim_level": claim_level,
                "ladder_level": "L3" if pipeline in {"composition_spec", "blank_shell"} else "L0",
                "domain": "generic",
                "cad_case": _preview_cad_case(
                    case_kind="benchmark_case",
                    requires_real_cad=requires_real_cad,
                    benchmark_suite_path=rel_suite,
                    benchmark_case_id=case_id,
                ),
                "source_refs": [_source("benchmark", rel_suite, case_id)],
            }
            if claim_level == "deferred":
                row["deferred_reason"] = "Failure or blocked benchmark case; non-CAD only until CAD case bound."
            else:
                row["notes"] = ["benchmark_pass_non_cad does not imply geometry_verified."]
            rows.append(row)
    return rows


def _regression_manifest_rows() -> list[dict[str, Any]]:
    manifest_path = PROJECT_ROOT / "examples" / "cad_regression" / "local_cad_regression_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rel_manifest = str(manifest_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    rows: list[dict[str, Any]] = []
    for case in manifest.get("cases", []):
        if not isinstance(case, dict):
            continue
        case_id = str(case.get("id", ""))
        requires_real_cad = bool(case.get("requires_real_cad", True))
        rows.append(
            {
                "capability_id": f"regression.{_slug(case_id)}",
                "display_name": str(case.get("title", case_id)),
                "category": "other",
                "claim_level": "deferred" if requires_real_cad else "smoke",
                "ladder_level": "L1" if requires_real_cad else "L0",
                "domain": "generic",
                "cad_case": _preview_cad_case(
                    case_kind="regression_manifest_case",
                    requires_real_cad=requires_real_cad,
                    manifest_path=rel_manifest,
                    manifest_case_id=case_id,
                    entrypoint=str(case.get("entrypoint", "")),
                    command=[str(item) for item in case.get("command", [])],
                    output_path=str(case.get("output_path", "")),
                ),
                "source_refs": [_source("regression_manifest", rel_manifest, case_id)],
                "notes": [f"expected_evidence_state={case.get('expected_evidence_state', '')}"],
            }
        )
        if requires_real_cad:
            rows[-1]["deferred_reason"] = "RCAD manifest case requires user-session AutoCAD before verified."
    return rows


def _block_library_rows() -> list[dict[str, Any]]:
    library_path = PROJECT_ROOT / "libraries" / "blocks" / "block_library.example.json"
    library = json.loads(library_path.read_text(encoding="utf-8"))
    rel = str(library_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    rows: list[dict[str, Any]] = []
    for block in library.get("blocks", []):
        if not isinstance(block, dict):
            continue
        block_id = str(block.get("block_id", ""))
        controlled = block_id.startswith("controlled-")
        row: dict[str, Any] = {
            "capability_id": f"block.library.{_slug(block_id)}",
            "display_name": f"Block {block.get('name', block_id)}",
            "category": "block",
            "claim_level": "deferred" if not controlled else "smoke",
            "ladder_level": "L1",
            "domain": str(block.get("domain", "generic")),
            "intent": "insert_block_alpha",
            "cad_case": _preview_cad_case(
                case_kind="cad_plan" if controlled else "none",
                requires_real_cad=controlled,
                plan_path="examples/plans/insert_block_alpha_test.json" if controlled else None,
            ),
            "source_refs": [_source("block_library", rel, block_id)],
        }
        if not controlled:
            row["deferred_reason"] = "Example block metadata without controlled CAD alpha proof."
        else:
            row["notes"] = ["Controlled block alpha has RCAD evidence; claim_level remains smoke until V-PROOF-03 backfill."]
        rows.append(row)
    return rows


def _component_role_rows() -> list[dict[str, Any]]:
    defaults = json.loads((PROJECT_ROOT / "libraries" / "objects" / "object_defaults.json").read_text(encoding="utf-8"))
    roles: set[str] = set()
    for spec in defaults.get("objects", {}).values():
        for component in spec.get("components", []):
            if isinstance(component, dict) and component.get("role"):
                roles.add(str(component["role"]))
        for ref in spec.get("clearance_refs", []):
            if isinstance(ref, dict) and ref.get("role"):
                roles.add(str(ref["role"]))
    rows: list[dict[str, Any]] = []
    for role in sorted(roles):
        rows.append(
            {
                "capability_id": f"component_role.{_slug(role)}",
                "display_name": f"Object component role {role}",
                "category": "other",
                "claim_level": "none",
                "ladder_level": "L0",
                "domain": "generic",
                "notes": ["Component role inventory for object_spec / layout assertions."],
                "source_refs": [_source("object_catalog", "libraries/objects/object_defaults.json", role)],
            }
        )
    return rows


def _block_insert_variants() -> list[dict[str, Any]]:
    variants = [
        ("anchor", "Alternate insertion anchor"),
        ("rotation", "90-degree rotation variant"),
        ("scale", "Uniform scale variant"),
        ("attributes", "Attribute probe variant"),
    ]
    rows: list[dict[str, Any]] = []
    for suffix, label in variants:
        rows.append(
            {
                "capability_id": f"block.insert_block_alpha.{suffix}",
                "display_name": label,
                "category": "block",
                "claim_level": "deferred",
                "ladder_level": "L1",
                "domain": "generic",
                "intent": "insert_block_alpha",
                "deferred_reason": f"Block alpha {suffix} variant not yet registry-verified (RCAD-04~05).",
                "cad_case": _preview_cad_case(
                    case_kind="cad_plan",
                    requires_real_cad=True,
                    plan_path="examples/plans/insert_block_alpha_test.json",
                ),
                "source_refs": [_source("cad_plan", "examples/plans/insert_block_alpha_test.json", suffix)],
            }
        )
    return rows


