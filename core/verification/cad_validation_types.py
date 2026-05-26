"""Shared types for CAD validation runners."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


CommandRunner = Callable[[list[str], Path, int], CommandResult]


@dataclass(frozen=True)
class ValidationStep:
    id: str
    title: str
    command: list[str]
    failure_category: str
    required: bool = True
    timeout_seconds: int = 120
    cad_required: bool = False
    stdout_artifact: str | None = None
