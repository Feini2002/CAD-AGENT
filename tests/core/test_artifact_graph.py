from __future__ import annotations

import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from core.workflows.artifact_graph import ArtifactGraph, build_artifact_graph_from_workflow


class ArtifactGraphTests(unittest.TestCase):
    def test_workflow_artifacts_have_dependency_order(self) -> None:
        graph = build_artifact_graph_from_workflow(PROJECT_ROOT / "examples/workflows/minimal_cabinet_loop.json")

        order = graph.dependency_order()

        self.assertLess(order.index("design_brief"), order.index("project_model"))
        self.assertLess(order.index("drawing_model"), order.index("project_model"))
        self.assertLess(order.index("project_model"), order.index("layout_proposal"))
        self.assertLess(order.index("layout_proposal"), order.index("design_proposal"))
        self.assertLess(order.index("design_proposal"), order.index("cad_plan"))
        self.assertEqual(set(order), set(graph.nodes))

    def test_workflow_artifact_paths_are_resolved_against_project_root(self) -> None:
        graph = build_artifact_graph_from_workflow(PROJECT_ROOT / "examples/workflows/minimal_cabinet_loop.json")

        path_checks = graph.validate_paths(PROJECT_ROOT)

        self.assertEqual(path_checks["status"], "ok")
        self.assertEqual(path_checks["missing"], [])

    def test_cycle_is_reported_as_invalid_dependency_graph(self) -> None:
        graph = ArtifactGraph()
        graph.add_artifact("brief", model_type="design_brief", depends_on=["plan"])
        graph.add_artifact("plan", model_type="cad_plan", depends_on=["brief"])

        with self.assertRaises(ValueError):
            graph.dependency_order()


if __name__ == "__main__":
    unittest.main()
