from __future__ import annotations

import json
from pathlib import Path
import unittest

from core.schemas.validator import validate_value
from core.verification.fake_cad_driver import FakeCadDriver
from tests.helpers import temporary_artifact_dir


def _sample_style_candidates() -> dict[str, object]:
    return {
        "schemaVersion": "style-candidates/v1",
        "caseId": "unit-style-candidates",
        "scenario": {
            "domain": "residential",
            "drawingType": "dimension_style_showcase",
            "expressionPurpose": "比较新场景的 A/B/C 尺寸表达。",
        },
        "styleIntent": "小户型玄关鞋柜尺寸标注新场景，不复刻旧十个尺寸样式。",
        "generationMethod": "parameterized_new_scene",
        "selection": {
            "selectedCandidateId": "",
            "needsUserChoice": True,
            "autoSelectPolicy": "ask_user",
        },
        "candidates": [
            {
                "candidateId": "A",
                "label": "A 紧凑",
                "summary": "紧凑尺寸表达，适合小空间快速扫读。",
                "parameters": {
                    "objectType": "shoe_cabinet",
                    "objectName": "玄关鞋柜 A",
                    "width": 1200,
                    "depth": 350,
                    "basePoint": [0, 0, 0],
                    "styleToken": "furniture.visible.medium",
                    "includeLabel": True,
                    "includeDimensions": True,
                    "textHierarchy": "compact",
                    "lineSpacing": 90,
                    "density": "high",
                    "layerStrategy": "preview_semantic_furniture",
                },
                "rationale": "用更短的标注距离控制信息密度。",
                "tradeoffs": ["信息密度较高", "用户需要确认是否太挤"],
            },
            {
                "candidateId": "B",
                "label": "B 均衡",
                "summary": "均衡尺寸表达，默认推荐。",
                "parameters": {
                    "objectType": "shoe_cabinet",
                    "objectName": "玄关鞋柜 B",
                    "width": 1400,
                    "depth": 380,
                    "basePoint": [2200, 0, 0],
                    "styleToken": "furniture.visible.medium",
                    "includeLabel": True,
                    "includeDimensions": True,
                    "textHierarchy": "balanced",
                    "lineSpacing": 140,
                    "density": "medium",
                    "layerStrategy": "preview_semantic_furniture",
                },
                "rationale": "尺寸、文字和对象比例更适合默认交付。",
                "tradeoffs": ["占图面略多", "可读性更稳"],
            },
            {
                "candidateId": "C",
                "label": "C 展示",
                "summary": "展示型尺寸表达，保留更宽的阅读留白。",
                "parameters": {
                    "objectType": "shoe_cabinet",
                    "objectName": "玄关鞋柜 C",
                    "width": 1600,
                    "depth": 420,
                    "basePoint": [4700, 0, 0],
                    "styleToken": "furniture.visible.medium",
                    "includeLabel": True,
                    "includeDimensions": True,
                    "textHierarchy": "presentation",
                    "lineSpacing": 190,
                    "density": "low",
                    "layerStrategy": "preview_semantic_furniture",
                },
                "rationale": "更适合请用户目视挑选和讨论。",
                "tradeoffs": ["图面占用最多", "视觉更舒展"],
            },
        ],
        "evidenceBoundary": {
            "checked": ["schema", "candidate_count", "preview_plan_generation"],
            "notChecked": ["user_choice", "real_cad_readback"],
        },
    }


class StyleCandidatesExecutionTests(unittest.TestCase):
    def test_style_candidates_schema_accepts_three_parameterized_options(self) -> None:
        schema = json.loads(Path("core/schemas/style_candidates.schema.json").read_text(encoding="utf-8"))
        errors = validate_value(_sample_style_candidates(), schema)

        self.assertEqual(errors, [])

    def test_executor_consumes_style_candidates_and_writes_candidate_plans(self) -> None:
        from core.execution.style_candidate_execute import execute_style_candidates_file

        with temporary_artifact_dir("style_candidates") as root:
            candidates_path = root / "style_candidates.json"
            candidates_path.write_text(json.dumps(_sample_style_candidates(), ensure_ascii=False), encoding="utf-8")

            report = execute_style_candidates_file(
                candidates_path,
                driver=FakeCadDriver(),
                output_dir=root / "executed",
            )

            self.assertEqual(report["status"], "executed")
            self.assertEqual(report["candidateCount"], 3)
            self.assertEqual(report["candidateIds"], ["A", "B", "C"])
            self.assertTrue(report["needsUserChoice"])
            self.assertFalse(report["savedCurrentDwg"])
            self.assertEqual(report["targetLayer"], "CODEX_PREVIEW")
            self.assertEqual(len(report["candidateSummaries"]), 3)
            for row in report["candidateSummaries"]:
                self.assertEqual(row["executionSummary"]["status"], "executed")
                self.assertEqual(row["executionSummary"]["layer"], "CODEX_PREVIEW")
                self.assertTrue(row["executionSummary"]["created_handles"])
                self.assertIn("style_evidence", row["executionSummary"])
                self.assertTrue((root / "executed" / f"{row['candidateId']}_cad_plan.json").is_file())


if __name__ == "__main__":
    unittest.main()
