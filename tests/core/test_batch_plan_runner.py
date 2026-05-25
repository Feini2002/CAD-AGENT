from __future__ import annotations

import json
import unittest

from tests.helpers import artifact_path

from core.composition_engine.templates import composition_to_cad_plans, create_composition_spec
from core.execution.batch_plan_runner import execute_plan_batch, translate_plan


class GeometryRecordingDriver:
    def __init__(self) -> None:
        self.entities: dict[str, dict[str, object]] = {}
        self.next_handle = 1

    def _handle(self) -> str:
        handle = f"H{self.next_handle}"
        self.next_handle += 1
        return handle

    def _record(self, entity: dict[str, object]) -> str:
        handle = self._handle()
        self.entities[handle] = {"handle": handle, **entity}
        return handle

    def draw_rectangle(self, **kwargs: object) -> dict[str, list[str]]:
        corner1 = list(kwargs["corner1"])  # type: ignore[arg-type]
        corner2 = list(kwargs["corner2"])  # type: ignore[arg-type]
        layer = str(kwargs["layer"])
        x1, y1, z1 = corner1
        x2, y2, _z2 = corner2
        points = [
            ([x1, y1, z1], [x2, y1, z1]),
            ([x2, y1, z1], [x2, y2, z1]),
            ([x2, y2, z1], [x1, y2, z1]),
            ([x1, y2, z1], [x1, y1, z1]),
        ]
        return {
            "handles": [
                self._record({"type": "line", "layer": layer, "start_point": start, "end_point": end})
                for start, end in points
            ]
        }

    def draw_text(self, **kwargs: object) -> dict[str, str]:
        return {
            "handle": self._record(
                {
                    "type": "text",
                    "layer": str(kwargs["layer"]),
                    "text": str(kwargs["text"]),
                    "position": list(kwargs["position"]),  # type: ignore[arg-type]
                }
            )
        }

    def add_dimension(self, **kwargs: object) -> dict[str, str]:
        return {"handle": self._record({"type": "dimension", "layer": str(kwargs["layer"])})}

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, object]]:
        result = [self.entities[handle] for handle in handles if handle in self.entities]
        if layer:
            result = [entity for entity in result if entity.get("layer") == layer]
        return result


class BatchPlanRunnerTests(unittest.TestCase):
    def test_translate_plan_offsets_absolute_base_point(self) -> None:
        plan = composition_to_cad_plans(create_composition_spec("office_desk_combo"))[0]

        translated = translate_plan(plan, offset=[1000, 2000, 0])

        self.assertEqual(translated["placement"]["base_point"], [1000, 2600, 0])
        self.assertEqual(plan["placement"]["base_point"], [0, 600, 0])

    def test_execute_plan_batch_writes_translated_plans_and_geometry_reports(self) -> None:
        plans = composition_to_cad_plans(create_composition_spec("office_desk_combo"))
        source_dir = artifact_path("batch_plan_runner", "source")
        source_dir.mkdir(parents=True, exist_ok=True)
        plan_paths = []
        for index, plan in enumerate(plans, start=1):
            path = source_dir / f"plan_{index}.json"
            path.write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
            plan_paths.append(path)

        result = execute_plan_batch(
            plan_paths,
            output_dir=artifact_path("batch_plan_runner", "out"),
            driver=GeometryRecordingDriver(),
            offset=[3000, 1000, 0],
        )

        self.assertEqual(result["status"], "geometry_verified", result)
        self.assertEqual(result["summary"]["total"], 3)
        self.assertEqual(result["summary"]["status_counts"], {"geometry_verified": 3})
        self.assertGreater(result["created_handle_count"], 0)
        for item in result["items"]:
            self.assertEqual(item["verification_report"]["status"], "geometry_verified")
            self.assertTrue(item["translated_plan_path"].endswith(".json"))


if __name__ == "__main__":
    unittest.main()
