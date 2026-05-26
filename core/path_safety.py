"""Shared path safety helpers for CAD Agent runners."""

from __future__ import annotations

import re
from pathlib import Path


SAFE_PATH_SEGMENT_RE = re.compile(r"^[A-Za-z0-9_.-]+$")


def is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def find_project_root(start: Path | None = None) -> Path:
    """Find the repository root by walking upward from a path."""

    base = (start or Path.cwd()).resolve()
    candidates = [base, *base.parents]
    if base.suffix:
        candidates = [base.parent, *base.parents]
    for candidate in candidates:
        if (candidate / "CORE_RESTRUCTURE_PLAN.md").is_file() and (candidate / "core").is_dir():
            return candidate
    raise ValueError(f"could not locate project root from {base}")


def resolve_under_project_root(project_root: Path, path: Path, *, label: str) -> Path:
    root = project_root.resolve()
    resolved = (path if path.is_absolute() else root / path).resolve()
    if not is_relative_to(resolved, root):
        raise ValueError(f"{label} must stay under project root")
    return resolved


def resolve_under_project_output(project_root: Path, path: Path, *, label: str) -> Path:
    root = project_root.resolve()
    output_root = (root / "output").resolve()
    resolved = (path if path.is_absolute() else root / path).resolve()
    if not is_relative_to(resolved, output_root):
        raise ValueError(f"{label} must stay under project output directory")
    return resolved


def validate_safe_path_segment(value: object, *, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty safe path segment")
    if value in {".", ".."} or not SAFE_PATH_SEGMENT_RE.fullmatch(value):
        raise ValueError(f"{label} must be a safe path segment")
    return value
