"""Load project sample fixtures via manifest (BETA-PROJECT-SAMPLE-02)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.drawing_analysis.shell_loader import load_manual_shell
from core.project_model.project_builder import ProjectBuildResult, build_project_model
from core.schemas.validator import validate_json
from core.project_samples.protocol import SCHEMA_ROOT, resolve_manifest_input_path, scan_project_sample


class ProjectSampleLoadError(ValueError):
    """Raised when a project sample cannot be loaded."""


INPUT_ROLE_LOADERS = {
    "shell_model": "load_shell",
    "design_brief": "load_json",
    "drawing_model": "load_json",
    "cad_context": "load_json",
    "project_model": "load_json",
}


def default_projects_root() -> Path:
    return Path(__file__).resolve().parents[2] / "projects"


def sample_dir(projects_root: Path, sample_id: str) -> Path:
    path = projects_root / sample_id
    if not path.is_dir():
        raise ProjectSampleLoadError(f"sample directory not found: {path}")
    return path


def load_sample_manifest(sample_dir: Path) -> dict[str, Any]:
    manifest_path = sample_dir / "sample.manifest.json"
    if not manifest_path.is_file():
        raise ProjectSampleLoadError(f"missing manifest: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ProjectSampleLoadError("sample.manifest.json must be an object")
    errors = validate_json(SCHEMA_ROOT / "project_sample_manifest.schema.json", manifest_path)
    if errors:
        raise ProjectSampleLoadError(f"invalid manifest: {errors}")
    return manifest


def resolve_input_path(sample_dir: Path, manifest: dict[str, Any], role: str) -> Path:
    for entry in manifest.get("input_files", []):
        if not isinstance(entry, dict):
            continue
        if str(entry.get("role")) == role:
            rel = str(entry.get("path", ""))
            try:
                path = resolve_manifest_input_path(sample_dir, rel)
            except ValueError as exc:
                raise ProjectSampleLoadError(str(exc)) from exc
            if not path.is_file():
                raise ProjectSampleLoadError(f"missing {role} file: {rel}")
            return path
    raise ProjectSampleLoadError(f"role {role!r} not declared in manifest input_files")


def load_sample_inputs(
    sample_id: str,
    *,
    projects_root: Path | None = None,
) -> dict[str, Any]:
    """Load all manifest-declared JSON inputs for a sample."""

    root = projects_root or default_projects_root()
    directory = sample_dir(root, sample_id)
    scan = scan_project_sample(directory, projects_root=root)
    if scan["status"] != "pass":
        raise ProjectSampleLoadError(f"sample {sample_id!r} failed protocol scan: {scan['violations']}")

    manifest = load_sample_manifest(directory)
    if str(manifest.get("sample_id")) != sample_id:
        raise ProjectSampleLoadError(
            f"manifest sample_id {manifest.get('sample_id')!r} != {sample_id!r}"
        )

    payloads: dict[str, Any] = {"manifest": manifest, "sample_dir": str(directory)}
    for entry in manifest.get("input_files", []):
        if not isinstance(entry, dict):
            continue
        role = str(entry.get("role", ""))
        path = resolve_input_path(directory, manifest, role)
        if role == "shell_model":
            payloads[role] = load_manual_shell(path)
        else:
            payloads[role] = json.loads(path.read_text(encoding="utf-8"))
    return payloads


def load_sample_shell(
    sample_id: str,
    *,
    projects_root: Path | None = None,
) -> dict[str, Any]:
    inputs = load_sample_inputs(sample_id, projects_root=projects_root)
    shell = inputs.get("shell_model")
    if not isinstance(shell, dict):
        raise ProjectSampleLoadError(f"sample {sample_id!r} has no shell_model input")
    return shell


def build_sample_project_model(
    sample_id: str,
    *,
    projects_root: Path | None = None,
) -> ProjectBuildResult:
    """Load sample brief + drawing + shell and build PROJECT_MODEL."""

    inputs = load_sample_inputs(sample_id, projects_root=projects_root)
    brief = inputs.get("design_brief")
    drawing = inputs.get("drawing_model")
    shell = inputs.get("shell_model")
    if not isinstance(brief, dict) or not isinstance(drawing, dict) or not isinstance(shell, dict):
        raise ProjectSampleLoadError(
            f"sample {sample_id!r} requires design_brief, drawing_model, and shell_model inputs"
        )
    return build_project_model(brief, drawing, shell_model=shell)


def compare_project_model_to_expected(
    actual: dict[str, Any],
    expected: dict[str, Any],
) -> list[str]:
    """Return human-readable diffs for key PROJECT_MODEL fields."""

    errors: list[str] = []
    for key in (
        "project_id",
        "brief_id",
        "drawing_model_id",
        "shell_id",
        "domain",
        "units",
    ):
        if actual.get(key) != expected.get(key):
            errors.append(f"{key}: expected {expected.get(key)!r}, got {actual.get(key)!r}")
    actual_space = (actual.get("spaces") or [{}])[0]
    expected_space = (expected.get("spaces") or [{}])[0]
    if actual_space.get("space_id") != expected_space.get("space_id"):
        errors.append("spaces[0].space_id mismatch")
    if actual_space.get("boundary") != expected_space.get("boundary"):
        errors.append("spaces[0].boundary mismatch")
    for constraint in (
        "fixed_obstacle:column-01",
        "no_place_zone:column-01-clearance",
        "opening:entrance-main",
    ):
        if constraint not in actual.get("constraints", []):
            errors.append(f"missing constraint {constraint!r}")
    ctx = actual.get("shell_context", {})
    if not ctx.get("openings") or not ctx.get("fixed_obstacles"):
        errors.append("shell_context missing openings or fixed_obstacles")
    return errors
