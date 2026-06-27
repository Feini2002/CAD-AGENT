from __future__ import annotations

from typing import Protocol

from cad_agent.domain.drawing import DrawingSnapshot
from cad_agent.domain.patch import CadPatch
from cad_agent.domain.receipt import ExecutionReceipt


class CadBackend(Protocol):
    def inspect_document(self, *, run_id: str) -> DrawingSnapshot:
        """Return a typed drawing snapshot for the current backend state."""
        ...

    def apply_patch(self, patch: CadPatch) -> ExecutionReceipt:
        """Apply a preview-only patch and return a typed receipt."""
        ...

    def readback(self, *, transaction_id: str) -> ExecutionReceipt:
        """Return typed readback for the current transaction scope."""
        ...

    def capture_view(self, *, transaction_id: str, output_path: str) -> str:
        """Capture a visual aid for a transaction and return its artifact path."""
        ...

    def rollback(self, *, rollback_token: str) -> ExecutionReceipt:
        """Rollback a previous transaction by token."""
        ...
