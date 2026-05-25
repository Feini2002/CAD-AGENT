"""Layout candidate scoring helpers."""

from __future__ import annotations

from typing import Any


def score_checks(checks: list[dict[str, Any]]) -> float:
    if not checks:
        return 0.5
    failures = sum(1 for check in checks if check.get("status") == "fail")
    warnings = sum(1 for check in checks if check.get("status") == "warning")
    score = 1.0 - failures * 0.35 - warnings * 0.1
    return max(0.0, min(1.0, score))
