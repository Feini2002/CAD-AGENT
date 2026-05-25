from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from _bootstrap import PROJECT_ROOT
except ModuleNotFoundError as exc:
    if exc.name != "_bootstrap":
        raise
    from scripts._bootstrap import PROJECT_ROOT
from core.maintenance.repo_audit import run_repo_audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Run CAD Agent repository hardening audit.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--max-python-lines", type=int, default=500)
    parser.add_argument("--fail-on-findings", action="store_true")
    args = parser.parse_args()

    report = run_repo_audit(args.root, max_python_lines=args.max_python_lines)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_findings and report["status"] == "findings":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
