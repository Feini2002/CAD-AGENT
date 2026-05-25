"""Load and normalize reusable CAD style profiles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STYLE_LIBRARY = PROJECT_ROOT / "libraries" / "styles"


class UnknownStyleError(ValueError):
    """Raised when a requested style preset does not exist."""


def load_style_profile(style: str, *, library: Path = STYLE_LIBRARY) -> dict[str, Any]:
    path = library / f"{style}.json"
    if not path.exists():
        available = sorted(item.stem for item in library.glob("*.json"))
        raise UnknownStyleError(f"Unknown style '{style}'. Available styles: {available}")
    with path.open("r", encoding="utf-8") as file:
        profile = json.load(file)
    if not isinstance(profile, dict):
        raise ValueError(f"Style profile must be a JSON object: {path}")
    return profile


def label_policy(profile: dict[str, Any]) -> str:
    tokens = profile.get("tokens", {})
    if not isinstance(tokens, dict):
        return "object_name"
    policy = tokens.get("label_policy")
    return policy if isinstance(policy, str) else "object_name"
