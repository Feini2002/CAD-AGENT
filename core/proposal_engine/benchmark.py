"""Proposal comparison benchmark helpers (BETA-PROPOSAL-02)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.benchmarks.runner import run_benchmark_suite

DEFAULT_BENCHMARK_REL = Path("examples/benchmarks/proposal_comparison_benchmark.json")


def default_proposal_comparison_benchmark_path(project_root: Path) -> Path:
    return project_root / DEFAULT_BENCHMARK_REL


def run_proposal_comparison_benchmark(
    *,
    project_root: Path,
    output_root: Path,
    suite_path: Path | None = None,
) -> dict[str, Any]:
    suite = suite_path or default_proposal_comparison_benchmark_path(project_root)
    return run_benchmark_suite(suite, output_root=output_root)
