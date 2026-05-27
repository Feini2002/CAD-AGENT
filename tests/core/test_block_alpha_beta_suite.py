from __future__ import annotations

import json
import math
import shutil
import unittest

from core.plan_engine.validate_plan import validate_plan
from core.block_engine.block_library import load_block_library, normalize_block
from core.verification.block_alpha_beta_suite import (
    default_suite_path,
    load_block_alpha_beta_suite,
    materialize_block_alpha_plan,
    run_block_alpha_beta_suite,
)
from tests.helpers import PROJECT_ROOT, artifact_path


class FakeBlockAlphaCadDriver:
    def __init__(self) -> None:
        self.entities: dict[str, dict[str, object]] = {}
        self.next_id = 1

    def insert_block_alpha(
        self,
        *,
        block_id: str = "controlled-test-block-001",
        block_name: str,
        base_point: list[float | int],
        rotation: float | int = 0,
        scale: list[float | int] | None = None,
        layer: str,
        **_: object,
    ) -> dict[str, str]:
        handle = f"BR{self.next_id}"
        self.next_id += 1
        scale_values = [float(value) for value in (scale or [1, 1, 1])]
        width = 900.0 * scale_values[0]
        depth = 450.0 * scale_values[1]
        for block in load_block_library().get("blocks", []):
            if isinstance(block, dict) and block.get("block_id") == block_id:
                footprint = normalize_block(block).get("footprint_2d", {})
                width = float(footprint["width"]) * scale_values[0]
                depth = float(footprint["depth"]) * scale_values[1]
                break
        theta = math.radians(float(rotation))
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)
        xs: list[float] = []
        ys: list[float] = []
        for x, y in ((0.0, 0.0), (width, 0.0), (width, depth), (0.0, depth)):
            xs.append(float(base_point[0]) + x * cos_t - y * sin_t)
            ys.append(float(base_point[1]) + x * sin_t + y * cos_t)
        entity = {
            "handle": handle,
            "type": "block_reference",
            "block_name": block_name,
            "insertion_point": [float(value) for value in base_point[:3]],
            "rotation": float(rotation),
            "scale": scale_values,
            "layer": layer,
            "bbox": {
                "min": [min(xs), min(ys)],
                "max": [max(xs), max(ys)],
            },
        }
        self.entities[handle] = entity
        return {"handle": handle}

    def snapshot_handles(self, *, handles: list[str], layer: str | None = None) -> list[dict[str, object]]:
        entities = [self.entities[handle] for handle in handles if handle in self.entities]
        if layer:
            entities = [entity for entity in entities if entity.get("layer") == layer]
        return entities


