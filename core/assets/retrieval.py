"""Lightweight CAD asset retrieval pack builder.

This module intentionally starts with JSON / Markdown lookup. It does not
provide RAG, embeddings, or capability proof; it prepares an auditable upstream
contract before visual intent and CAD_PLAN generation.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OBJECT_DEFAULTS_REL = Path("libraries/objects/object_defaults.json")
SYSTEM_LIBRARY_REL = Path("libraries/system_library")
REFERENCE_LIBRARY_REL = Path("libraries/reference_library/manifests")
KNOWLEDGE_RULES_REL = Path("libraries/knowledge/rules")
TRAINING_ERRORS_REL = Path("docs/training/training-errors.md")
LEGACY_TRAINING_ERRORS_REL = Path("TRAINING_ERRORS.md")


ARCHETYPE_BY_OBJECT = {
    "chair": "seating",
    "sofa": "seating",
    "bench": "seating",
    "stool": "seating",
    "table": "surface",
    "desk": "surface",
    "counter": "surface",
    "bed": "sleeping",
    "cabinet": "storage",
    "storage_cabinet": "storage",
    "file_cabinet": "storage",
    "shelf": "storage",
    "display_unit": "display",
    "monitor": "workstation",
    "computer_desk": "workstation",
}

ARCHETYPE_TERMS = {
    "seating": ["seat", "chair", "sofa", "bench", "stool", "沙发", "椅", "座椅", "卡座"],
    "surface": ["table", "desk", "counter", "worktop", "桌", "台面", "柜台"],
    "sleeping": ["bed", "mattress", "床", "床头"],
    "storage": ["cabinet", "shelf", "wardrobe", "drawer", "柜", "架", "抽屉", "衣柜"],
    "display": ["display", "showcase", "shelf", "展", "货架", "展示"],
    "workstation": ["workstation", "computer", "monitor", "办公位", "电脑", "屏幕"],
}

OBJECT_ALIASES = {
    "cabinet": ["柜", "柜子", "cabinet"],
    "shelf": ["架", "货架", "书架", "shelf"],
    "table": ["桌", "桌子", "餐桌", "table"],
    "desk": ["办公桌", "书桌", "desk"],
    "chair": ["椅", "椅子", "chair"],
    "bed": ["床", "床铺", "bed"],
    "rug": ["地毯", "rug"],
    "sofa": ["沙发", "sofa", "couch"],
    "counter": ["柜台", "台面", "counter"],
    "display_unit": ["展示柜", "展示架", "display"],
    "monitor": ["显示器", "屏幕", "monitor"],
    "computer_desk": ["电脑桌", "电脑位", "computer desk"],
    "storage_cabinet": ["储物柜", "收纳柜", "storage cabinet"],
    "file_cabinet": ["文件柜", "file cabinet"],
}


def _read_json_object(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _iter_json_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(path for path in root.rglob("*.json") if path.is_file())


def _compact_text(value: Any) -> str:
    if isinstance(value, str):
        return value.lower()
    if isinstance(value, list):
        return " ".join(_compact_text(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_compact_text(item) for item in value.values())
    return str(value).lower()


def _term_hits(text: str, terms: list[str]) -> list[str]:
    lowered = text.lower()
    return [term for term in terms if term.lower() in lowered]


def _object_terms(object_id: str, data: dict[str, Any]) -> list[str]:
    terms = [object_id, object_id.replace("_", " ")]
    name = data.get("name")
    if isinstance(name, str):
        terms.append(name)
    aliases = data.get("aliases")
    if isinstance(aliases, list):
        terms.extend(str(alias) for alias in aliases)
    terms.extend(OBJECT_ALIASES.get(object_id, []))
    return sorted({term for term in terms if term})


def _component_roles(data: dict[str, Any]) -> list[str]:
    roles: list[str] = []
    components = data.get("components")
    if isinstance(components, list):
        for component in components:
            if isinstance(component, dict) and isinstance(component.get("role"), str):
                roles.append(component["role"])
    parts = data.get("parts")
    if isinstance(parts, list):
        roles.extend(str(part) for part in parts)
    return sorted({role for role in roles if role})


def _match_object_defaults(root: Path, brief: str) -> list[dict[str, Any]]:
    data = _read_json_object(root / OBJECT_DEFAULTS_REL) or {}
    objects = data.get("objects", {})
    if not isinstance(objects, dict):
        return []

    matches: list[dict[str, Any]] = []
    for object_id, spec in objects.items():
        if not isinstance(spec, dict):
            continue
        terms = _object_terms(str(object_id), spec)
        hits = _term_hits(brief, terms)
        if not hits:
            continue
        parts = _component_roles(spec)
        matches.append(
            {
                "id": f"object_default.{object_id}",
                "asset_type": "object_default",
                "source": str(OBJECT_DEFAULTS_REL).replace("\\", "/"),
                "canonical_name": object_id,
                "display_name": spec.get("name", object_id),
                "match_strength": "object_family",
                "matched_terms": hits,
                "archetype": ARCHETYPE_BY_OBJECT.get(str(object_id), "unknown"),
                "required_parts": parts,
                "parameters": {
                    "width_mm": spec.get("width"),
                    "depth_mm": spec.get("depth"),
                    "height_mm": spec.get("height"),
                },
            }
        )
    return matches


def _match_asset_json_files(root: Path, folder: Path, brief: str, *, source_kind: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for path in _iter_json_files(root / folder):
        data = _read_json_object(path)
        if not data:
            continue
        searchable = _compact_text(
            {
                "id": data.get("id"),
                "canonical_name": data.get("canonical_name"),
                "aliases": data.get("aliases"),
                "object_tags": data.get("object_tags"),
                "part_tags": data.get("part_tags"),
                "style_tags": data.get("style_tags"),
                "parts": data.get("parts"),
            }
        )
        terms = [term for term in re.split(r"\s+", searchable) if term]
        hits = _term_hits(brief, terms)
        if not hits:
            continue
        try:
            rel_path = path.relative_to(root)
        except ValueError:
            rel_path = path
        matches.append(
            {
                "id": data.get("id", path.stem),
                "asset_type": source_kind,
                "source": str(rel_path).replace("\\", "/"),
                "canonical_name": data.get("canonical_name") or data.get("source_name") or path.stem,
                "match_strength": "asset_match" if source_kind == "system_asset" else "reference_match",
                "matched_terms": sorted(set(hits))[:8],
                "validation_status": data.get("validation_status"),
                "usage_boundary": data.get("usage_boundary"),
                "required_parts": data.get("parts") or data.get("part_tags") or [],
                "representation": data.get("representation", {}),
            }
        )
    return matches


def _match_knowledge_rules(root: Path, brief: str) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for path in _iter_json_files(root / KNOWLEDGE_RULES_REL):
        data = _read_json_object(path)
        if not data:
            continue
        searchable = _compact_text(data)
        object_name = str(data.get("object", ""))
        terms = [object_name, *OBJECT_ALIASES.get(object_name, [])]
        hits = _term_hits(brief, [term for term in terms if term])
        if not hits and object_name not in searchable:
            continue
        try:
            rel_path = path.relative_to(root)
        except ValueError:
            rel_path = path
        matches.append(
            {
                "id": data.get("id", path.stem),
                "source": str(rel_path).replace("\\", "/"),
                "object": data.get("object"),
                "claim": data.get("claim"),
                "status": data.get("status", "candidate"),
                "required_parts": data.get("required_parts", []),
                "forbidden_shortcuts": data.get("forbidden_shortcuts", []),
            }
        )
    return matches


def _infer_archetype(brief: str, matched_assets: list[dict[str, Any]]) -> str:
    for asset in matched_assets:
        archetype = asset.get("archetype")
        if isinstance(archetype, str) and archetype and archetype != "unknown":
            return archetype
        name = str(asset.get("canonical_name", ""))
        if name in ARCHETYPE_BY_OBJECT:
            return ARCHETYPE_BY_OBJECT[name]
    for archetype, terms in ARCHETYPE_TERMS.items():
        if _term_hits(brief, terms):
            return archetype
    return "unknown"


def _known_failures(root: Path, brief: str, case_dir: Path | None, *, limit: int) -> list[dict[str, str]]:
    terms = set()
    for object_id, aliases in OBJECT_ALIASES.items():
        if _term_hits(brief, [object_id, *aliases]):
            terms.add(object_id)
            terms.update(alias.lower() for alias in aliases)
    if not terms:
        return []

    training_errors = root / TRAINING_ERRORS_REL
    sources = [training_errors] if training_errors.is_file() else [root / LEGACY_TRAINING_ERRORS_REL]
    if case_dir is not None:
        sources.append(case_dir / "feedback.md")

    failures: list[dict[str, str]] = []
    for source in sources:
        if not source.is_file():
            continue
        for line_number, line in enumerate(source.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            lowered = line.lower()
            if any(term and term in lowered for term in terms):
                try:
                    rel_path = source.relative_to(root)
                except ValueError:
                    rel_path = source
                failures.append(
                    {
                        "source": str(rel_path).replace("\\", "/"),
                        "line": str(line_number),
                        "summary": line.strip()[:220],
                    }
                )
            if len(failures) >= limit:
                return failures
    return failures


def _choose_route(matched_assets: list[dict[str, Any]], archetype: str) -> str:
    for asset in matched_assets:
        representation = asset.get("representation")
        if (
            asset.get("asset_type") == "system_asset"
            and asset.get("validation_status") == "system_verified"
            and isinstance(representation, dict)
            and representation.get("block_ref")
        ):
            return "exact_reuse"
    if any(asset.get("asset_type") in {"system_asset", "object_default"} for asset in matched_assets):
        return "parametric_variant"
    if any(asset.get("asset_type") == "reference_asset" for asset in matched_assets):
        return "semantic_redraw"
    if archetype != "unknown":
        return "novel_with_constraints"
    return "unsupported_or_risky"


def _allowed_render_tiers(route: str) -> list[str]:
    if route == "exact_reuse":
        return ["controlled_block", "symbol_readable", "component_preview", "deferred"]
    if route in {"parametric_variant", "semantic_redraw"}:
        return ["symbol_readable", "component_preview", "bbox_placeholder_requires_user_waiver", "deferred"]
    if route == "novel_with_constraints":
        return ["component_preview", "exploratory_symbol_candidate", "deferred"]
    return ["deferred"]


def build_retrieval_pack(
    brief: str,
    *,
    scene: str = "residential",
    case_dir: Path | None = None,
    project_root: Path = PROJECT_ROOT,
    max_known_failures: int = 5,
) -> dict[str, Any]:
    """Build a lightweight retrieval pack from local structured assets."""

    root = Path(project_root)
    resolved_case_dir = Path(case_dir) if case_dir else None
    if resolved_case_dir is not None and not resolved_case_dir.is_absolute():
        resolved_case_dir = root / resolved_case_dir

    object_matches = _match_object_defaults(root, brief)
    system_matches = _match_asset_json_files(root, SYSTEM_LIBRARY_REL, brief, source_kind="system_asset")
    reference_matches = _match_asset_json_files(root, REFERENCE_LIBRARY_REL, brief, source_kind="reference_asset")
    rule_matches = _match_knowledge_rules(root, brief)

    matched_assets = [*system_matches, *object_matches, *reference_matches]
    archetype = _infer_archetype(brief, matched_assets)
    route = _choose_route(matched_assets, archetype)
    object_family = ""
    if matched_assets:
        object_family = str(matched_assets[0].get("canonical_name") or matched_assets[0].get("id") or "")
    elif archetype != "unknown":
        object_family = f"{archetype}_candidate"

    required_parts: list[str] = []
    for item in [*matched_assets, *rule_matches]:
        parts = item.get("required_parts")
        if isinstance(parts, list):
            required_parts.extend(str(part) for part in parts)
    required_parts = sorted({part for part in required_parts if part})

    return {
        "schema_version": 1,
        "retrieval_id": f"retrieval.{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
        "scene": scene,
        "case_id": resolved_case_dir.name if resolved_case_dir else "",
        "brief": brief,
        "route": route,
        "matched_assets": matched_assets,
        "rule_matches": rule_matches,
        "object_family": object_family,
        "archetype": archetype,
        "required_parts": required_parts,
        "allowed_render_tiers": _allowed_render_tiers(route),
        "known_failures": _known_failures(root, brief, resolved_case_dir, limit=max_known_failures),
        "evidence_boundary": {
            "checked": [
                "local_object_defaults_lookup",
                "local_system_library_json_lookup",
                "local_reference_manifest_lookup",
                "local_knowledge_rule_lookup",
            ],
            "not_checked": [
                "real_cad_geometry",
                "user_visual_acceptance",
                "production_block_authorization",
                "external_asset_license_for_production_use",
            ],
            "assumptions": [
                "lexical_matching_only_no_embedding_rag",
                "retrieval_pack_is_upstream_contract_not_capability_proof",
            ],
        },
    }


def write_retrieval_pack(pack: dict[str, Any], output_path: Path) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    return output_path
