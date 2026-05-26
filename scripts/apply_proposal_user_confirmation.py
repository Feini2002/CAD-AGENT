#!/usr/bin/env python3
"""Apply PROPOSAL_USER_CONFIRMATION to a design proposal (BETA-PROPOSAL-03)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from core.proposal_engine.user_confirmation import (  # noqa: E402
    apply_user_confirmation,
    load_user_confirmation,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply user confirmation to a design proposal JSON file.")
    parser.add_argument("--proposal", type=Path, required=True)
    parser.add_argument("--confirmation", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    proposal = json.loads(args.proposal.read_text(encoding="utf-8"))
    confirmation = load_user_confirmation(args.confirmation)
    updated = apply_user_confirmation(proposal, confirmation)
    output = args.output or args.proposal
    output.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output.resolve()), "confirmed_candidate_id": updated.get("confirmed_candidate_id")}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
