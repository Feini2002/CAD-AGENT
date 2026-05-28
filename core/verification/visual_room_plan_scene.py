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
    "arc": 11,
    "circle": 12,
    "dimension": 4,
    "line": 94,
    "polyline": 5,
    "text": 10,
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
        ("VCAD-EXPAND ROOM", (270, 4980), 170, annotation),
        ("OPEN OFFICE", (1500, 4600), 145, annotation),
        ("MEETING", (5730, 4600), 145, annotation),
        ("DOOR 1000", (1080, 360), 120, accent),
        ("WINDOW 2000", (5470, 4980), 120, annotation),
        ("N", (7820, 4860), 150, annotation),
        ("1:100", (320, 1080), 110, annotation),
        ("WALL", (520, 860), 95, annotation),
        ("FURN", (520, 700), 95, annotation),
        ("ZONE", (520, 540), 95, annotation),
    ]
    for index, (text, position, height, color) in enumerate(text_specs, start=1):
        add("room_tags", f"text_{index}", _text(driver, base=base_point, text=text, position=position, height=height, layer=layer, color=color))
    add("room_tags", "north_arrow_stem", _line(driver, base=base_point, start=(7900, 4500), end=(7900, 4800), layer=layer, color=annotation))
    add("room_tags", "north_arrow_left", _line(driver, base=base_point, start=(7900, 4800), end=(7800, 4640), layer=layer, color=annotation))
    add("room_tags", "north_arrow_right", _line(driver, base=base_point, start=(7900, 4800), end=(8000, 4640), layer=layer, color=annotation))

    add("room_tags", "legend_frame", _rect(driver, base=base_point, x=240, y=420, w=2100, d=980, layer=layer, color=annotation))
    for index, (y, color) in enumerate(((760, wall), (600, furniture), (440, accent)), start=1):
        add("room_tags", f"legend_swatch_{index}", _rect(driver, base=base_point, x=360, y=y, w=260, d=90, layer=layer, color=color))

    for index, start_y in enumerate(range(2100, 4700, 360), start=1):
        add(
            "furniture_cluster",
            f"work_zone_hatch_{index}",
            _line(
                driver,
                base=base_point,
                start=(980, start_y),
                end=(4040, start_y + 520),
                layer=layer,
                color=accent,
            ),
        )

    plant_centers = [(3520, 4320), (7360, 2280)]
    for index, center in enumerate(plant_centers, start=1):
        add("furniture_cluster", f"plant_pot_{index}", _circle(driver, base=base_point, center=center, radius=120, layer=layer, color=furniture))
        add(
            "furniture_cluster",
            f"plant_leaf_{index}",
            _arc(driver, base=base_point, center=center, radius=190, start_angle=35, end_angle=145, layer=layer, color=accent),
        )

    add(
        "dimension_chain",
        "meeting_table_width",
        _dimension(driver, base=base_point, start=(5480, 2600), end=(6980, 2600), text_position=(6230, 2360), layer=layer, color=annotation),
    )
    add("furniture_cluster", "scale_bar_base", _line(driver, base=base_point, start=(320, 1240), end=(1320, 1240), layer=layer, color=annotation))
    add("furniture_cluster", "scale_bar_tick_a", _line(driver, base=base_point, start=(320, 1180), end=(320, 1300), layer=layer, color=annotation))
    add("furniture_cluster", "scale_bar_tick_b", _line(driver, base=base_point, start=(1320, 1180), end=(1320, 1300), layer=layer, color=annotation))
    add(
        "furniture_cluster",
        "reception_counter",
        _polyline(
            driver,
            base=base_point,
            points=[(1180, 1280), (2860, 1280), (2860, 1580), (1180, 1580)],
            closed=True,
            layer=layer,
            color=furniture,
        ),
    )

    return handles, draw_log, visual_intent


RETAIL_SHOWROOM_BASE_POINT = [200500.0, 90000.0, 0.0]
RETAIL_SHOWROOM_SIZE = [7200.0, 4800.0]
RETAIL_SHOWROOM_REQUIRED_GROUPS = ROOM_PLAN_REQUIRED_GROUPS
RETAIL_SHOWROOM_EXPECTED_TYPE_COUNTS = {
    "arc": 2,
    "circle": 12,
    "dimension": 3,
    "line": 63,
    "polyline": 1,
    "text": 8,
}


