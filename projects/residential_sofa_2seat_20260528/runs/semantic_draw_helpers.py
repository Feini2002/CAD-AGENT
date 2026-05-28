"""Case-local semantic draw — round10 open assembly (no closed outer shell)."""

from __future__ import annotations

import math
from typing import Any, Literal

from core.cad_io.autocad_com import PREVIEW_LAYER, AutoCADComDriver

# Reference block probe: seat front protrudes ~30mm past arm front (plan Y+).
SEAT_FRONT_PROTRUSION_MM = 30.0


def _arc(
    driver: AutoCADComDriver,
    *,
    cx: float,
    cy: float,
    r: float,
    start_deg: float,
    end_deg: float,
    created: list[str],
) -> None:
    obj = driver.draw_arc(
        center=[cx, cy, 0],
        radius=r,
        start_angle=start_deg,
        end_angle=end_deg,
        layer=PREVIEW_LAYER,
        color="cyan",
    )
    created.append(obj["handle"])


def _line(
    driver: AutoCADComDriver,
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    created: list[str],
) -> None:
    obj = driver.draw_line(
        start_point=[x1, y1, 0],
        end_point=[x2, y2, 0],
        layer=PREVIEW_LAYER,
        color="cyan",
    )
    created.append(obj["handle"])


def _front_bow_arc(
    driver: AutoCADComDriver,
    *,
    xl: float,
    xr: float,
    yf: float,
    bow: float,
    created: list[str],
) -> None:
    cx = (xl + xr) / 2.0
    chord = xr - xl
    if chord < 20:
        return
    sag = max(10.0, min(bow, chord * 0.055))
    radius = (chord * chord) / (8.0 * sag) + sag / 2.0
    cy = yf - radius + sag
    sa = math.degrees(math.atan2(yf - cy, xl - cx))
    ea = math.degrees(math.atan2(yf - cy, xr - cx))
    if (ea - sa) % 360.0 > 180.0:
        sa, ea = ea, sa
    _arc(driver, cx=cx, cy=cy, r=radius, start_deg=sa, end_deg=ea, created=created)


def _arm_block(
    driver: AutoCADComDriver,
    *,
    x_outer: float,
    x_inner: float,
    y_front: float,
    y_top: float,
    y_split: float,
    r: float,
    side: Literal["left", "right"],
    created: list[str],
) -> None:
    """Armrest strip — open at front; does not wrap seat protrusion."""
    arm_w = abs(x_inner - x_outer)
    rr = min(r, arm_w * 0.45, (y_top - y_front) * 0.2, 28.0)
    rr = max(8.0, rr)
    if side == "left":
        _line(driver, x_outer, y_front + rr, x_outer, y_top, created)
        _line(driver, x_inner, y_front, x_inner, y_split, created)
        _arc(driver, cx=x_outer + rr, cy=y_front + rr, r=rr, start_deg=180, end_deg=270, created=created)
        _line(driver, x_outer + rr, y_front, x_inner, y_front, created)
    else:
        _line(driver, x_outer, y_front + rr, x_outer, y_top, created)
        _line(driver, x_inner, y_front, x_inner, y_split, created)
        _arc(driver, cx=x_outer - rr, cy=y_front + rr, r=rr, start_deg=270, end_deg=360, created=created)
        _line(driver, x_inner, y_front, x_outer - rr, y_front, created)


def _seat_cushion_protruding(
    driver: AutoCADComDriver,
    *,
    x0: float,
    x1: float,
    y_bot: float,
    y_top: float,
    r: float,
    created: list[str],
) -> None:
    """Seat cushion — closed rounded rect; front at y_bot protrudes past arm front."""
    w = x1 - x0
    h = y_top - y_bot
    if w < 80 or h < 50:
        return
    cr = min(r, 30.0, w * 0.14, h * 0.24)
    yf = y_bot + cr
    cy_back = y_top - cr

    _line(driver, x0 + cr, y_top, x1 - cr, y_top, created)
    _line(driver, x0, yf, x0, cy_back, created)
    _line(driver, x1, yf, x1, cy_back, created)
    _arc(driver, cx=x0 + cr, cy=cy_back, r=cr, start_deg=90, end_deg=180, created=created)
    _arc(driver, cx=x1 - cr, cy=cy_back, r=cr, start_deg=0, end_deg=90, created=created)
    _line(driver, x0 + cr, y_bot, x1 - cr, y_bot, created)
    _arc(driver, cx=x0 + cr, cy=yf, r=cr, start_deg=180, end_deg=270, created=created)
    _arc(driver, cx=x1 - cr, cy=yf, r=cr, start_deg=270, end_deg=360, created=created)


