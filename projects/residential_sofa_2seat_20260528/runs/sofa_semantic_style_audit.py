"""Backward-compatible re-exports — use core.verification.training_geometry_audit instead."""

from core.verification.training_geometry_audit import (
    detect_forbidden_patterns,
    extract_preview_layout_profile as extract_preview_style_features,
    read_block_layout_profile as read_reference_style_profile,
    run_training_geometry_audit,
)

__all__ = [
    "read_reference_style_profile",
    "extract_preview_style_features",
    "detect_forbidden_patterns",
    "run_training_geometry_audit",
]


def audit_style_vs_reference(preview, reference, **kwargs):
    """Deprecated: use run_training_geometry_audit with checklist."""
    from core.verification.training_geometry_audit import _evaluate_reference_profile_match

    failures: list[str] = []
    deltas: dict[str, float] = {}
    spec = {
        "seat_split_ratio_tol": kwargs.get("tol_split", 0.08),
        "back_band_ratio_tol": kwargs.get("tol_back", 0.08),
        "arm_width_tol_mm": kwargs.get("tol_arm", 35),
        "max_inset_mm": kwargs.get("max_inset_mm", 38),
        "back_band_min": kwargs.get("min_back_band", 0.12),
        "back_band_max": kwargs.get("max_back_band", 0.28),
    }
    _evaluate_reference_profile_match(preview, reference, spec, failures, deltas)
    return {
        "reference_profile": reference,
        "preview_features": preview,
        "style_deltas": deltas,
        "style_failures": failures,
        "style_pass": len(failures) == 0,
    }
