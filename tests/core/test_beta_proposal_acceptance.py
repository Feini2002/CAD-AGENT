from __future__ import annotations

import unittest

from core.proposal_engine.proposal_acceptance import run_beta_proposal_acceptance_rollup
from tests.bootstrap import PROJECT_ROOT
from tests.helpers import artifact_path


class BetaProposalAcceptanceTests(unittest.TestCase):
    def test_beta_proposal_parent_rollup_passes(self) -> None:
        rollup = run_beta_proposal_acceptance_rollup(
            project_root=PROJECT_ROOT,
            output_root=artifact_path("benchmarks", "beta_proposal_acceptance"),
        )
        self.assertEqual(rollup["status"], "pass", rollup)
        self.assertEqual(rollup["geometry_verified_count"], 0)
        self.assertTrue(rollup["non_cad_only"])


if __name__ == "__main__":
    unittest.main()
