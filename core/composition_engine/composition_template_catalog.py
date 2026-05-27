"""Merged composition template catalog loaded from libraries/composition_templates."""

from __future__ import annotations

from typing import Any

from core.composition_engine.catalog_loader import load_composition_template_catalog


COMPOSITION_TEMPLATES: dict[str, dict[str, Any]] = load_composition_template_catalog()
