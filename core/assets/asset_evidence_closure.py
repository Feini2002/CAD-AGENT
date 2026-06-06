"""Close stale active evidence references without fabricating old artifacts."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


EVIDENCE_LIST_KEYS = {"evidenceRefs", "refs"}
EVIDENCE_DETAIL_KEYS = {
    "summary",
    "report",
    "screenshot",
    "focusedScreenshot",
    "reportPath",
    "screenshotPath",
    "preview",
    "previewPath",
}
VISUAL_DETAIL_KEYS = {"screenshot", "focusedScreenshot", "screenshotPath", "preview", "previewPath"}
LOCAL_REF_PREFIXES = ("output/", "projects/", "docs/", "agents/", "libraries/")


def _normalize_ref(value: str) -> str:
    return value.replace("\\", "/").strip()


def _looks_like_local_ref(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = _normalize_ref(value)
    if not text or text.startswith(("http://", "https://")):
        return False
    if "<" in text or ">" in text:
        return False
    return text.startswith(LOCAL_REF_PREFIXES)


def _rel_ref(path: Path, root: Path) -> str:
    resolved = path if path.is_absolute() else root / path
    try:
        return resolved.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return _normalize_ref(str(path))


def _unique(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = _normalize_ref(str(item))
        if text and text not in seen:
            seen.add(text)
            result.append(text)
    return result


def _ref_exists(root: Path, ref: str) -> bool:
    return (root / _normalize_ref(ref)).is_file()


def _replacement_for_detail_key(key: str, report_ref: str, visual_ref: str | None) -> str:
    if key in VISUAL_DETAIL_KEYS and visual_ref:
        return visual_ref
    return report_ref


def _active_replacement_refs(report_ref: str, visual_ref: str | None, extra_active_refs: list[str]) -> list[str]:
    refs = [report_ref]
    if visual_ref:
        refs.append(visual_ref)
    refs.extend(extra_active_refs)
    return _unique(refs)


def _close_value(
    value: Any,
    *,
    root: Path,
    report_ref: str,
    visual_ref: str | None,
    extra_active_refs: list[str],
    archived: list[dict[str, Any]],
    path: str,
) -> Any:
    replacements = _active_replacement_refs(report_ref, visual_ref, extra_active_refs)
    if isinstance(value, list):
        changed_items: list[Any] = []
        for index, item in enumerate(value):
            changed_items.append(
                _close_value(
                    item,
                    root=root,
                    report_ref=report_ref,
                    visual_ref=visual_ref,
                    extra_active_refs=extra_active_refs,
                    archived=archived,
                    path=f"{path}[{index}]",
                )
            )
        return changed_items

    if not isinstance(value, dict):
        return value

    changed = dict(value)
    for key, item in list(changed.items()):
        key_text = str(key)
        child_path = f"{path}/{key_text}" if path else key_text
        if key_text in EVIDENCE_LIST_KEYS and isinstance(item, list):
            kept: list[str] = []
            missing: list[str] = []
            for ref in item:
                if not _looks_like_local_ref(ref):
                    continue
                normalized = _normalize_ref(str(ref))
                if _ref_exists(root, normalized):
                    kept.append(normalized)
                else:
                    missing.append(normalized)
            if missing:
                archived.extend(
                    {
                        "path": child_path,
                        "oldRef": missing_ref,
                        "replacementRefs": replacements,
                    }
                    for missing_ref in missing
                )
                changed[key_text] = _unique([*kept, *replacements])
            continue
        if key_text in EVIDENCE_DETAIL_KEYS and _looks_like_local_ref(item):
            normalized = _normalize_ref(str(item))
            if not _ref_exists(root, normalized):
                replacement = _replacement_for_detail_key(key_text, report_ref, visual_ref)
                archived.append(
                    {
                        "path": child_path,
                        "oldRef": normalized,
                        "replacementRefs": [replacement],
                    }
                )
                changed[key_text] = replacement
            continue
        if isinstance(item, (dict, list)):
            changed[key_text] = _close_value(
                item,
                root=root,
                report_ref=report_ref,
                visual_ref=visual_ref,
                extra_active_refs=extra_active_refs,
                archived=archived,
                path=child_path,
            )
    return changed


def _active_refs(value: Any) -> list[str]:
    refs: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in EVIDENCE_LIST_KEYS and isinstance(item, list):
                refs.extend(_normalize_ref(str(ref)) for ref in item if _looks_like_local_ref(ref))
            if key_text in EVIDENCE_DETAIL_KEYS and _looks_like_local_ref(item):
                refs.append(_normalize_ref(str(item)))
            if isinstance(item, (dict, list)):
                refs.extend(_active_refs(item))
    elif isinstance(value, list):
        for item in value:
            refs.extend(_active_refs(item))
    return _unique(refs)


def _attach_asset_closure(payload: dict[str, Any], archived_by_asset: dict[str, list[dict[str, Any]]], *, reason: str) -> None:
    assets = payload.get("assets")
    if not isinstance(assets, list):
        return
    for index, asset in enumerate(assets):
        if not isinstance(asset, dict):
            continue
        asset_id = str(asset.get("assetId") or asset.get("id") or "")
        archived = archived_by_asset.get(asset_id) or archived_by_asset.get(str(index))
        if not archived:
            continue
        deduped: list[dict[str, Any]] = []
        seen_old_refs: set[str] = set()
        for item in archived:
            old_ref = str(item.get("oldRef") or "")
            if old_ref in seen_old_refs:
                continue
            seen_old_refs.add(old_ref)
            deduped.append(item)
        asset["evidenceClosure"] = {
            "status": "closed",
            "reason": reason,
            "archivedMissingRefs": deduped,
            "activeEvidenceRefs": _active_refs(asset),
        }


def close_missing_asset_evidence_refs(
    *,
    project_root: Path,
    json_paths: list[Path],
    closure_report_path: Path,
    report_ref: str,
    visual_ref: str | None = None,
    extra_active_refs: list[str] | None = None,
    reason: str,
) -> dict[str, Any]:
    """Archive missing active evidence refs and replace them with current refs."""
    root = Path(project_root)
    report_ref = _normalize_ref(report_ref)
    visual_ref = _normalize_ref(visual_ref) if visual_ref else None
    extra_active_refs = _unique([*(extra_active_refs or []), _rel_ref(closure_report_path, root)])
    replacement_refs = _active_replacement_refs(report_ref, visual_ref, extra_active_refs)
    missing_replacement_refs = [ref for ref in replacement_refs if not _ref_exists(root, ref) and ref != _rel_ref(closure_report_path, root)]
    if missing_replacement_refs:
        raise ValueError(f"replacement evidence refs are missing: {missing_replacement_refs}")

    generated_at = datetime.now(UTC).replace(microsecond=0).isoformat()
    all_archived: list[dict[str, Any]] = []
    touched_files: list[str] = []
    for json_path in json_paths:
        path = Path(json_path)
        payload = json.loads(path.read_text(encoding="utf-8-sig"))
        archived: list[dict[str, Any]] = []
        updated = _close_value(
            payload,
            root=root,
            report_ref=report_ref,
            visual_ref=visual_ref,
            extra_active_refs=extra_active_refs,
            archived=archived,
            path="",
        )
        if archived:
            archived_by_asset: dict[str, list[dict[str, Any]]] = {}
            if isinstance(updated, dict) and isinstance(updated.get("assets"), list):
                for index, asset in enumerate(updated["assets"]):
                    if not isinstance(asset, dict):
                        continue
                    asset_id = str(asset.get("assetId") or asset.get("id") or "")
                    asset_archived = [
                        item for item in archived if str(item.get("path", "")).startswith(f"assets[{index}]")
                    ]
                    if asset_archived:
                        archived_by_asset[asset_id or str(index)] = asset_archived
            if isinstance(updated, dict):
                _attach_asset_closure(updated, archived_by_asset, reason=reason)
                updated["updatedAt"] = generated_at
            path.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            touched_files.append(_rel_ref(path, root))
            for item in archived:
                item["jsonPath"] = _rel_ref(path, root)
            all_archived.extend(archived)

    closure_report = {
        "status": "pass",
        "generatedAt": generated_at,
        "reason": reason,
        "touchedFiles": touched_files,
        "replacementRefs": replacement_refs,
        "missingRefCount": len({str(item.get("oldRef")) for item in all_archived}),
        "archivedMissingRefs": all_archived,
        "evidenceBoundary": {
            "checked": [
                "active evidence refs point to existing current files",
                "missing historical refs moved to archivedMissingRefs",
            ],
            "notChecked": [
                "historical missing files were not recreated",
                "CAD geometry is proven only by replacement reports, not by archived refs",
            ],
        },
    }
    closure_report_path.parent.mkdir(parents=True, exist_ok=True)
    closure_report_path.write_text(json.dumps(closure_report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return closure_report