def _draw_retail_showroom(driver: Any, *, base_point: list[float], layer: str) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    handles: list[str] = []
    draw_log: list[dict[str, Any]] = []

    def add(visual_group: str, label: str, value: object) -> None:
        group_handles = _collect_handles(value)
        handles.extend(group_handles)
        draw_log.append({"visual_group": visual_group, "group": label, "handles": group_handles})

    visual_intent = {
        "version": "0.1",
        "intent": "visual_retail_showroom_smoke",
        "base_point": base_point,
        "layer": layer,
        "scene": "retail_showroom_plan",
        "requirements": list(RETAIL_SHOWROOM_REQUIRED_GROUPS),
    }
    wall, furniture, annotation, accent = "cyan", "yellow", "white", "green"
    w, d = 7200.0, 4800.0

    outer = [
        ((0, 0), (w, 0)),
        ((w, 0), (w, d)),
        ((w, d), (0, d)),
        ((0, d), (0, 0)),
        ((180, 180), (w - 180, 180)),
        ((w - 180, 180), (w - 180, d - 180)),
        ((w - 180, d - 180), (180, d - 180)),
        ((180, d - 180), (180, 180)),
    ]
    for index, (start, end) in enumerate(outer, start=1):
        add("segmented_double_wall", f"wall_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    add("door_leaf_and_swing", "entry_leaf", _line(driver, base=base_point, start=(3200, 180), end=(3200, 1180), layer=layer, color=accent))
    add("door_leaf_and_swing", "entry_swing", _arc(driver, base=base_point, center=(3200, 180), radius=1000, start_angle=0, end_angle=90, layer=layer, color=accent))
    add("door_leaf_and_swing", "entry_jamb", _arc(driver, base=base_point, center=(4200, 180), radius=120, start_angle=90, end_angle=180, layer=layer, color=accent))
    add("door_leaf_and_swing", "entry_threshold", _line(driver, base=base_point, start=(3200, 90), end=(4200, 90), layer=layer, color=accent))

    window_segments = [((1200, d), (2400, d)), ((4800, d), (6000, d)), ((1200, d - 180), (2400, d - 180))]
    for index, (start, end) in enumerate(window_segments, start=1):
        add("window_symbol", f"window_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    islands = [(900, 1400, 1800, 1200), (4200, 1400, 1800, 1200), (900, 3200, 1800, 1100)]
    for index, (x, y, iw, ih) in enumerate(islands, start=1):
        add("furniture_cluster", f"display_island_{index}", _rect(driver, base=base_point, x=x, y=y, w=iw, d=ih, layer=layer, color=furniture))
        for grid_y in range(int(y + 200), int(y + ih - 100), 280):
            add(
                "furniture_cluster",
                f"display_grid_h_{index}_{grid_y}",
                _line(driver, base=base_point, start=(x + 100, grid_y), end=(x + iw - 100, grid_y), layer=layer, color=accent),
            )
        for grid_x in range(int(x + 200), int(x + iw - 100), 320):
            add(
                "furniture_cluster",
                f"display_grid_v_{index}_{grid_x}",
                _line(driver, base=base_point, start=(grid_x, y + 100), end=(grid_x, y + ih - 100), layer=layer, color=accent),
            )
        for corner, (cx, cy) in enumerate(
            ((x + 180, y + 180), (x + iw - 180, y + 180), (x + iw - 180, y + ih - 180), (x + 180, y + ih - 180)),
            start=1,
        ):
            add(
                "furniture_cluster",
                f"display_pedestal_{index}_{corner}",
                _circle(driver, base=base_point, center=(cx, cy), radius=90, layer=layer, color=furniture),
            )

    add("furniture_cluster", "cashier", _polyline(
        driver,
        base=base_point,
        points=[(5600, 420), (6800, 420), (6800, 1100), (5600, 1100)],
        closed=True,
        layer=layer,
        color=furniture,
    ))
    add("furniture_cluster", "fitting_room", _rect(driver, base=base_point, x=5600, y=2800, w=1200, d=1500, layer=layer, color=furniture))
    add("furniture_cluster", "fitting_door", _line(driver, base=base_point, start=(6200, 2800), end=(6200, 3100), layer=layer, color=accent))

    for label, start, end, text_position in (
        ("dimension_width", (0, 0), (w, 0), (w / 2, -480)),
        ("dimension_depth", (w, 0), (w, d), (w + 420, d / 2)),
        ("dimension_entry", (3200, 0), (4200, 0), (3700, -260)),
    ):
        add("dimension_chain", label, _dimension(driver, base=base_point, start=start, end=end, text_position=text_position, layer=layer, color=annotation))

    for index, (text, position, height) in enumerate(
        (
            ("VCAD-03 RETAIL", (320, 4500), 160),
            ("SHOWROOM", (1200, 4200), 140),
            ("DISPLAY A", (1200, 2000), 120),
            ("DISPLAY B", (4500, 2000), 120),
            ("CASHIER", (5700, 1280), 120),
            ("FITTING", (5720, 4100), 120),
            ("1:100", (320, 900), 110),
            ("N", (6600, 4400), 140),
        ),
        start=1,
    ):
        add("room_tags", f"text_{index}", _text(driver, base=base_point, text=text, position=position, height=height, layer=layer, color=annotation))

    add("room_tags", "north_stem", _line(driver, base=base_point, start=(6700, 4000), end=(6700, 4300), layer=layer, color=annotation))
    add("room_tags", "north_left", _line(driver, base=base_point, start=(6700, 4300), end=(6600, 4160), layer=layer, color=annotation))
    add("room_tags", "north_right", _line(driver, base=base_point, start=(6700, 4300), end=(6800, 4160), layer=layer, color=annotation))
    add("room_tags", "legend_frame", _rect(driver, base=base_point, x=240, y=360, w=1600, d=720, layer=layer, color=annotation))

    return handles, draw_log, visual_intent


BATHROOM_PLAN_BASE_POINT = [211000.0, 90000.0, 0.0]
BATHROOM_PLAN_SIZE = [3600.0, 2400.0]
BATHROOM_PLAN_REQUIRED_GROUPS = ROOM_PLAN_REQUIRED_GROUPS
BATHROOM_PLAN_EXPECTED_TYPE_COUNTS = {
    "arc": 3,
    "circle": 5,
    "dimension": 3,
    "line": 60,
    "polyline": 1,
    "text": 8,
}

KITCHEN_PLAN_BASE_POINT = [221500.0, 90000.0, 0.0]
KITCHEN_PLAN_SIZE = [4800.0, 3600.0]
KITCHEN_PLAN_REQUIRED_GROUPS = ROOM_PLAN_REQUIRED_GROUPS
KITCHEN_PLAN_EXPECTED_TYPE_COUNTS = {
    "arc": 1,
    "circle": 12,
    "dimension": 3,
    "line": 67,
    "polyline": 2,
    "text": 8,
}


def _draw_bathroom_plan(driver: Any, *, base_point: list[float], layer: str) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    handles: list[str] = []
    draw_log: list[dict[str, Any]] = []

    def add(visual_group: str, label: str, value: object) -> None:
        group_handles = _collect_handles(value)
        handles.extend(group_handles)
        draw_log.append({"visual_group": visual_group, "group": label, "handles": group_handles})

    visual_intent = {
        "version": "0.1",
        "intent": "visual_bathroom_plan_smoke",
        "base_point": base_point,
        "layer": layer,
        "scene": "residential_bathroom_plan",
        "requirements": list(BATHROOM_PLAN_REQUIRED_GROUPS),
    }
    wall, fixture, annotation, accent = "cyan", "yellow", "white", "green"
    w, d = 3600.0, 2400.0

    outer = [
        ((0, 0), (w, 0)),
        ((w, 0), (w, d)),
        ((w, d), (0, d)),
        ((0, d), (0, 0)),
        ((150, 150), (w - 150, 150)),
        ((w - 150, 150), (w - 150, d - 150)),
        ((w - 150, d - 150), (150, d - 150)),
        ((150, d - 150), (150, 150)),
    ]
    for index, (start, end) in enumerate(outer, start=1):
        add("segmented_double_wall", f"wall_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    add("door_leaf_and_swing", "entry_leaf", _line(driver, base=base_point, start=(150, 150), end=(150, 950), layer=layer, color=accent))
    add("door_leaf_and_swing", "entry_swing", _arc(driver, base=base_point, center=(150, 150), radius=800, start_angle=0, end_angle=90, layer=layer, color=accent))
    add("door_leaf_and_swing", "entry_jamb", _line(driver, base=base_point, start=(150, 950), end=(260, 950), layer=layer, color=accent))

    for index, (start, end) in enumerate(
        (((1800, d), (2400, d)), ((1800, d - 150), (2400, d - 150)), ((2100, d - 150), (2100, d))),
        start=1,
    ):
        add("window_symbol", f"window_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    add("furniture_cluster", "toilet_tank", _rect(driver, base=base_point, x=420, y=1680, w=520, d=280, layer=layer, color=fixture))
    add("furniture_cluster", "toilet_bowl", _circle(driver, base=base_point, center=(680, 1480), radius=220, layer=layer, color=fixture))
    add("furniture_cluster", "toilet_seat", _arc(driver, base=base_point, center=(680, 1480), radius=280, start_angle=200, end_angle=340, layer=layer, color=fixture))

    add("furniture_cluster", "lavatory_counter", _rect(driver, base=base_point, x=2680, y=1680, w=720, d=420, layer=layer, color=fixture))
    add("furniture_cluster", "lavatory_basin", _circle(driver, base=base_point, center=(3040, 1880), radius=160, layer=layer, color=fixture))
    add("furniture_cluster", "lavatory_faucet_stem", _line(driver, base=base_point, start=(3040, 2100), end=(3040, 2220), layer=layer, color=accent))
    add("furniture_cluster", "lavatory_faucet_spout", _line(driver, base=base_point, start=(2920, 2220), end=(3160, 2220), layer=layer, color=accent))
    add("furniture_cluster", "mirror", _rect(driver, base=base_point, x=2780, y=2120, w=520, d=80, layer=layer, color=annotation))

    add("furniture_cluster", "bathtub_outer", _rect(driver, base=base_point, x=900, y=380, w=1680, d=720, layer=layer, color=fixture))
    add("furniture_cluster", "bathtub_inner", _rect(driver, base=base_point, x=980, y=460, w=1520, d=560, layer=layer, color=accent))
    add("furniture_cluster", "bathtub_head", _arc(driver, base=base_point, center=(1740, 780), radius=320, start_angle=90, end_angle=180, layer=layer, color=fixture))
    add("furniture_cluster", "bathtub_drain", _circle(driver, base=base_point, center=(1200, 520), radius=45, layer=layer, color=accent))

    add(
        "furniture_cluster",
        "shower_enclosure",
        _polyline(
            driver,
            base=base_point,
            points=[(2680, 380), (3300, 380), (3300, 1280), (2680, 1280)],
            closed=True,
            layer=layer,
            color=accent,
        ),
    )
    add("furniture_cluster", "shower_head", _circle(driver, base=base_point, center=(2990, 1180), radius=90, layer=layer, color=fixture))
    add("furniture_cluster", "shower_drain", _circle(driver, base=base_point, center=(2990, 480), radius=55, layer=layer, color=accent))
    for index, y in enumerate((520, 720, 920), start=1):
        add(
            "furniture_cluster",
            f"shower_glass_{index}",
            _line(driver, base=base_point, start=(2720, y), end=(3260, y), layer=layer, color=wall),
        )

    for label, start, end, text_position in (
        ("dimension_width", (0, 0), (w, 0), (w / 2, -420)),
        ("dimension_depth", (w, 0), (w, d), (w + 380, d / 2)),
        ("dimension_door", (150, 0), (150, 950), (-280, 475)),
    ):
        add("dimension_chain", label, _dimension(driver, base=base_point, start=start, end=end, text_position=text_position, layer=layer, color=annotation))

    for index, (text, position, height) in enumerate(
        (
            ("VCAD-04 BATH", (280, 2180), 150),
            ("WC", (620, 1920), 120),
            ("LAVATORY", (2760, 1920), 110),
            ("BATHTUB", (1180, 1120), 110),
            ("SHOWER", (2760, 1120), 110),
            ("1:50", (280, 520), 100),
            ("N", (3180, 2180), 130),
            ("WET ZONE", (1180, 320), 95),
        ),
        start=1,
    ):
        add("room_tags", f"text_{index}", _text(driver, base=base_point, text=text, position=position, height=height, layer=layer, color=annotation))

    add("room_tags", "north_stem", _line(driver, base=base_point, start=(3280, 2000), end=(3280, 2140), layer=layer, color=annotation))
    add("room_tags", "north_left", _line(driver, base=base_point, start=(3280, 2140), end=(3200, 2060), layer=layer, color=annotation))
    add("room_tags", "north_right", _line(driver, base=base_point, start=(3280, 2140), end=(3360, 2060), layer=layer, color=annotation))
    add("room_tags", "legend_frame", _rect(driver, base=base_point, x=240, y=280, w=1200, d=520, layer=layer, color=annotation))
    for index, start_y in enumerate(range(1320, 2100, 180), start=1):
        add(
            "furniture_cluster",
            f"floor_tile_{index}",
            _line(driver, base=base_point, start=(1680, start_y), end=(2520, start_y + 120), layer=layer, color=accent),
        )
    for index, x in enumerate(range(1680, 2520, 200), start=1):
        add(
            "furniture_cluster",
            f"floor_tile_v_{index}",
            _line(driver, base=base_point, start=(x, 1320), end=(x + 80, 2100), layer=layer, color=accent),
        )
    for index, y in enumerate((1480, 1620, 1760, 1900, 2040), start=1):
        add(
            "furniture_cluster",
            f"wet_zone_marker_{index}",
            _line(driver, base=base_point, start=(1080, y), end=(1560, y), layer=layer, color=wall),
        )

    return handles, draw_log, visual_intent


def _draw_kitchen_plan(driver: Any, *, base_point: list[float], layer: str) -> tuple[list[str], list[dict[str, Any]], dict[str, Any]]:
    handles: list[str] = []
    draw_log: list[dict[str, Any]] = []

    def add(visual_group: str, label: str, value: object) -> None:
        group_handles = _collect_handles(value)
        handles.extend(group_handles)
        draw_log.append({"visual_group": visual_group, "group": label, "handles": group_handles})

    visual_intent = {
        "version": "0.1",
        "intent": "visual_kitchen_plan_smoke",
        "base_point": base_point,
        "layer": layer,
        "scene": "residential_kitchen_plan",
        "requirements": list(KITCHEN_PLAN_REQUIRED_GROUPS),
    }
    wall, cabinet, annotation, accent = "cyan", "yellow", "white", "green"
    w, d = 4800.0, 3600.0

    outer = [
        ((0, 0), (w, 0)),
        ((w, 0), (w, d)),
        ((w, d), (0, d)),
        ((0, d), (0, 0)),
        ((180, 180), (w - 180, 180)),
        ((w - 180, 180), (w - 180, d - 180)),
        ((w - 180, d - 180), (180, d - 180)),
        ((180, d - 180), (180, 180)),
    ]
    for index, (start, end) in enumerate(outer, start=1):
        add("segmented_double_wall", f"wall_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    add("door_leaf_and_swing", "entry_leaf", _line(driver, base=base_point, start=(2200, 180), end=(2200, 1180), layer=layer, color=accent))
    add("door_leaf_and_swing", "entry_swing", _arc(driver, base=base_point, center=(2200, 180), radius=1000, start_angle=0, end_angle=90, layer=layer, color=accent))
    add("door_leaf_and_swing", "entry_threshold", _line(driver, base=base_point, start=(2200, 90), end=(3200, 90), layer=layer, color=accent))

    for index, (start, end) in enumerate(
        (((600, d), (1800, d)), ((600, d - 180), (1800, d - 180)), ((1200, d - 180), (1200, d))),
        start=1,
    ):
        add("window_symbol", f"window_{index}", _line(driver, base=base_point, start=start, end=end, layer=layer, color=wall))

    add(
        "furniture_cluster",
        "l_counter",
        _polyline(
            driver,
            base=base_point,
            points=[(320, 320), (4200, 320), (4200, 920), (320, 920)],
            closed=True,
            layer=layer,
            color=cabinet,
        ),
    )
    add("furniture_cluster", "wall_cabinet_run", _rect(driver, base=base_point, x=320, y=2480, w=3880, d=420, layer=layer, color=cabinet))
    for index, x in enumerate(range(520, 4000, 480), start=1):
        add(
            "furniture_cluster",
            f"wall_cabinet_door_{index}",
            _line(driver, base=base_point, start=(x, 2520), end=(x, 2860), layer=layer, color=cabinet),
        )

    add("furniture_cluster", "sink_basin", _circle(driver, base=base_point, center=(1680, 620), radius=200, layer=layer, color=accent))
    add("furniture_cluster", "sink_faucet", _line(driver, base=base_point, start=(1680, 820), end=(1680, 980), layer=layer, color=accent))
    add("furniture_cluster", "dishwasher", _rect(driver, base=base_point, x=2280, y=360, w=620, d=560, layer=layer, color=cabinet))
    for index, (cx, cy) in enumerate(((3680, 620), (3880, 620), (4080, 620)), start=1):
        add("furniture_cluster", f"burner_{index}", _circle(driver, base=base_point, center=(cx, cy), radius=110, layer=layer, color=accent))
        add(
            "furniture_cluster",
            f"burner_ring_{index}",
            _circle(driver, base=base_point, center=(cx, cy), radius=70, layer=layer, color=cabinet),
        )

    add("furniture_cluster", "fridge", _rect(driver, base=base_point, x=320, y=1080, w=720, d=1180, layer=layer, color=cabinet))
    add("furniture_cluster", "fridge_handle", _line(driver, base=base_point, start=(920, 1480), end=(920, 1880), layer=layer, color=accent))
    add("furniture_cluster", "island", _rect(driver, base=base_point, x=1880, y=1480, w=1400, d=820, layer=layer, color=cabinet))
    add("furniture_cluster", "island_sink", _circle(driver, base=base_point, center=(2580, 1880), radius=130, layer=layer, color=accent))

    add(
        "furniture_cluster",
        "dining_nook",
        _polyline(
            driver,
            base=base_point,
            points=[(320, 2480), (1480, 2480), (1480, 3200), (320, 3200)],
            closed=True,
            layer=layer,
            color=accent,
        ),
    )
    table_center = (900, 2840)
    add("furniture_cluster", "dining_table", _rect(driver, base=base_point, x=620, y=2640, w=560, d=400, layer=layer, color=cabinet))
    for index, offset in enumerate(((-280, 0), (280, 0), (0, -280), (0, 280)), start=1):
        cx, cy = table_center[0] + offset[0], table_center[1] + offset[1]
        add("furniture_cluster", f"chair_{index}", _circle(driver, base=base_point, center=(cx, cy), radius=120, layer=layer, color=cabinet))

    for label, start, end, text_position in (
        ("dimension_width", (0, 0), (w, 0), (w / 2, -480)),
        ("dimension_depth", (w, 0), (w, d), (w + 420, d / 2)),
        ("dimension_island", (1880, 1480), (3280, 1480), (2580, 1240)),
    ):
        add("dimension_chain", label, _dimension(driver, base=base_point, start=start, end=end, text_position=text_position, layer=layer, color=annotation))

    for index, (text, position, height) in enumerate(
        (
            ("VCAD-04 KITCHEN", (360, 3320), 160),
            ("L-COUNTER", (2100, 1120), 120),
            ("SINK", (1520, 920), 110),
            ("RANGE", (3880, 920), 110),
            ("FRIDGE", (420, 1680), 110),
            ("ISLAND", (2280, 2280), 110),
            ("1:50", (360, 680), 100),
            ("N", (4300, 3280), 130),
        ),
        start=1,
    ):
        add("room_tags", f"text_{index}", _text(driver, base=base_point, text=text, position=position, height=height, layer=layer, color=annotation))

    add("room_tags", "north_stem", _line(driver, base=base_point, start=(4400, 3080), end=(4400, 3280), layer=layer, color=annotation))
    add("room_tags", "north_left", _line(driver, base=base_point, start=(4400, 3280), end=(4320, 3180), layer=layer, color=annotation))
    add("room_tags", "north_right", _line(driver, base=base_point, start=(4400, 3280), end=(4480, 3180), layer=layer, color=annotation))
    add("room_tags", "legend_frame", _rect(driver, base=base_point, x=360, y=360, w=1400, d=640, layer=layer, color=annotation))
    for index, start_y in enumerate(range(1080, 2200, 220), start=1):
        add(
            "furniture_cluster",
            f"floor_grid_{index}",
            _line(driver, base=base_point, start=(1520, start_y), end=(4200, start_y + 160), layer=layer, color=accent),
        )
    for index, x in enumerate(range(1520, 4200, 260), start=1):
        add(
            "furniture_cluster",
            f"floor_grid_v_{index}",
            _line(driver, base=base_point, start=(x, 1080), end=(x + 100, 2360), layer=layer, color=accent),
        )

    return handles, draw_log, visual_intent
