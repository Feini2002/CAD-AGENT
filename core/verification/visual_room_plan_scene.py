"""Scene drawing data for VCAD-02 visual room plan smoke."""

from __future__ import annotations

from typing import Any

from core.verification.visual_cad_smoke import _arc, _circle, _collect_handles, _line, _point, _rect


PREVIEW_LAYER = "CODEX_PREVIEW"
ROOM_PLAN_BASE_POINT = [190000.0, 90000.0, 0.0]
ROOM_PLAN_SIZE = [8400.0, 5400.0]
ROOM_PLAN_REQUIRED_GROUPS = (
    "segmented_double_wall",
    "door_leaf_and_swing",
    "window_symbol",
    "dimension_chain",
    "room_tags",
    "furniture_cluster",
)
ROOM_PLAN_EXPECTED_TYPE_COUNTS = {
    "arc": 9,
    "circle": 10,
    "dimension": 3,
    "line": 67,
    "polyline": 4,
    "text": 6,
}


def _polyline(
    driver: Any,
    *,
    base: list[float],
    points: list[tuple[float, float]],
    closed: bool,
    layer: str,
    color: str,
) -> object:
    return driver.draw_polyline(
        points=[_point(base, point[0], point[1]) for point in points],
        closed=closed,
        layer=layer,
        color=color,
    )


def _dimension(
    driver: Any,
    *,
    base: list[float],
    start: tuple[float, float],
    end: tuple[float, float],
    text_position: tuple[float, float],
    layer: str,
    color: str,
) -> object:
    return driver.add_dimension(
        start_point=_point(base, start[0], start[1]),
        end_point=_point(base, end[0], end[1]),
        text_position=_point(base, text_position[0], text_position[1]),
        textheight=140,
        layer=layer,
        color=color,
    )


def _text(
    driver: Any,
    *,
    base: list[float],
    text: str,
    position: tuple[float, float],
    height: float,
    layer: str,
    color: str,
) -> object:
    return driver.draw_text(
        text=text,
        position=_point(base, position[0], position[1]),
        height=height,
        layer=layer,
        color=color,
    )


