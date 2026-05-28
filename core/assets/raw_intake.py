"""Automatic intake for raw standard CAD library batches."""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any


RAW_LIBRARY_REL = Path("standard_cad_library_raw")
REFERENCE_LIBRARY_REL = Path("libraries/reference_library")
KNOWLEDGE_SOURCE_NOTES_REL = Path("libraries/knowledge/source_notes")

IGNORED_NAMES = {
    ".ds_store",
    "thumbs.db",
}
IGNORED_SUFFIXES = {
    ".bak",
    ".crdownload",
    ".download",
    ".dwl",
    ".dwl2",
    ".part",
    ".tmp",
}
IGNORED_PARTS = {"__macosx"}

VIEW_TERMS = {
    "plan": ["plan", "floorplan", "top", "topview", "layout", "pingmian", "平面", "俯视", "布置"],
    "elevation": ["elevation", "front", "side", "facade", "立面", "正立面", "侧立面"],
    "detail": ["detail", "node", "section", "joint", "详图", "节点", "剖面", "大样"],
    "perspective": ["perspective", "render", "3d", "效果", "透视"],
}

OBJECT_TERMS = {
    "sofa": ["sofa", "couch", "沙发"],
    "bed": ["bed", "床"],
    "table": ["table", "desk", "茶几", "桌", "桌子", "餐桌", "书桌"],
    "chair": ["chair", "seat", "椅", "椅子", "座椅"],
    "cabinet": ["cabinet", "wardrobe", "closet", "柜", "柜子", "衣柜", "橱柜"],
    "shelf": ["shelf", "rack", "书架", "货架", "架子"],
    "door": ["door", "门"],
    "window": ["window", "窗"],
    "wall": ["wall", "墙"],
    "sink": ["sink", "basin", "水槽", "洗手盆"],
    "toilet": ["toilet", "wc", "马桶", "坐便器"],
    "bathtub": ["bathtub", "bath", "浴缸"],
}

PARTS_BY_OBJECT = {
    "sofa": ["seat", "back", "arm_left", "arm_right"],
    "bed": ["mattress", "headboard"],
    "table": ["top", "legs"],
    "chair": ["seat", "back", "legs"],
    "cabinet": ["body", "door_panel", "shelf"],
    "shelf": ["frame", "shelves"],
    "door": ["panel", "swing"],
    "window": ["frame", "glass"],
    "wall": ["segment"],
    "sink": ["basin", "counter_cutout"],
    "toilet": ["bowl", "tank"],
    "bathtub": ["tub"],
}

DOMAIN_TERMS = {
    "residential": ["residential", "home", "furniture", "house", "住宅", "家装", "家居", "家具"],
    "office": ["office", "workstation", "办公", "工位", "会议"],
    "retail": ["retail", "showroom", "store", "展厅", "零售", "店铺"],
    "restaurant": ["restaurant", "dining", "餐饮", "餐厅"],
}

STYLE_TERMS = {
    "modern": ["modern", "minimal", "现代", "极简"],
    "classic": ["classic", "traditional", "古典", "传统"],
    "industrial": ["industrial", "loft", "工业"],
    "chinese": ["chinese", "中式", "新中式"],
}


@dataclass(frozen=True)
class RawFile:
    path: Path
    rel_to_original: Path
    size_bytes: int


def _validate_source_slug(source_slug: str) -> str:
    slug = source_slug.strip()
    if not slug:
        raise ValueError("source_slug is required.")
    slug_path = Path(slug)
    if slug_path.is_absolute() or any(part in {"..", ""} for part in slug_path.parts):
        raise ValueError("source_slug must be a single safe folder name.")
    if "/" in slug or "\\" in slug:
        raise ValueError("source_slug must not contain path separators.")
    return slug


