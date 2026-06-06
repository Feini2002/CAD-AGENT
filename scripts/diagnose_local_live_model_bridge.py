#!/usr/bin/env python
"""Diagnose a local-live-model-bridge Worker run package without side effects."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT  # noqa: F401
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT  # noqa: F401

from core.orchestrator.local_live_model_bridge_diagnostics import diagnose_run
from core.runtime.encoding_guard import configure_utf8_process


def main(argv: list[str] | None = None) -> int:
    configure_utf8_process()
    parser = argparse.ArgumentParser(description="Diagnose which local live model bridge proof layer is blocked.")
    parser.add_argument("--run-dir", type=Path, required=True, help="Run directory containing worker_run_state.json.")
    parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path.")
    parser.add_argument("--fail-on-blocked", action="store_true", help="Return exit code 1 when any proof layer is blocked.")
    args = parser.parse_args(argv)

    report = diagnose_run(args.run_dir)
    text = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 1 if args.fail_on_blocked and report.get("status") == "blocked" else 0


if __name__ == "__main__":
    raise SystemExit(main())
