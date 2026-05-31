#!/usr/bin/env python
"""Run a lightweight CAD Agent self-check without touching the active DWG."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from core.execution.execute_plan import execute_plan_file
    from core.plan_engine.validate_plan import load_json, validate_plan
    from core.verification.render_preview import get_preview_capabilities
except ImportError:  # pragma: no cover - compatibility with legacy layout.
    from scripts.execute_plan import execute_plan_file
    from scripts.render_preview import get_preview_capabilities
    from scripts.validate_plan import load_json, validate_plan


REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "当前状态入口.md",
    "长期规则入口.md",
    "变更记录入口.md",
    "问题风险入口.md",
    "路线图入口.md",
    "CAD卡壳排障入口.md",
    "docs/ROADMAP.md",
    "docs/roadmap/current.md",
    "docs/status/current.md",
    "docs/status/changelog.md",
    "docs/status/issues.md",
    "docs/governance/cad-agent-rules.md",
    "docs/runbooks/blocker-playbook.md",
    "CORE_RESTRUCTURE_PLAN.md",
    "CORE_STATUS.md",
    "core/plan_engine/validate_plan.py",
    "core/plan_engine/dry_run_plan.py",
    "core/execution/execute_plan.py",
    "core/verification/render_preview.py",
    "core/verification/inspect_dwg.py",
    "schemas/cad_plan.schema.json",
    "examples/plans/draw_test_cabinet.json",
    "scripts/validate_plan.py",
    "scripts/dry_run_plan.py",
    "scripts/execute_plan.py",
    "scripts/render_preview.py",
    "scripts/inspect_dwg.py",
]


class RecordingDriver:
    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, object]]] = []

    def draw_rectangle(self, **kwargs: object) -> None:
        self.calls.append(("draw_rectangle", kwargs))

    def draw_text(self, **kwargs: object) -> None:
        self.calls.append(("draw_text", kwargs))

    def add_dimension(self, **kwargs: object) -> None:
        self.calls.append(("add_dimension", kwargs))


def check_result(name: str, status: str, detail: str, **extra: object) -> dict[str, object]:
    return {
        "name": name,
        "status": status,
        "detail": detail,
        **extra,
    }


def check_required_files(root: Path) -> dict[str, object]:
    missing = [path for path in REQUIRED_FILES if not (root / path).exists()]
    if missing:
        return check_result("required_files", "fail", "Some required CAD Agent files are missing.", missing=missing)
    return check_result("required_files", "pass", "Required CAD Agent files are present.")


def check_sample_plan_validates(root: Path) -> dict[str, object]:
    plan_path = root / "examples" / "plans" / "draw_test_cabinet.json"
    plan = load_json(plan_path)
    errors = validate_plan(plan)
    if errors:
        return check_result("sample_plan_validates", "fail", "Sample CAD_PLAN is invalid.", errors=errors)
    return check_result("sample_plan_validates", "pass", "Sample CAD_PLAN validates.")


def check_preview_execution_without_cad(root: Path) -> dict[str, object]:
    plan_path = root / "examples" / "plans" / "draw_test_cabinet.json"
    driver = RecordingDriver()
    result = execute_plan_file(plan_path, driver=driver)

    if result.get("status") != "executed":
        return check_result("preview_execution_without_cad", "fail", "Preview execution did not report executed.", result=result)
    if result.get("layer") != "CODEX_PREVIEW":
        return check_result("preview_execution_without_cad", "fail", "Preview execution used a non-preview layer.", result=result)
    if len(driver.calls) < 1:
        return check_result("preview_execution_without_cad", "fail", "Preview execution made no driver calls.", result=result)

    return check_result(
        "preview_execution_without_cad",
        "pass",
        "Preview execution can run against a recording driver without touching CAD.",
        calls=len(driver.calls),
        result=result,
    )


def check_screenshot_tooling(root: Path) -> dict[str, object]:
    output = root / "output" / "previews" / "preview.png"
    capabilities = get_preview_capabilities(output)
    if "screen" not in capabilities.get("capture_modes", []):
        return check_result(
            "screenshot_tooling",
            "warn",
            "Screenshot tool exists, but screen capture dependency is unavailable.",
            capabilities=capabilities,
        )
    return check_result(
        "screenshot_tooling",
        "pass",
        "Screenshot tooling can capture the visible screen when requested.",
        capabilities=capabilities,
    )


def run_self_check(root: Path | str | None = None) -> dict[str, object]:
    project_root = Path(root) if root is not None else Path(__file__).resolve().parents[2]
    project_root = project_root.resolve()

    checks: list[dict[str, object]] = []
    for check in [
        check_required_files,
        check_sample_plan_validates,
        check_preview_execution_without_cad,
        check_screenshot_tooling,
    ]:
        try:
            checks.append(check(project_root))
        except Exception as exc:  # Keep self-check useful even when one probe breaks.
            checks.append(check_result(check.__name__, "fail", str(exc), error_type=type(exc).__name__))

    statuses = {str(check["status"]) for check in checks}
    if "fail" in statuses:
        status = "fail"
    elif "warn" in statuses:
        status = "warn"
    else:
        status = "pass"

    return {
        "status": status,
        "root": str(project_root),
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAD Agent self-checks.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()

    report: dict[str, Any] = run_self_check(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
