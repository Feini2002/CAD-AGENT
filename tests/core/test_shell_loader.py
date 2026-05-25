from __future__ import annotations

import json
import unittest


from tests.bootstrap import PROJECT_ROOT

from core.drawing_analysis.shell_loader import ShellLoadError, load_manual_shell
from core.schemas.validator import validate_value
from tests.helpers import artifact_path


def write_payload(name: str, payload: dict[str, object]) -> Path:
    path = artifact_path("shell_loader", name)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_json(path: str) -> dict[str, object]:
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


class ShellLoaderTests(unittest.TestCase):
    def test_load_manual_shell_requires_units_and_boundary(self) -> None:
        path = write_payload(
            "missing_units.json",
            {
                "version": "0.1",
                "shell_id": "shell-missing-units",
                "boundary": {"type": "bbox", "min": [0, 0], "max": [1000, 1000]},
            },
        )

        with self.assertRaisesRegex(ShellLoadError, "units"):
            load_manual_shell(path)

    def test_load_manual_shell_normalizes_sample_blank_shell(self) -> None:
        shell = load_manual_shell(PROJECT_ROOT / "projects/sample_blank_shell/input/shell.manual.json")

        self.assertEqual(shell["shell_id"], "shell-sample-blank-shell")
        self.assertEqual(shell["units"], "mm")
        self.assertEqual(shell["boundary"]["type"], "bbox")
        self.assertEqual(shell["boundary"]["min"], [0, 0])
        self.assertEqual(shell["boundary"]["max"], [9000, 5200])
        self.assertEqual(shell["openings"][0]["opening_id"], "entrance-main")
        self.assertEqual(shell["openings"][0]["width"], 1200)
        self.assertEqual(shell["fixed_obstacles"][0]["obstacle_id"], "column-01")
        self.assertTrue(shell["no_place_zones"])
        self.assertEqual(shell["source"]["type"], "manual_annotation")

        schema = load_json("core/schemas/shell_model.schema.json")
        self.assertEqual(validate_value(shell, schema), [])

    def test_load_manual_shell_keeps_legacy_drawing_style_compatible(self) -> None:
        path = write_payload(
            "legacy_drawing_style_shell.json",
            {
                "version": "0.1",
                "drawing_id": "drawing-legacy-store",
                "units": "mm",
                "spaces": [
                    {
                        "space_id": "sales-floor",
                        "boundary": {"type": "bbox", "min": [0, 0], "max": [6000, 3000]},
                        "entrances": [
                            {
                                "id": "front-door",
                                "type": "entry",
                                "point": [0, 1500],
                                "width": 1200,
                            }
                        ],
                        "avoid_zones": [
                            {
                                "id": "column-a",
                                "bbox": {"min": [2800, 1200], "max": [3200, 1600]},
                            }
                        ],
                    }
                ],
                "uncertainties": ["legacy manual annotation"],
            },
        )

        shell = load_manual_shell(path)

        self.assertEqual(shell["shell_id"], "shell-legacy-store")
        self.assertEqual(shell["openings"][0]["opening_id"], "front-door")
        self.assertEqual(shell["fixed_obstacles"][0]["obstacle_id"], "column-a")
        self.assertEqual(shell["no_place_zones"][0]["zone_id"], "column-a")
        self.assertEqual(shell["uncertainties"], ["legacy manual annotation"])

    def test_load_manual_shell_rejects_opening_without_width(self) -> None:
        path = write_payload(
            "opening_without_width.json",
            {
                "version": "0.1",
                "shell_id": "shell-bad-opening",
                "units": "mm",
                "boundary": {"type": "bbox", "min": [0, 0], "max": [3000, 2000]},
                "openings": [{"opening_id": "entry", "type": "entry", "center": [0, 1000]}],
            },
        )

        with self.assertRaisesRegex(ShellLoadError, "width"):
            load_manual_shell(path)

    def test_load_manual_shell_rejects_no_place_zone_outside_boundary(self) -> None:
        path = write_payload(
            "zone_outside_boundary.json",
            {
                "version": "0.1",
                "shell_id": "shell-bad-zone",
                "units": "mm",
                "boundary": {"type": "bbox", "min": [0, 0], "max": [3000, 2000]},
                "openings": [{"opening_id": "entry", "type": "entry", "center": [0, 1000], "width": 900}],
                "no_place_zones": [
                    {"zone_id": "zone-outside", "bbox": {"min": [2500, 1500], "max": [3500, 2100]}}
                ],
            },
        )

        with self.assertRaisesRegex(ShellLoadError, "outside boundary"):
            load_manual_shell(path)


if __name__ == "__main__":
    unittest.main()
