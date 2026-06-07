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

from core.entrypoint_custody.audit import build_entrypoint_custody_audit


def main() -> int:
    parser = argparse.ArgumentParser(description="Run readonly entrypoint custody audit.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument("--manifest", type=Path, default=PROJECT_ROOT / "config" / "entrypoint_custody_manifest.json")
    parser.add_argument("--fail-on-blocked", action="store_true")
    args = parser.parse_args()

    report = build_entrypoint_custody_audit(args.root, manifest_path=args.manifest)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    if args.fail_on_blocked and report.get("status") == "blocked":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
