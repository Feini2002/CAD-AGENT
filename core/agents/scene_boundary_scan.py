"""Static boundary scan for lightweight Scene Agent trees (X-SCENE-03)."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

AGENT_FILE_SUFFIXES = {".py", ".md", ".json", ".yaml", ".yml"}

# Documents the forbidden catalog itself; not subject to substring scan.
BOUNDARY_RULES_DOC = "SCENE_AGENT_RULES.md"
NON_SCENE_AGENT_DIRS = {"pipeline"}

# (rule_id, forbidden_substring)
FORBIDDEN_SUBSTRINGS: tuple[tuple[str, str], ...] = (
    ("cad_execute", "execute_plan_file"),
    ("cad_execute", "execute_plan("),
    ("cad_execute", "AutoCADComDriver"),
    ("cad_execute", "insert_block_alpha"),
    ("cad_execute", "ensure_controlled_block_definition"),
    ("cad_readback", "snapshot_modelspace"),
    ("cad_readback", "inspect_dwg"),
    ("cad_readback", "readback_geometry"),
    ("cad_com", "AddLine("),
    ("cad_com", "AddText("),
    ("cad_com", "AddDimAligned("),
    ("cad_com", "AddCircle("),
    ("cad_com", "AddPolyline("),
    ("cad_com", "win32com"),
    ("cad_com", "pythoncom"),
    ("cad_com", "Dispatch("),
    ("cad_io", "save_dwg"),
    ("cad_io", "delete_entity"),
    ("plan_validate", "validate_plan("),
    ("plan_validate", "dry_run_plan"),
    ("plan_validate", "run_cad_validation"),
    ("pipeline_impl", "run_blank_shell_pipeline"),
    ("pipeline_impl", "build_blank_shell_candidate_sets"),
    ("pipeline_impl", "build_blank_shell_comparison_detail"),
    ("layout_algorithm", "generate_circulation_candidates"),
    ("layout_algorithm", "split_zones("),
    ("layout_algorithm", "create_zone_placements"),
    ("layout_algorithm", "create_layout_candidates"),
    ("geometry_lib", "geometry_backends"),
    ("geometry_lib", "rect_intersects"),
    ("geometry_lib", "path_to_rect_strips"),
    ("geometry_lib", "rect_contains"),
    ("geometry_lib", "subtract_no_place_zones"),
)

# (rule_id, import prefix) — only checked on lines that look like Python imports
FORBIDDEN_IMPORT_PREFIXES: tuple[tuple[str, str], ...] = (
    ("core_import", "from core.workflows"),
    ("core_import", "from core.layout_engine"),
    ("core_import", "from core.cad_io"),
    ("core_import", "from core.geometry_backends"),
    ("core_import", "from core.execution"),
    ("core_import", "from core.plan_engine"),
    ("core_import", "from core.verification"),
    ("core_import", "from core.proposal_engine"),
    ("core_import", "import core.workflows"),
    ("core_import", "import core.layout_engine"),
    ("core_import", "import core.cad_io"),
    ("core_import", "import core.geometry_backends"),
    ("core_import", "import core.execution"),
)


@dataclass(frozen=True)
class BoundaryViolation:
    relative_path: str
    rule_id: str
    detail: str


def _non_scene_agent_path(relative_path: Path) -> bool:
    return bool(relative_path.parts and relative_path.parts[0] in NON_SCENE_AGENT_DIRS)


def iter_agent_files(agent_root: Path) -> list[Path]:
    if not agent_root.is_dir():
        return []
    return sorted(
        path
        for path in agent_root.rglob("*")
        if path.is_file() and path.suffix.lower() in AGENT_FILE_SUFFIXES
        and not _non_scene_agent_path(path.relative_to(agent_root))
    )


def _documentation_only_path(relative_path: str) -> bool:
    """Scene rules document Core entrypoints; substring guard applies to prefs/json only."""

    return relative_path == BOUNDARY_RULES_DOC or relative_path.endswith("/rules.md")


def scan_text(*, relative_path: str, text: str) -> list[BoundaryViolation]:
    violations: list[BoundaryViolation] = []
    if not _documentation_only_path(relative_path):
        for rule_id, pattern in FORBIDDEN_SUBSTRINGS:
            if pattern in text:
                violations.append(
                    BoundaryViolation(
                        relative_path=relative_path,
                        rule_id=rule_id,
                        detail=f"forbidden substring {pattern!r}",
                    )
                )
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped.startswith(("import ", "from ")):
            continue
        for rule_id, prefix in FORBIDDEN_IMPORT_PREFIXES:
            if stripped.startswith(prefix):
                violations.append(
                    BoundaryViolation(
                        relative_path=relative_path,
                        rule_id=rule_id,
                        detail=f"line {line_number}: forbidden import {prefix!r}",
                    )
                )
    return violations


def scan_agent_tree(agent_root: Path) -> list[BoundaryViolation]:
    violations: list[BoundaryViolation] = []
    for path in iter_agent_files(agent_root):
        relative = path.relative_to(agent_root).as_posix()
        text = path.read_text(encoding="utf-8")
        violations.extend(scan_text(relative_path=relative, text=text))
    return violations
