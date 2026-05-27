"""P3 multi-scene productization parent contract (office + restaurant rollup)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.agents.office_p3_wave import (
    OFFICE_P3_ACCEPTANCE_DOC,
    OFFICE_P3_WAVE_PACKAGE_ID,
    assert_office_p3_wave_contract,
    office_p3_wave_status_summary,
)
from core.agents.restaurant_p3_wave import (
    RESTAURANT_P3_ACCEPTANCE_DOC,
    RESTAURANT_P3_WAVE_PACKAGE_ID,
    assert_restaurant_p3_wave_contract,
    restaurant_p3_wave_status_summary,
)

MULTI_SCENE_P3_PACKAGE_ID = "REST-PROD-04-MULTI-SCENE-P3-ROLLUP"
MULTI_SCENE_P3_ACCEPTANCE_DOC = "docs/verification/rest_prod_04_multi_scene_p3_rollup_acceptance.md"
MULTI_SCENE_P3_CHILD_PACKAGE_IDS = (
    OFFICE_P3_WAVE_PACKAGE_ID,
    RESTAURANT_P3_WAVE_PACKAGE_ID,
)
MULTI_SCENE_P3_CHILD_ACCEPTANCE_DOCS = (
    OFFICE_P3_ACCEPTANCE_DOC,
    RESTAURANT_P3_ACCEPTANCE_DOC,
)


def assert_multi_scene_p3_wave_contract(*, project_root: Path) -> None:
    """Raise when the multi-scene P3 rollup artifacts or child contracts are missing."""

    root = project_root.resolve()

    if not (root / MULTI_SCENE_P3_ACCEPTANCE_DOC).is_file():
        raise AssertionError(f"missing REST-PROD-04 acceptance doc: {MULTI_SCENE_P3_ACCEPTANCE_DOC}")

    for rel in MULTI_SCENE_P3_CHILD_ACCEPTANCE_DOCS:
        if not (root / rel).is_file():
            raise AssertionError(f"missing child P3 acceptance doc: {rel}")

    assert_office_p3_wave_contract(project_root=root)
    assert_restaurant_p3_wave_contract(project_root=root)

    summary = multi_scene_p3_wave_status_summary(project_root=root)
    if summary["readback_geometry_verified_count"] != 0:
        raise AssertionError("multi-scene P3 no-CAD rollup must not report geometry_verified")


def multi_scene_p3_wave_status_summary(*, project_root: Path) -> dict[str, Any]:
    root = project_root.resolve()
    office = office_p3_wave_status_summary(project_root=root)
    restaurant = restaurant_p3_wave_status_summary(project_root=root)
    scene_summaries = {
        "office": office,
        "restaurant": restaurant,
    }
    return {
        "package_id": MULTI_SCENE_P3_PACKAGE_ID,
        "package_ids": list(MULTI_SCENE_P3_CHILD_PACKAGE_IDS),
        "acceptance_doc": MULTI_SCENE_P3_ACCEPTANCE_DOC,
        "child_acceptance_docs": list(MULTI_SCENE_P3_CHILD_ACCEPTANCE_DOCS),
        "docs_present": all(
            (root / rel).is_file()
            for rel in (*MULTI_SCENE_P3_CHILD_ACCEPTANCE_DOCS, MULTI_SCENE_P3_ACCEPTANCE_DOC)
        ),
        "scene_count": len(scene_summaries),
        "child_package_count": sum(int(item.get("child_package_count", 0)) + 1 for item in scene_summaries.values()),
        "alpha_case_count": sum(int(item.get("alpha_case_count", 0)) for item in scene_summaries.values()),
        "beta_case_count": sum(int(item.get("beta_case_count", 0)) for item in scene_summaries.values()),
        "readback_geometry_verified_count": 0,
        "scene_summaries": scene_summaries,
    }
