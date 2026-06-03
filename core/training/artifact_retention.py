from __future__ import annotations

import json
import shutil
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterable


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
REFERENCE_SUFFIXES = {".json", ".md", ".txt", ".js", ".py", ".html"}
DEFAULT_ARCHIVE_ROOT = Path("archive") / "training_artifacts"


def _resolve_under_root(path: Path, root: Path) -> Path:
    resolved = path if path.is_absolute() else root / path
    resolved = resolved.resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"path must stay under project root: {resolved}") from exc
    return resolved


def _display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path)


def _reference_variants(path: Path, root: Path) -> set[str]:
    rel = _display_path(path, root)
    return {
        rel,
        rel.replace("/", "\\"),
        str(path),
        str(path).replace("\\", "/"),
    }


def _iter_image_candidates(scan_roots: Iterable[Path], root: Path, archive_root: Path) -> list[Path]:
    candidates: list[Path] = []
    resolved_archive = archive_root.resolve()
    for raw_scan_root in scan_roots:
        scan_root = _resolve_under_root(raw_scan_root, root)
        if not scan_root.exists():
            continue
        for path in scan_root.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in IMAGE_SUFFIXES:
                continue
            try:
                path.resolve().relative_to(resolved_archive)
                continue
            except ValueError:
                candidates.append(path.resolve())
    return sorted(candidates, key=lambda item: _display_path(item, root))


def _iter_reference_files(reference_roots: Iterable[Path], root: Path, archive_root: Path) -> list[Path]:
    files: list[Path] = []
    resolved_archive = archive_root.resolve()
    for raw_reference_root in reference_roots:
        reference_root = _resolve_under_root(raw_reference_root, root)
        if reference_root.is_file():
            roots = [reference_root]
        elif reference_root.exists():
            roots = [path for path in reference_root.rglob("*") if path.is_file()]
        else:
            roots = []
        for path in roots:
            if path.suffix.lower() not in REFERENCE_SUFFIXES:
                continue
            try:
                path.resolve().relative_to(resolved_archive)
                continue
            except ValueError:
                files.append(path.resolve())
    return sorted(set(files), key=lambda item: _display_path(item, root))


def _read_reference_texts(reference_files: Iterable[Path]) -> list[tuple[Path, str]]:
    texts: list[tuple[Path, str]] = []
    for path in reference_files:
        try:
            texts.append((path, path.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
    return texts


def _find_reference(path: Path, root: Path, reference_texts: Iterable[tuple[Path, str]]) -> str | None:
    variants = _reference_variants(path, root)
    for reference_path, text in reference_texts:
        if any(variant in text for variant in variants):
            return _display_path(reference_path, root)
    return None


def _latest_images_by_dir(candidates: Iterable[Path], keep_latest_per_dir: int) -> set[Path]:
    if keep_latest_per_dir <= 0:
        return set()
    grouped: dict[Path, list[Path]] = {}
    for path in candidates:
        grouped.setdefault(path.parent, []).append(path)

    keep: set[Path] = set()
    for paths in grouped.values():
        ordered = sorted(paths, key=lambda item: (item.stat().st_mtime_ns, str(item)))
        keep.update(ordered[-keep_latest_per_dir:])
    return keep


def run_training_artifact_retention(
    *,
    project_root: Path,
    scan_roots: list[Path],
    reference_roots: list[Path],
    archive_root: Path | None = None,
    keep_latest_per_dir: int = 1,
    write: bool = False,
    output_path: Path | None = None,
) -> dict[str, Any]:
    root = project_root.resolve()
    archive_base = _resolve_under_root(archive_root or DEFAULT_ARCHIVE_ROOT, root)
    candidates = _iter_image_candidates(scan_roots, root, archive_base)
    reference_files = _iter_reference_files(reference_roots, root, archive_base)
    reference_texts = _read_reference_texts(reference_files)
    latest_keep = _latest_images_by_dir(candidates, keep_latest_per_dir)

    kept: list[dict[str, str]] = []
    archive_planned: list[dict[str, str]] = []
    for candidate in candidates:
        reference = _find_reference(candidate, root, reference_texts)
        if reference:
            kept.append({"path": _display_path(candidate, root), "reason": "referenced", "reference": reference})
        elif candidate in latest_keep:
            kept.append({"path": _display_path(candidate, root), "reason": "latest_preview"})
        else:
            relative = candidate.resolve().relative_to(root)
            archive_path = archive_base / relative
            archive_planned.append(
                {
                    "path": _display_path(candidate, root),
                    "reason": "unreferenced_old_preview",
                    "archivePath": _display_path(archive_path, root),
                }
            )

    archived: list[dict[str, str]] = []
    if write:
        for item in archive_planned:
            source = root / item["path"]
            target = root / item["archivePath"]
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                stamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
                target = target.with_name(f"{target.stem}-{stamp}{target.suffix}")
            shutil.move(str(source), str(target))
            archived.append({**item, "archivePath": _display_path(target, root)})

    report = {
        "version": "0.1",
        "status": "pass",
        "generatedAt": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "write": write,
        "policy": {
            "mode": "archive_unreferenced_old_screenshots",
            "keepLatestPerDir": keep_latest_per_dir,
            "deleteFiles": False,
            "archiveRoot": _display_path(archive_base, root),
        },
        "scanRoots": [_display_path(_resolve_under_root(path, root), root) for path in scan_roots],
        "referenceRoots": [_display_path(_resolve_under_root(path, root), root) for path in reference_roots],
        "candidateCount": len(candidates),
        "referenceFileCount": len(reference_files),
        "keptCount": len(kept),
        "archivePlannedCount": len(archive_planned),
        "archivedCount": len(archived),
        "kept": kept,
        "archivePlanned": archive_planned,
        "archived": archived,
    }

    if output_path:
        resolved_output = _resolve_under_root(output_path, root)
        resolved_output.parent.mkdir(parents=True, exist_ok=True)
        resolved_output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        report["outputPath"] = _display_path(resolved_output, root)
    return report
