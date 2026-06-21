"""Derived training workbench view models.

The workbench package builds compact, read-only data for the local HTML
dashboard. It must not become a source of truth for training, Table C, or CAD
geometry claims.
"""

from .flightdeck import build_contract_workbench_panel, build_workbench_v3

__all__ = ["build_contract_workbench_panel", "build_workbench_v3"]
