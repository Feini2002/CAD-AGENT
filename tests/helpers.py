from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = PROJECT_ROOT / "output" / "test_artifacts"


def artifact_path(*parts: str) -> Path:
    path = ARTIFACT_ROOT.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path
