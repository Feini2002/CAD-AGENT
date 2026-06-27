from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Gate0SafetyPolicy:
    preview_only: bool = True
    target_layer: str = "CODEX_PREVIEW"
    save_current_dwg: bool = False
    allow_delete: bool = False
    allow_formal_layer: bool = False
    max_created_entities: int = 100
    max_repair_rounds: int = 2

