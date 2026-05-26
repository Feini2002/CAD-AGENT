"""Project sample benchmark helpers (BETA-PROJECT-SAMPLE-04)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.benchmarks.runner import run_benchmark_suite
from core.project_samples.workflow import default_project_root


DEFAULT_BENCHMARK_REL = Path("examples/benchmarks/project_sample_benchmark.json")


def default_project_sample_benchmark_path(project_root: Path | None = None) -> Path:
    root = project_root or default_project_root()
    return root / DEFAULT_BENCHMARK_REL


def run_project_sample_benchmark(
    *,
    project_root: Path | None = None,
    output_root: Path,
    suite_path: Path | None = None,
) -> dict[str, Any]:
    """Run the project sample benchmark suite and return benchmark_summary payload."""

    root = project_root or default_project_root()
    suite = suite_path or default_project_sample_benchmark_path(root)
    return run_benchmark_suite(suite, output_root=output_root)
