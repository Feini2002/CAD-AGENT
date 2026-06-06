from __future__ import annotations

import unittest


class ErrorTaxonomyTests(unittest.TestCase):
    def test_network_text_is_classified_as_network_unavailable(self) -> None:
        from core.orchestrator.error_taxonomy import NETWORK_UNAVAILABLE, classify_error_category

        self.assertEqual(classify_error_category(stderr="websocket failed while connecting to api.openai.com"), NETWORK_UNAVAILABLE)
        self.assertEqual(classify_error_category(stderr="访问权限不允许访问套接字"), NETWORK_UNAVAILABLE)

    def test_nonzero_without_network_clue_is_provider_unavailable(self) -> None:
        from core.orchestrator.error_taxonomy import PROVIDER_UNAVAILABLE, classify_error_category

        self.assertEqual(classify_error_category(return_code=1, stderr="codex command failed"), PROVIDER_UNAVAILABLE)

    def test_schema_missing_fields_is_schema_invalid(self) -> None:
        from core.orchestrator.error_taxonomy import SCHEMA_INVALID, classify_error_category

        self.assertEqual(
            classify_error_category(validation={"status": "fail", "missingFields": ["assumptions"], "issues": []}),
            SCHEMA_INVALID,
        )

    def test_schema_valid_business_unavailable_is_not_provider_unavailable(self) -> None:
        from core.orchestrator.error_taxonomy import MODEL_BUSINESS_BLOCKED, classify_error_category

        self.assertEqual(
            classify_error_category(
                review={"status": "unavailable", "modelInvoked": True},
                validation={"status": "pass", "issues": [], "missingFields": []},
            ),
            MODEL_BUSINESS_BLOCKED,
        )

    def test_provider_status_includes_error_category(self) -> None:
        from core.model_review.provider_status import with_model_provider_status
        from core.orchestrator.error_taxonomy import MODEL_BUSINESS_BLOCKED, PROVIDER_UNAVAILABLE

        provider_fail = with_model_provider_status({"status": "unavailable", "modelInvoked": False})
        self.assertEqual(provider_fail["modelProviderStatus"]["errorCategory"], PROVIDER_UNAVAILABLE)

        business_fail = with_model_provider_status(
            {"status": "unavailable", "modelInvoked": True},
            validation={"status": "pass", "issues": [], "missingFields": []},
        )
        self.assertEqual(business_fail["modelProviderStatus"]["errorCategory"], MODEL_BUSINESS_BLOCKED)


if __name__ == "__main__":
    unittest.main()