class BlockAlphaBetaSuiteTests(unittest.TestCase):
    def test_beta_cad_block_01_suite_has_eight_transform_cases(self) -> None:
        suite = load_block_alpha_beta_suite(default_suite_path(PROJECT_ROOT))

        self.assertEqual(suite["suite_id"], "block-alpha-beta-01")
        self.assertEqual(len(suite["cases"]), 8)
        case_ids = {case["case_id"] for case in suite["cases"]}
        self.assertIn("beta_anchor_mid_room", case_ids)
        self.assertIn("beta_rotation_45", case_ids)
        self.assertIn("beta_scale_half", case_ids)
        self.assertIn("beta_combined_transform", case_ids)

    def test_beta_cad_block_01_rejects_non_uniform_scale(self) -> None:
        case = {
            "case_id": "invalid_scale",
            "placement": {"base_point": [0, 0, 0], "rotation": 0, "scale": [1, 2, 1]},
        }
        plan = materialize_block_alpha_plan(case)
        errors = validate_plan(plan)
        self.assertTrue(any("uniform scale" in error for error in errors))

    def test_beta_cad_block_01_suite_validate_and_dry_run_pass(self) -> None:
        result = run_block_alpha_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=artifact_path("block_alpha_beta", "beta_cad_block_01"),
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 8, "passed": 8, "failed": 0})
        summary = result["evidence_summary"]
        self.assertEqual(summary["dry_run_valid_count"], 8)
        self.assertEqual(summary.get("geometry_verified_count", 0), 0)
        self.assertTrue(summary.get("non_cad_only", True))

        combined = run_block_alpha_beta_suite(default_suite_path(PROJECT_ROOT))
        rotations = {
            case["actual"]["rotation"]
            for case in combined["cases"]
            if case["case_id"].startswith("beta_rotation")
        }
        self.assertEqual(rotations, {45, 90})

        half = next(case for case in combined["cases"] if case["case_id"] == "beta_scale_half")
        self.assertEqual(half["actual"]["scale"], [0.5, 0.5, 0.5])
        self.assertLess(half["actual"]["bbox"]["max"][0], 3000)

    def test_beta_cad_block_01_summary_written_to_artifacts(self) -> None:
        output_root = artifact_path("block_alpha_beta", "beta_cad_block_01_write")
        run_block_alpha_beta_suite(default_suite_path(PROJECT_ROOT), output_root=output_root)

        summary_path = output_root / "block_alpha_beta_summary.json"
        self.assertTrue(summary_path.is_file())
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        self.assertEqual(summary["status"], "pass")
        self.assertTrue((output_root / "beta_rotation_90" / "dry_run_report.json").is_file())

    def test_beta_cad_block_01_connect_cad_verifies_created_handle_readback(self) -> None:
        output_root = artifact_path("block_alpha_beta", "beta_cad_block_01_cad")
        result = run_block_alpha_beta_suite(
            default_suite_path(PROJECT_ROOT),
            output_root=output_root,
            driver_factory=FakeBlockAlphaCadDriver,
        )

        self.assertEqual(result["status"], "pass", result)
        evidence = result["evidence_summary"]
        self.assertFalse(evidence["non_cad_only"])
        self.assertEqual(evidence["geometry_verified_count"], 8)
        self.assertEqual(evidence["readback_geometry_verified_count"], 8)
        self.assertEqual(evidence["evidence_state"], "readback_geometry_verified")
        first = result["cases"][0]
        self.assertEqual(first["block_alpha_report"]["status"], "geometry_verified")
        self.assertEqual(len(first["actual"]["created_handles"]), 1)
        self.assertTrue((output_root / first["case_id"] / "block_alpha_report.json").is_file())

    def test_vproof_41_suite_covers_first_and_second_controlled_blocks(self) -> None:
        suite_path = PROJECT_ROOT / "examples/plans/block_cad_matrix_vproof_41.json"
        result = run_block_alpha_beta_suite(
            suite_path,
            output_root=artifact_path("block_alpha_beta", "vproof_41"),
            driver_factory=FakeBlockAlphaCadDriver,
        )

        self.assertEqual(result["status"], "pass", result)
        self.assertEqual(result["summary"], {"total": 2, "passed": 2, "failed": 0})
        self.assertEqual(result["evidence_summary"]["geometry_verified_count"], 2)
        names = {
            case["block_alpha_report"]["entity"]["block_name"]
            for case in result["cases"]
        }
        self.assertEqual(names, {"CODEX_TEST_BLOCK_001", "CODEX_TEST_BLOCK_002"})

    def test_beta_suite_rejects_output_root_outside_project_output(self) -> None:
        output_root = PROJECT_ROOT / "tests" / "outside_block_alpha_beta"
        try:
            with self.assertRaisesRegex(ValueError, "output_root"):
                run_block_alpha_beta_suite(default_suite_path(PROJECT_ROOT), output_root=output_root)
        finally:
            if output_root.exists():
                shutil.rmtree(output_root, ignore_errors=True)

    def test_beta_suite_rejects_unsafe_case_id(self) -> None:
        suite_path = artifact_path("block_alpha_beta", "unsafe_suite.json")
        suite_path.write_text(
            json.dumps(
                {
                    "suite_id": "unsafe-block-alpha",
                    "cases": [
                        {
                            "case_id": "../escape",
                            "placement": {"base_point": [0, 0, 0]},
                        }
                    ],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        output_root = artifact_path("block_alpha_beta", "unsafe_suite_out")

        with self.assertRaisesRegex(ValueError, "case_id"):
            run_block_alpha_beta_suite(suite_path, output_root=output_root)


if __name__ == "__main__":
    unittest.main()