def _back_cushion_pillow(
    driver: AutoCADComDriver,
    *,
    x0: float,
    x1: float,
    y_bot: float,
    y_top: float,
    r: float,
    created: list[str],
) -> None:
    """Back cushion — slightly elliptical pillow + one stitch line."""
    w, h = x1 - x0, y_top - y_bot
    if w < 60 or h < 40:
        return
    rx = min(r, 32.0, w * 0.24)
    ry = min(r * 0.85, 26.0, h * 0.32)
    cx_l, cx_r = x0 + rx, x1 - rx
    cy_b, cy_t = y_bot + ry, y_top - ry

    _line(driver, cx_l, cy_t, cx_r, cy_t, created)
    _line(driver, cx_l, cy_b, cx_r, cy_b, created)
    _arc(driver, cx=cx_l, cy=cy_b, r=rx, start_deg=180, end_deg=270, created=created)
    _arc(driver, cx=cx_r, cy=cy_b, r=rx, start_deg=270, end_deg=360, created=created)
    _arc(driver, cx=cx_l, cy=cy_t, r=rx, start_deg=90, end_deg=180, created=created)
    _arc(driver, cx=cx_r, cy=cy_t, r=rx, start_deg=0, end_deg=90, created=created)
    stitch_y = cy_b + (cy_t - cy_b) * 0.45
    _line(driver, cx_l + 14, stitch_y, cx_r - 14, stitch_y, created)


def _back_cushion_and_rest(
    driver: AutoCADComDriver,
    *,
    x0: float,
    x1: float,
    y_bot: float,
    y_top: float,
    r: float,
    created: list[str],
) -> None:
    """Back cushion (靠垫) + local back band — separate from seat, between arms."""
    w, h = x1 - x0, y_top - y_bot
    if w < 60 or h < 40:
        return
    cr = min(r * 0.9, 28.0, w * 0.2, h * 0.35)
    pad_top = cr * 0.35
    cx0, cx1 = x0 + cr * 0.4, x1 - cr * 0.4
    cy_bot, cy_top = y_bot + cr * 0.5, y_top - pad_top
    cy_back = cy_top - cr

    _line(driver, cx0 + cr, cy_top, cx1 - cr, cy_top, created)
    _line(driver, cx0, cy_bot + cr, cx0, cy_back, created)
    _line(driver, cx1, cy_bot + cr, cx1, cy_back, created)
    _arc(driver, cx=cx0 + cr, cy=cy_back, r=cr, start_deg=90, end_deg=180, created=created)
    _arc(driver, cx=cx1 - cr, cy=cy_back, r=cr, start_deg=0, end_deg=90, created=created)
    _line(driver, cx0 + cr, cy_bot, cx1 - cr, cy_bot, created)
    _arc(driver, cx=cx0 + cr, cy=cy_bot + cr, r=cr, start_deg=180, end_deg=270, created=created)
    _arc(driver, cx=cx1 - cr, cy=cy_bot + cr, r=cr, start_deg=270, end_deg=360, created=created)
    stitch_y = cy_bot + (cy_back - cy_bot) * 0.42
    _line(driver, cx0 + 16, stitch_y, cx1 - 16, stitch_y, created)


def draw_two_seater_semantic(
    driver: AutoCADComDriver,
    *,
    px0: float,
    py0: float,
    w2: float,
    h: float,
    ref_style: dict[str, Any],
) -> list[str]:
    px1 = px0 + w2
    r = float(ref_style["fillet_r_mm"])
    arm = float(ref_style["arm_width_mm"])
    y_split = py0 + h * float(ref_style["seat_split_ratio"])
    y_arm_front = py0 + SEAT_FRONT_PROTRUSION_MM
    y_back_top = py0 + h
    mid_x = px0 + w2 / 2.0
    seat_w = (w2 - 2 * arm) / 2.0
    pad = 8.0
    created: list[str] = []

    # Backrest top rail only — NOT a closed outer tub.
    _line(driver, px0 + r, y_back_top, px1 - r, y_back_top, created)
    _line(driver, px0 + arm, y_split, px1 - arm, y_split, created)

    _arm_block(
        driver,
        x_outer=px0,
        x_inner=px0 + arm,
        y_front=y_arm_front,
        y_top=y_back_top - r,
        y_split=y_split,
        r=r,
        side="left",
        created=created,
    )
    _arm_block(
        driver,
        x_outer=px1,
        x_inner=px1 - arm,
        y_front=y_arm_front,
        y_top=y_back_top - r,
        y_split=y_split,
        r=r,
        side="right",
        created=created,
    )

    _line(driver, mid_x, y_arm_front, mid_x, y_split, created)
    # 禁止 px0+arm 到 px1-arm 的前横连线 — 会把开放总成又封成盒

    seat_top = y_split - pad
    back_bot = y_split + pad * 0.3
    back_top = y_back_top - pad * 0.4

    for side in (0, 1):
        sx0 = px0 + arm + side * seat_w + pad
        sx1 = sx0 + seat_w - 2 * pad
        _seat_cushion_protruding(
            driver,
            x0=sx0,
            x1=sx1,
            y_bot=py0,
            y_top=seat_top,
            r=r,
            created=created,
        )
        _back_cushion_pillow(
            driver,
            x0=sx0,
            x1=sx1,
            y_bot=back_bot,
            y_top=back_top,
            r=r,
            created=created,
        )

    return created