def _id_slug(source_slug: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", source_slug.lower()).strip("_")
    if normalized:
        return normalized
    digest = hashlib.sha1(source_slug.encode("utf-8")).hexdigest()[:8]
    return f"source_{digest}"


def _split_tags(value: str | list[str] | tuple[str, ...] | None) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        pieces = re.split(r"[,;\s]+", value.strip())
    else:
        pieces = [str(item) for item in value]
    tags = [piece.strip().lower() for piece in pieces if piece and piece.strip()]
    return sorted(dict.fromkeys(tags))


def _is_ignored_file(path: Path) -> bool:
    lowered_parts = {part.lower() for part in path.parts}
    if lowered_parts & IGNORED_PARTS:
        return True
    name = path.name.lower()
    if name in IGNORED_NAMES:
        return True
    return path.suffix.lower() in IGNORED_SUFFIXES


def _scan_raw_files(original_dir: Path) -> tuple[list[RawFile], list[str]]:
    raw_files: list[RawFile] = []
    skipped: list[str] = []
    if not original_dir.exists():
        return raw_files, skipped
    for path in sorted(original_dir.rglob("*")):
        if not path.is_file():
            continue
        rel_path = path.relative_to(original_dir)
        if _is_ignored_file(rel_path):
            skipped.append(str(rel_path).replace("\\", "/"))
            continue
        raw_files.append(RawFile(path=path, rel_to_original=rel_path, size_bytes=path.stat().st_size))
    return raw_files, skipped


def _contains_term(text: str, term: str) -> bool:
    lowered = text.lower()
    if any(ord(char) > 127 for char in term):
        return term in text
    return term.lower() in lowered


def _infer_from_terms(text: str, term_map: dict[str, list[str]]) -> list[str]:
    matches: list[str] = []
    for value, terms in term_map.items():
        if any(_contains_term(text, term) for term in [value, *terms]):
            matches.append(value)
    return matches


def _infer_view_type(text: str, explicit_view_type: str | None = None) -> tuple[str, str]:
    if explicit_view_type:
        return explicit_view_type, "user_provided"
    matches = _infer_from_terms(text, VIEW_TERMS)
    if matches:
        return matches[0], "inferred_from_path_or_note"
    return "unknown", "unknown_default"


def _infer_domain(text: str, object_tags: list[str], explicit_domain: str | None = None) -> tuple[str, str]:
    if explicit_domain:
        return explicit_domain, "user_provided"
    matches = _infer_from_terms(text, DOMAIN_TERMS)
    if matches:
        return matches[0], "inferred_from_path_or_note"
    if any(tag in {"sofa", "bed"} for tag in object_tags):
        return "residential", "inferred_from_object_family"
    return "generic", "generic_default"


def _infer_object_tags(text: str, explicit_tags: list[str]) -> tuple[list[str], str]:
    if explicit_tags:
        return explicit_tags, "user_provided"
    matches = _infer_from_terms(text, OBJECT_TERMS)
    if matches:
        return sorted(dict.fromkeys(matches)), "inferred_from_path_or_note"
    return ["unknown"], "unknown_default"


def _infer_style_tags(text: str, explicit_tags: list[str]) -> tuple[list[str], str]:
    if explicit_tags:
        return explicit_tags, "user_provided"
    matches = _infer_from_terms(text, STYLE_TERMS)
    if matches:
        return sorted(dict.fromkeys(matches)), "inferred_from_path_or_note"
    return [], "not_detected"


def _infer_part_tags(object_tags: list[str], explicit_tags: list[str]) -> tuple[list[str], str]:
    if explicit_tags:
        return explicit_tags, "user_provided"
    parts: list[str] = []
    for object_tag in object_tags:
        parts.extend(PARTS_BY_OBJECT.get(object_tag, []))
    if parts:
        return sorted(dict.fromkeys(parts)), "default_parts_by_object_family"
    return [], "not_detected"


def _file_text(source_slug: str, description: str, files: list[RawFile]) -> str:
    pieces = [source_slug, description]
    for raw_file in files:
        pieces.append(str(raw_file.rel_to_original))
    return " ".join(pieces)


def _relative_ref(path: Path, project_root: Path) -> str:
    try:
        rel_path = path.relative_to(project_root)
    except ValueError:
        rel_path = path
    return str(rel_path).replace("\\", "/")


def _source_note_markdown(intake: dict[str, Any]) -> str:
    inferred = intake["inferred_metadata"]
    return "\n".join(
        [
            f"# {intake['source_slug']}",
            "",
            f"Date: {intake['ingest_date']}",
            f"Raw folder: `{intake['raw_original_ref']}`",
            f"Description: {intake.get('description') or 'not provided'}",
            "",
            "## Conservative Defaults",
            "",
            f"- Source type: `{intake['source_type']}`",
            f"- License status: `{intake['license_status']}`",
            f"- Usage boundary: `{intake['usage_boundary']}`",
            f"- Privacy boundary: `{intake['privacy_boundary']}`",
            "",
            "## Agent-Inferred Fields",
            "",
            f"- Domain: `{inferred['domain']}` ({inferred['domain_source']})",
            f"- Object tags: `{', '.join(inferred['object_tags'])}` ({inferred['object_tags_source']})",
            f"- Part tags: `{', '.join(inferred['part_tags']) or 'none'}` ({inferred['part_tags_source']})",
            f"- Style tags: `{', '.join(inferred['style_tags']) or 'none'}` ({inferred['style_tags_source']})",
            f"- View type: `{inferred['view_type']}` ({inferred['view_type_source']})",
            "",
            "## Boundary",
            "",
            "- This batch is reference input only.",
            "- It is not a system asset and does not prove CAD drawing capability.",
            "- Promotion to `libraries/system_library/` requires schema, lineage, checks, evidence boundary, and promotion gate.",
            "",
            "## File Summary",
            "",
            f"- Included files: {intake['file_count']}",
            f"- Skipped files: {len(intake['skipped_files'])}",
            "",
        ]
    )


def _reference_source_markdown(intake: dict[str, Any]) -> str:
    inferred = intake["inferred_metadata"]
    return "\n".join(
        [
            f"# Reference Source: {intake['source_slug']}",
            "",
            f"- Raw folder: `{intake['raw_original_ref']}`",
            f"- License status: `{intake['license_status']}`",
            f"- Usage boundary: `{intake['usage_boundary']}`",
            f"- Privacy boundary: `{intake['privacy_boundary']}`",
            f"- Domain: `{inferred['domain']}`",
            f"- Object tags: `{', '.join(inferred['object_tags'])}`",
            f"- View type: `{inferred['view_type']}`",
            "",
            "This file mirrors raw intake metadata for retrieval and audit. It does not authorize system-library promotion.",
            "",
        ]
    )


def build_raw_reference_intake(
    source_slug: str,
    *,
    project_root: Path,
    description: str = "",
    source_type: str = "user_provided",
    license_status: str = "unknown",
    usage_boundary: str = "reference_only",
    privacy_boundary: str = "raw",
    domain: str | None = None,
    object_tags: str | list[str] | tuple[str, ...] | None = None,
    part_tags: str | list[str] | tuple[str, ...] | None = None,
    style_tags: str | list[str] | tuple[str, ...] | None = None,
    view_type: str | None = None,
    ingest_date: str | None = None,
) -> dict[str, Any]:
    """Scan a raw source folder and build conservative reference intake data."""

    slug = _validate_source_slug(source_slug)
    root = Path(project_root)
    raw_source_dir = root / RAW_LIBRARY_REL / slug
    original_dir = raw_source_dir / "original"
    raw_files, skipped_files = _scan_raw_files(original_dir)

    scan_text = _file_text(slug, description, raw_files)
    explicit_object_tags = _split_tags(object_tags)
    explicit_part_tags = _split_tags(part_tags)
    explicit_style_tags = _split_tags(style_tags)

    inferred_object_tags, object_tags_source = _infer_object_tags(scan_text, explicit_object_tags)
    inferred_part_tags, part_tags_source = _infer_part_tags(inferred_object_tags, explicit_part_tags)
    inferred_style_tags, style_tags_source = _infer_style_tags(scan_text, explicit_style_tags)
    inferred_view_type, view_type_source = _infer_view_type(scan_text, view_type)
    inferred_domain, domain_source = _infer_domain(scan_text, inferred_object_tags, domain)
    ingest_date_text = ingest_date or date.today().isoformat()
    id_source_slug = _id_slug(slug)

    inferred_metadata = {
        "domain": inferred_domain,
        "domain_source": domain_source,
        "object_tags": inferred_object_tags,
        "object_tags_source": object_tags_source,
        "part_tags": inferred_part_tags,
        "part_tags_source": part_tags_source,
        "style_tags": inferred_style_tags,
        "style_tags_source": style_tags_source,
        "view_type": inferred_view_type,
        "view_type_source": view_type_source,
    }

    evidence_boundary = {
        "checked": ["raw folder scanned", "metadata inferred conservatively"],
        "not_checked": [
            "raw CAD geometry was not parsed",
            "license was not verified by the script",
            "drawing correctness was not verified",
            "system_library promotion was not attempted",
        ],
        "assumptions": [
            "folder and file names may describe the object family",
            "unknown fields must remain unknown until user or evidence confirms them",
        ],
    }

    assets: list[dict[str, Any]] = []
    annotations: list[dict[str, Any]] = []
    for index, raw_file in enumerate(raw_files, start=1):
        asset_id = f"ref.{inferred_domain}.{id_source_slug}.{index:04d}"
        source_ref = _relative_ref(raw_file.path, root)
        asset = {
            "id": asset_id,
            "source_type": source_type,
            "source_name": slug,
            "source_uri_or_local_ref": source_ref,
            "license_status": license_status,
            "ingest_date": ingest_date_text,
            "domain": inferred_domain,
            "object_tags": inferred_object_tags,
            "part_tags": inferred_part_tags,
            "style_tags": inferred_style_tags,
            "view_type": inferred_view_type,
            "usage_boundary": usage_boundary,
            "privacy_boundary": privacy_boundary,
            "notes": "Auto raw intake: reference-only candidate; not a system asset.",
            "review_status": "agent_inferred",
            "inference": inferred_metadata,
            "file_info": {
                "relative_to_original": str(raw_file.rel_to_original).replace("\\", "/"),
                "extension": raw_file.path.suffix.lower(),
                "size_bytes": raw_file.size_bytes,
            },
            "evidence_boundary": evidence_boundary,
        }
        assets.append(asset)
        annotations.append(
            {
                "annotation_id": f"ann.{inferred_domain}.{id_source_slug}.{index:04d}",
                "asset_ref": asset_id,
                "object_tags": inferred_object_tags,
                "part_tags": inferred_part_tags,
                "style_tags": inferred_style_tags,
                "view_type": inferred_view_type,
                "notes": "Agent-inferred from source folder, file names, and optional user note.",
                "annotator": "agent:auto_raw_intake",
                "review_status": "agent_inferred",
                "inference_source": ["source_slug", "description", "file_paths"],
            }
        )

    intake: dict[str, Any] = {
        "schema_version": 1,
        "status": "ready" if assets else "no_files",
        "source_slug": slug,
        "description": description,
        "ingest_date": ingest_date_text,
        "source_type": source_type,
        "license_status": license_status,
        "usage_boundary": usage_boundary,
        "privacy_boundary": privacy_boundary,
        "raw_original_ref": _relative_ref(original_dir, root),
        "file_count": len(assets),
        "skipped_files": skipped_files,
        "inferred_metadata": inferred_metadata,
        "assets": assets,
        "annotations": annotations,
        "warnings": [
            "raw intake does not parse CAD geometry",
            "raw intake does not promote anything to system_library",
            "unknown metadata is allowed and should not block intake",
        ],
    }
    intake["source_note_markdown"] = _source_note_markdown(intake)
    intake["reference_source_markdown"] = _reference_source_markdown(intake)
    return intake


def write_raw_reference_intake(intake: dict[str, Any], *, project_root: Path) -> dict[str, str]:
    """Write source notes, reference assets, and inferred annotations."""

    root = Path(project_root)
    source_slug = _validate_source_slug(str(intake["source_slug"]))
    id_source_slug = _id_slug(source_slug)

    written: dict[str, str] = {}
    raw_source_dir = root / RAW_LIBRARY_REL / source_slug
    raw_source_dir.mkdir(parents=True, exist_ok=True)
    source_note_path = raw_source_dir / "source_note.md"
    source_note_path.write_text(str(intake["source_note_markdown"]), encoding="utf-8")
    written["raw_source_note"] = _relative_ref(source_note_path, root)

    reference_sources_dir = root / REFERENCE_LIBRARY_REL / "sources"
    reference_sources_dir.mkdir(parents=True, exist_ok=True)
    reference_source_path = reference_sources_dir / f"{source_slug}.md"
    reference_source_path.write_text(str(intake["reference_source_markdown"]), encoding="utf-8")
    written["reference_source"] = _relative_ref(reference_source_path, root)

    knowledge_source_dir = root / KNOWLEDGE_SOURCE_NOTES_REL
    knowledge_source_dir.mkdir(parents=True, exist_ok=True)
    knowledge_source_path = knowledge_source_dir / f"{source_slug}.md"
    knowledge_source_path.write_text(str(intake["source_note_markdown"]), encoding="utf-8")
    written["knowledge_source_note"] = _relative_ref(knowledge_source_path, root)

    manifest_dir = root / REFERENCE_LIBRARY_REL / "manifests" / source_slug
    annotation_dir = root / REFERENCE_LIBRARY_REL / "annotations" / source_slug
    manifest_dir.mkdir(parents=True, exist_ok=True)
    annotation_dir.mkdir(parents=True, exist_ok=True)

    asset_paths: list[str] = []
    for asset in intake.get("assets", []):
        if not isinstance(asset, dict):
            continue
        filename = f"{asset.get('id', id_source_slug)}.json"
        path = manifest_dir / filename
        path.write_text(json.dumps(asset, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        asset_paths.append(_relative_ref(path, root))
    written["reference_assets"] = ", ".join(asset_paths)

    annotation_paths: list[str] = []
    for annotation in intake.get("annotations", []):
        if not isinstance(annotation, dict):
            continue
        filename = f"{annotation.get('annotation_id', id_source_slug)}.json"
        path = annotation_dir / filename
        path.write_text(json.dumps(annotation, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        annotation_paths.append(_relative_ref(path, root))
    written["annotations"] = ", ".join(annotation_paths)

    return written
