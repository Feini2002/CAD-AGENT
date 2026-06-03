from __future__ import annotations

import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_ROOT = PROJECT_ROOT / "output" / "test_artifacts"


def artifact_path(*parts: str) -> Path:
    path = ARTIFACT_ROOT.joinpath(*parts)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def temporary_artifact_dir(prefix: str = "tmp") -> Iterator[Path]:
    """Create a writable temporary directory under the repo artifact root."""

    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    root = ARTIFACT_ROOT.resolve()
    path = (ARTIFACT_ROOT / f"{prefix}_{uuid4().hex}").resolve()
    if not path.is_relative_to(root):
        raise ValueError(f"temporary artifact dir escaped artifact root: {path}")
    path.mkdir(parents=True, exist_ok=False)
    try:
        yield path
    finally:
        if path.exists() and path.resolve().is_relative_to(root):
            shutil.rmtree(path)
