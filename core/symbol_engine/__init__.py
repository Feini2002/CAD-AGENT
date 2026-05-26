"""CAD symbol grammar: SYMBOL_SPEC / SYMBOL_GRAPH models and semantic guards."""

from core.symbol_engine.archetypes import ARCHETYPE_GRAMMARS, validate_archetype_grammar
from core.symbol_engine.fallback_policy import (
    FALLBACK_RENDER_TIERS,
    assess_render_tiers,
    detect_silent_degradation,
    resolve_symbol_render_resolution,
    tier_evidence_state,
)
from core.symbol_engine.readability import (
    READABILITY_STATUSES,
    build_symbol_readability_report,
    evaluate_object_spec_readability,
)
from core.symbol_engine.object_to_symbol import (
    OBJECT_TYPE_TO_ARCHETYPE,
    ObjectToSymbolResult,
    object_spec_to_symbol_spec,
)
from core.symbol_engine.primitives import (
    SUPPORTED_PART_KINDS,
    symbol_spec_to_cad_plan,
    symbol_spec_to_glyph_primitives,
)
from core.symbol_engine.symbol_spec import (
    FALLBACK_MODES,
    SYMBOL_PART_KINDS,
    validate_symbol_graph,
    validate_symbol_spec,
)

__all__ = [
    "ARCHETYPE_GRAMMARS",
    "FALLBACK_RENDER_TIERS",
    "READABILITY_STATUSES",
    "OBJECT_TYPE_TO_ARCHETYPE",
    "ObjectToSymbolResult",
    "FALLBACK_MODES",
    "SUPPORTED_PART_KINDS",
    "SYMBOL_PART_KINDS",
    "assess_render_tiers",
    "build_symbol_readability_report",
    "detect_silent_degradation",
    "evaluate_object_spec_readability",
    "object_spec_to_symbol_spec",
    "resolve_symbol_render_resolution",
    "symbol_spec_to_cad_plan",
    "tier_evidence_state",
    "symbol_spec_to_glyph_primitives",
    "validate_archetype_grammar",
    "validate_symbol_graph",
    "validate_symbol_spec",
]
