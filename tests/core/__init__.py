"""Core test package.

When unittest is run with ``discover -s tests``, this directory is imported as
``core``. Extend the package path so imports such as ``core.execution`` still
resolve to the project Core modules.
"""

from pathlib import Path

__path__.append(str(Path(__file__).resolve().parents[2] / "core"))