def _draw_room_plan(driver: Any, *, base_point: list[float], layer: str) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    handles: list[str] = []
    draw_log: list[dict[str, Any]] = []

    def add(visual_group: str, label: str, value: object) -> None:
        group_handles = _collect_handles(value)
        handles.extend(group_handles)
        draw_log.append({"visual_group": visual_group, "group": label, "handles": group_handles})

    visual_intent = {
        "version": "0.1",
        "intent": "visual_room_plan_smoke",
        "base_point": base_point,
        "layer": layer,
        "scene": "annotated_office_room_plan",
        "requirements": list(ROOM_PLAN_REQUIRED_GROUPS),
    }
    wall, furniture, annotation, accent = "cyan", "yellow", "white", "green"

    wall_segments = [
        ((0, 0), (900, 0)),
        ((1900, 0), (8400, 0)),
        ((180, 180), (900, 180)),
        ((1900, 180), (8220, 180)),
        ((0, 5400), (5200, 5400)),
        ((7200, 5400), (8400, 5400)),
        ((180, 5220), (5200, 5220)),
        ((7200, 5220), (8220, 5220)),
        ((0, 0), (0, 5400)),
        ((180, 180), (180, 5220)),
        ((8400, 0), (8400, 5400)),
        ((8220, 180), (8220, 5220)),
        ((900, 0), (900, 180)),
        ((1900, 0), (1900, 180)),
    ]
    for index, (start, end) in enumerate(wall_segments, start=1):
        add("segmented_double_wall", f"wall_segment_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    add("door_leaf_and_swing", "door_leaf", _line(driver, base=base_point, start=(900, 180), end=(900, 1180), layer=layer, color=accent))
    add("door_leaf_and_swing", "door_swing", _arc(driver, base=base_point, center=(900, 180), radius=1000, start_angle=0, end_angle=90, layer=layer, color=accent))
    add("door_leaf_and_swing", "door_stop", _line(driver, base=base_point, start=(900, 1180), end=(1010, 1180), layer=layer, color=accent))
    add("door_leaf_and_swing", "door_threshold", _line(driver, base=base_point, start=(900, 90), end=(1900, 90), layer=layer, color=accent))

    window_segments = [
        ((5200, 5400), (7200, 5400)),
        ((5200, 5220), (7200, 5220)),
        ((5200, 5310), (7200, 5310)),
        ((5200, 5220), (5200, 5400)),
        ((7200, 5220), (7200, 5400)),
        ((6200, 5220), (6200, 5400)),
    ]
    for index, (start, end) in enumerate(window_segments, start=1):
        add("window_symbol", f"window_segment_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    zone_specs = [
        ("circulation_boundary", [(1000, 580), (7600, 580), (7600, 1600), (1000, 1600)], True),
        ("work_zone_boundary", [(860, 1800), (4200, 1800), (4200, 4920), (860, 4920)], True),
        ("meeting_zone_boundary", [(4680, 1800), (7840, 1800), (7840, 4920), (4680, 4920)], True),
        ("circulation_arrow", [(1300, 1120), (3500, 1120), (3500, 1380), (3920, 1060)], False),
    ]
    for label, points, closed in zone_specs:
        add("furniture_cluster", label, _polyline(driver, base=base_point, points=points, closed=closed, layer=layer, color=accent))

    add("furniture_cluster", "meeting_table", _rect(driver, base=base_point, x=5480, y=2800, w=1500, d=850, layer=layer, color=furniture))
    meeting_chairs = [(5280, 3080), (5280, 3380), (7180, 3080), (7180, 3380), (5900, 3900), (6600, 3900)]
    for index, center in enumerate(meeting_chairs, start=1):
        add("furniture_cluster", f"meeting_chair_{index}", _circle(driver, base=base_point, center=center, radius=145, layer=layer, color=furniture))
        add("furniture_cluster", f"meeting_chair_back_{index}", _arc(driver, base=base_point, center=center, radius=205, start_angle=205, end_angle=335, layer=layer, color=furniture))
        add("furniture_cluster", f"meeting_chair_split_{index}", _line(driver, base=base_point, start=(center[0] - 110, center[1]), end=(center[0] + 110, center[1]), layer=layer, color=furniture))

    workstation_specs = [(1080, 2760), (2860, 2760)]
    for index, (x, y) in enumerate(workstation_specs, start=1):
        add("furniture_cluster", f"desk_{index}", _rect(driver, base=base_point, x=x, y=y, w=1320, d=720, layer=layer, color=furniture))
        add("furniture_cluster", f"monitor_{index}", _rect(driver, base=base_point, x=x + 460, y=y + 390, w=400, d=210, layer=layer, color="cyan"))
        add("furniture_cluster", f"keyboard_{index}", _line(driver, base=base_point, start=(x + 380, y + 310), end=(x + 960, y + 310), layer=layer, color="cyan"))
        add("furniture_cluster", f"desk_cable_{index}", _line(driver, base=base_point, start=(x + 660, y + 390), end=(x + 660, y + 310), layer=layer, color="cyan"))
        add("furniture_cluster", f"task_chair_{index}", _circle(driver, base=base_point, center=(x + 660, y - 360), radius=210, layer=layer, color=furniture))
        add("furniture_cluster", f"task_chair_back_{index}", _arc(driver, base=base_point, center=(x + 660, y - 255), radius=285, start_angle=205, end_angle=335, layer=layer, color=furniture))
        add("furniture_cluster", f"task_chair_split_{index}", _line(driver, base=base_point, start=(x + 490, y - 320), end=(x + 830, y - 320), layer=layer, color=furniture))
        add("furniture_cluster", f"desk_lamp_{index}", _circle(driver, base=base_point, center=(x + 1080, y + 570), radius=80, layer=layer, color=furniture))

    add("furniture_cluster", "storage_cabinet", _rect(driver, base=base_point, x=700, y=3880, w=880, d=660, layer=layer, color=furniture))
    for index, y in enumerate((4000, 4130, 4260, 4390), start=1):
        add("furniture_cluster", f"storage_drawer_{index}", _line(driver, base=base_point, start=(790, y), end=(1490, y), layer=layer, color=furniture))
    add("furniture_cluster", "storage_pull", _line(driver, base=base_point, start=(1040, 4460), end=(1240, 4460), layer=layer, color=furniture))

    dimension_specs = [
        ("dimension_width", (0, 0), (8400, 0), (4200, -520)),
        ("dimension_depth", (8400, 0), (8400, 5400), (8900, 2700)),
        ("dimension_door", (900, 0), (1900, 0), (1400, -260)),
    ]
    for label, start, end, text_position in dimension_specs:
        add("dimension_chain", label, _dimension(driver, base=base_point, start=start, end=end, text_position=text_position, layer=layer, color=annotation))

    text_specs = [
        ("VCAD-02 ROOM PLAN", (270, 4980), 170, annotation),
        ("OPEN OFFICE", (1500, 4600), 145, annotation),
        ("MEETING", (5730, 4600), 145, annotation),
        ("DOOR 1000", (1080, 360), 120, accent),
        ("WINDOW 2000", (5470, 4980), 120, annotation),
        ("N", (7820, 4860), 150, annotation),
    ]
    for index, (text, position, height, color) in enumerate(text_specs, start=1):
        add("room_tags", f"text_{index}", _text(driver, base=base_point, text=text, position=position, height=height, layer=layer, color=color))
    add("room_tags", "north_arrow_stem", _line(driver, base=base_point, start=(7900, 4500), end=(7900, 4800), layer=layer, color=annotation))
    add("room_tags", "north_arrow_left", _line(driver, base=base_point, start=(7900, 4800), end=(7800, 4640), layer=layer, color=annotation))
    add("room_tags", "north_arrow_right", _line(driver, base=base_point, start=(7900, 4800), end=(8000, 4640), layer=layer, color=annotation))

    return handles, draw_log, visual_intent
