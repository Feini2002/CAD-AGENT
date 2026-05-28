#!/usr/bin/env python3
"""Build a lightweight CAD asset retrieval pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from _bootstrap import PROJECT_ROOT, ensure_project_root_on_path

ensure_project_root_on_path()

from core.assets import build_retrieval_pack, write_retrieval_pack  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a CAD asset retrieval pack from local indexes.")
    parser.add_argument("--brief", required=True, help="User brief or object request.")
    parser.add_argument("--scene", default="residential")
    parser.add_argument("--case-dir", type=Path)
    parser.add_argument("--output", "--output-path", dest="output_path", type=Path)
    args = parser.parse_args()

    case_dir = args.case_dir
    if case_dir is not None and not case_dir.is_absolute():
        case_dir = PROJECT_ROOT / case_dir

    pack = build_retrieval_pack(args.brief, scene=args.scene, case_dir=case_dir, project_root=PROJECT_ROOT)
    if args.output_path:
        output_path = args.output_path
        if not output_path.is_absolute():
            output_path = PROJECT_ROOT / output_path
        write_retrieval_pack(pack, output_path)
        pack["written_to"] = str(output_path.relative_to(PROJECT_ROOT))

    print(json.dumps(pack, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
