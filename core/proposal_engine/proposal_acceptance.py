"""BETA-PROPOSAL 01–05 acceptance rollup (non-CAD)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.path_safety import resolve_under_project_output
from core.proposal_engine.benchmark import run_proposal_comparison_benchmark
from core.proposal_engine.confirmed_benchmark import run_proposal_confirmed_benchmark

PARENT_PACKAGE_ID = "BETA-PROPOSAL"
ROLLUP_VERSION = "0.1"


def run_beta_proposal_acceptance_rollup(
    *,
    project_root: Path,
    output_root: Path,
) -> dict[str, Any]:
    project_root = project_root.resolve()
    output_root = resolve_under_project_output(project_root, output_root, label="output_root")
    comparison = run_proposal_comparison_benchmark(project_root=project_root, output_root=output_root / "comparison")
    confirmed = run_proposal_confirmed_benchmark(project_root=project_root, output_root=output_root / "confirmed")

    subpackages = [
        {"subpackage_id": "BETA-PROPOSAL-02", "status": comparison.get("status"), "summary": comparison.get("summary", {})},
        {"subpackage_id": "BETA-PROPOSAL-05", "status": confirmed.get("status"), "summary": confirmed.get("summary", {})},
    ]
    failed = [item for item in subpackages if item["status"] != "pass"]
    rollup = {
        "version": ROLLUP_VERSION,
        "parent_package_id": PARENT_PACKAGE_ID,
        "status": "pass" if not failed else "fail",
        "subpackages": subpackages,
        "geometry_verified_count": 0,
        "non_cad_only": True,
        "allowed_claims": [
            "候选 score_breakdown / ranking_reasons 可机器断言（01）",
            "proposal_comparison_summary benchmark 可断言（02）",
            "用户确认 schema + apply round-trip（03）",
            "局部修改后仅重算 CAD_PLAN（04）",
            "确认后受控 CAD_PLAN bundle + 未选方案证据（05）",
        ],
        "forbidden_claims": [
            "不得将 benchmark pass 或 dry_run valid 等同于 geometry_verified",
            "不得将 comparison_summary 或确认 bundle 当作用户已签署的最终设计决策",
        ],
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "beta_proposal_acceptance_rollup.json").write_text(
        json.dumps(rollup, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return rollup
