"""De-identified project sample directory protocol and README/manifest scanner (BETA-PROJECT-SAMPLE-01)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.schemas.validator import validate_json


MANIFEST_SCHEMA = "project_sample_manifest.schema.json"
FORBIDDEN_SOURCE_SUFFIXES = {".dwg", ".dxf", ".bak"}
SCHEMA_ROOT = Path(__file__).resolve().parents[1] / "schemas"

REQUIRED_PROJECTS_README_SECTIONS = (
    "用途",
    "目录结构",
    "脱敏要求",
    "可提交字段",
    "禁止事项",
    "证据声称边界",
)

REQUIRED_SAMPLE_README_SECTIONS = (
    "样本标识",
    "输入说明",
    "预期输出",
    "不可声称",
)

REQUIRED_SAMPLE_DIRS = ("input", "expected")
REQUIRED_SAMPLE_FILES = (
    "README.md",
    "sample.manifest.json",
    "expected/expected_notes.md",
)


@dataclass(frozen=True)
class ProtocolViolation:
    sample_id: str
    rule_id: str
    detail: str


def _missing_sections(text: str, required: tuple[str, ...]) -> list[str]:
    return [title for title in required if title not in text]


def _load_manifest(manifest_path: Path) -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON: {exc}"]
    if not isinstance(manifest, dict):
        return None, ["manifest must be a JSON object"]
    schema_path = SCHEMA_ROOT / MANIFEST_SCHEMA
    validation_errors = validate_json(schema_path, manifest_path)
    if validation_errors:
        errors.extend(validation_errors)
    return manifest, errors


def resolve_manifest_input_path(sample_dir: Path, relative_path: str) -> Path:
    """Resolve a manifest input path while keeping it inside the sample directory."""

    base = sample_dir.resolve()
    path = (sample_dir / relative_path).resolve()
    try:
        path.relative_to(base)
    except ValueError as exc:
        raise ValueError(f"manifest input path escapes sample directory: {relative_path}") from exc
    return path


def scan_project_sample(sample_dir: Path, *, projects_root: Path) -> dict[str, Any]:
    sample_id = sample_dir.name
    violations: list[ProtocolViolation] = []

    for rel in REQUIRED_SAMPLE_FILES:
        if not (sample_dir / rel).is_file():
            violations.append(
                ProtocolViolation(sample_id, "required_file", f"missing {rel}")
            )

    for dirname in REQUIRED_SAMPLE_DIRS:
        path = sample_dir / dirname
        if not path.is_dir():
            violations.append(
                ProtocolViolation(sample_id, "required_dir", f"missing directory {dirname}/")
            )

    readme_path = sample_dir / "README.md"
    if readme_path.is_file():
        missing = _missing_sections(readme_path.read_text(encoding="utf-8"), REQUIRED_SAMPLE_README_SECTIONS)
        for title in missing:
            violations.append(
                ProtocolViolation(sample_id, "sample_readme_section", f"missing section: {title}")
            )

    manifest_path = sample_dir / "sample.manifest.json"
    manifest: dict[str, Any] | None = None
    if manifest_path.is_file():
        manifest, manifest_errors = _load_manifest(manifest_path)
        for message in manifest_errors:
            violations.append(ProtocolViolation(sample_id, "manifest_invalid", message))
        if manifest is not None:
            declared_id = str(manifest.get("sample_id", ""))
            if declared_id != sample_id:
                violations.append(
                    ProtocolViolation(
                        sample_id,
                        "manifest_sample_id",
                        f"sample_id {declared_id!r} != directory {sample_id!r}",
                    )
                )
            for entry in manifest.get("input_files", []):
                if not isinstance(entry, dict):
                    continue
                rel = str(entry.get("path", ""))
                if not rel:
                    continue
                try:
                    input_path = resolve_manifest_input_path(sample_dir, rel)
                except ValueError:
                    violations.append(
                        ProtocolViolation(
                            sample_id,
                            "manifest_input_outside_sample",
                            f"input file must stay inside sample directory: {rel}",
                        )
                    )
                    continue
                if not input_path.is_file():
                    violations.append(
                        ProtocolViolation(
                            sample_id,
                            "manifest_input_missing",
                            f"input file not found: {rel}",
                        )
                    )

    for path in sample_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() in FORBIDDEN_SOURCE_SUFFIXES:
            rel = path.relative_to(sample_dir).as_posix()
            violations.append(
                ProtocolViolation(
                    sample_id,
                    "forbidden_source_file",
                    f"deidentified sample must not commit {rel}",
                )
            )

    status = "pass" if not violations else "fail"
    return {
        "sample_id": sample_id,
        "path": sample_dir.relative_to(projects_root).as_posix(),
        "status": status,
        "manifest": manifest,
        "violations": [
            {"rule_id": v.rule_id, "detail": v.detail} for v in violations
        ],
    }


def scan_projects_root(projects_root: Path) -> dict[str, Any]:
    """Scan projects/ README and every sample directory for protocol compliance."""

    violations: list[dict[str, str]] = []
    readme_path = projects_root / "README.md"
    if not readme_path.is_file():
        violations.append({"rule_id": "projects_readme", "detail": "missing projects/README.md"})
    else:
        missing = _missing_sections(readme_path.read_text(encoding="utf-8"), REQUIRED_PROJECTS_README_SECTIONS)
        for title in missing:
            violations.append(
                {"rule_id": "projects_readme_section", "detail": f"missing section: {title}"}
            )

    samples: list[dict[str, Any]] = []
    for child in sorted(projects_root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("."):
            continue
        samples.append(scan_project_sample(child, projects_root=projects_root))

    sample_failures = [sample for sample in samples if sample["status"] != "pass"]
    status = "pass" if not violations and not sample_failures else "fail"
    return {
        "version": "0.1",
        "status": status,
        "projects_readme": str(readme_path.relative_to(projects_root.parent)).replace("\\", "/")
        if readme_path.is_file()
        else "",
        "sample_count": len(samples),
        "samples": samples,
        "root_violations": violations,
    }
