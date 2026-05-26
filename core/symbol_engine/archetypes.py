"""Archetype grammar: required symbol parts and relative placement constraints."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


ArchetypeValidator = Callable[[dict[str, Any], set[str]], list[str]]


@dataclass(frozen=True)
class ArchetypeGrammar:
    archetype: str
    required_kinds: frozenset[str]
    required_one_of: tuple[frozenset[str], ...] = ()
    description: str = ""


ARCHETYPE_GRAMMARS: dict[str, ArchetypeGrammar] = {
    "surface": ArchetypeGrammar(
        archetype="surface",
        required_kinds=frozenset({"outline", "inner_offset"}),
        required_one_of=(
            frozenset({"leg_marker"}),
            frozenset({"split_line"}),
            frozenset({"orientation_marker"}),
        ),
        description="Work surfaces need shell, edge band, and support or facing cue.",
    ),
    "seating": ArchetypeGrammar(
        archetype="seating",
        required_kinds=frozenset({"outline", "orientation_marker"}),
        required_one_of=(frozenset({"seat_split"}), frozenset({"split_line", "thick_band"})),
        description="Seating needs outline, facing, and seat/back readability cues.",
    ),
    "sleeping": ArchetypeGrammar(
        archetype="sleeping",
        required_kinds=frozenset({"outline", "inner_offset", "orientation_marker"}),
        description="Sleeping symbols need frame, mattress inset, and head orientation.",
    ),
    "storage": ArchetypeGrammar(
        archetype="storage",
        required_kinds=frozenset({"outline"}),
        required_one_of=(
            frozenset({"drawer_line"}),
            frozenset({"door_swing"}),
            frozenset({"split_line"}),
        ),
        description="Storage needs shell plus drawer, door, or shelf division.",
    ),
    "display": ArchetypeGrammar(
        archetype="display",
        required_kinds=frozenset({"outline", "split_line", "orientation_marker"}),
        description="Display units need frame, shelf/zone splits, and viewing direction.",
    ),
    "workstation": ArchetypeGrammar(
        archetype="workstation",
        required_kinds=frozenset({"outline", "inner_offset", "orientation_marker"}),
        required_one_of=(
            frozenset({"leg_marker"}),
            frozenset({"split_line"}),
            frozenset({"thick_band"}),
        ),
        description="Workstations need desktop inset, facing, and zone/support markers.",
    ),
}


def _part_kinds(spec: dict[str, Any]) -> set[str]:
    kinds: set[str] = set()
    for part in spec.get("parts", []):
        if isinstance(part, dict) and isinstance(part.get("kind"), str):
            kinds.add(part["kind"])
    return kinds


def _params(part: dict[str, Any]) -> dict[str, Any]:
    raw = part.get("params")
    return raw if isinstance(raw, dict) else {}


def _check_required_kinds(grammar: ArchetypeGrammar, kinds: set[str]) -> list[str]:
    errors: list[str] = []
    missing = grammar.required_kinds - kinds
    if missing:
        errors.append(
            f"$.archetype `{grammar.archetype}` requires parts kinds: "
            f"{sorted(grammar.required_kinds)}; missing {sorted(missing)}."
        )
    if grammar.required_one_of:
        satisfied = any(group.issubset(kinds) for group in grammar.required_one_of)
        if not satisfied:
            options = " OR ".join("{" + ", ".join(sorted(group)) + "}" for group in grammar.required_one_of)
            errors.append(
                f"$.archetype `{grammar.archetype}` requires at least one readable part group: {options}."
            )
    return errors


def _position_constraints_surface(spec: dict[str, Any], kinds: set[str]) -> list[str]:
    errors: list[str] = []
    footprint = spec.get("footprint", {})
    width = float(footprint.get("width_mm", 0))
    depth = float(footprint.get("depth_mm", 0))
    limit = min(width, depth) * 0.45
    for part in spec.get("parts", []):
        if not isinstance(part, dict):
            continue
        if part.get("kind") == "inner_offset":
            inset = float(_params(part).get("inset_mm", 0))
            if inset <= 0 or inset >= limit:
                errors.append(
                    "$.parts inner_offset inset_mm must be > 0 and < 45% of the smaller footprint dimension for surface."
                )
        if part.get("kind") == "orientation_marker":
            facing = str(spec.get("orientation", {}).get("facing", "unspecified"))
            axis = str(_params(part).get("axis", "y"))
            if facing in {"north", "south"} and axis != "y":
                errors.append("$.parts orientation_marker axis should be 'y' when facing north/south on surface.")
            if facing in {"east", "west"} and axis != "x":
                errors.append("$.parts orientation_marker axis should be 'x' when facing east/west on surface.")
    return errors


def _position_constraints_seating(spec: dict[str, Any], kinds: set[str]) -> list[str]:
    errors: list[str] = []
    footprint = spec.get("footprint", {})
    depth = float(footprint.get("depth_mm", 0))
    for part in spec.get("parts", []):
        if not isinstance(part, dict):
            continue
        if part.get("kind") == "seat_split":
            ratio = float(_params(part).get("span_ratio", 0.35))
            if ratio <= 0.1 or ratio >= 0.65:
                errors.append("$.parts seat_split span_ratio should sit between seat and back zones (0.1~0.65).")
        if part.get("kind") == "thick_band" and depth > 0:
            band = float(_params(part).get("band_width_mm", 0))
            if band <= 0 or band >= depth * 0.5:
                errors.append("$.parts thick_band band_width_mm should be within the rear half of seating depth.")
    return errors


def _position_constraints_sleeping(spec: dict[str, Any], kinds: set[str]) -> list[str]:
    errors: list[str] = []
    footprint = spec.get("footprint", {})
    width = float(footprint.get("width_mm", 0))
    depth = float(footprint.get("depth_mm", 0))
    limit = min(width, depth) * 0.4
    for part in spec.get("parts", []):
        if isinstance(part, dict) and part.get("kind") == "inner_offset":
            inset = float(_params(part).get("inset_mm", 0))
            if inset <= 0 or inset >= limit:
                errors.append(
                    "$.parts inner_offset inset_mm must define a mattress inset within the bed frame for sleeping."
                )
    return errors


def _position_constraints_storage(spec: dict[str, Any], kinds: set[str]) -> list[str]:
    errors: list[str] = []
    footprint = spec.get("footprint", {})
    height = float(footprint.get("height_mm", footprint.get("depth_mm", 0)))
    for part in spec.get("parts", []):
        if not isinstance(part, dict):
            continue
        if part.get("kind") == "drawer_line":
            spacing = float(_params(part).get("line_spacing_mm", 0))
            if spacing <= 0 or (height > 0 and spacing >= height * 0.8):
                errors.append("$.parts drawer_line line_spacing_mm should divide the storage front into readable drawers.")
        if part.get("kind") == "door_swing" and str(part.get("role", "")) != "door_front":
            errors.append("$.parts door_swing should use role 'door_front' for storage archetype.")
    return errors


def _position_constraints_display(spec: dict[str, Any], kinds: set[str]) -> list[str]:
    errors: list[str] = []
    for part in spec.get("parts", []):
        if isinstance(part, dict) and part.get("kind") == "split_line":
            axis = str(_params(part).get("axis", "x"))
            if axis != "x":
                errors.append("$.parts display split_line should use axis 'x' for shelf bands.")
    return errors


def _position_constraints_workstation(spec: dict[str, Any], kinds: set[str]) -> list[str]:
    errors: list[str] = []
    errors.extend(_position_constraints_surface(spec, kinds))
    if "split_line" in kinds and "leg_marker" not in kinds:
        for part in spec.get("parts", []):
            if isinstance(part, dict) and part.get("kind") == "split_line":
                role = str(part.get("role", ""))
                if role not in {"keyboard_zone", "screen_zone", "zone_split"}:
                    errors.append(
                        "$.parts workstation split_line should declare keyboard_zone, screen_zone, or zone_split role."
                    )
    return errors


_POSITION_CHECKS: dict[str, ArchetypeValidator] = {
    "surface": _position_constraints_surface,
    "seating": _position_constraints_seating,
    "sleeping": _position_constraints_sleeping,
    "storage": _position_constraints_storage,
    "display": _position_constraints_display,
    "workstation": _position_constraints_workstation,
}


def get_archetype_grammar(archetype: str) -> ArchetypeGrammar | None:
    return ARCHETYPE_GRAMMARS.get(archetype)


def validate_archetype_grammar(spec: dict[str, Any]) -> list[str]:
    """Validate SYMBOL_SPEC parts against archetype required kinds and placement rules."""

    archetype = str(spec.get("archetype", ""))
    grammar = get_archetype_grammar(archetype)
    if grammar is None:
        return [f"$.archetype `{archetype}` is not a registered archetype grammar."]

    kinds = _part_kinds(spec)
    errors = _check_required_kinds(grammar, kinds)
    position_check = _POSITION_CHECKS.get(archetype)
    if position_check is not None:
        errors.extend(position_check(spec, kinds))
    return errors
