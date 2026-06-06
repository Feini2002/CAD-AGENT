"""Expression regression guard for adaptive foundation replay."""

from __future__ import annotations

from typing import Any


EXPRESSION_RANK = {
    "smoke": 1,
    "growth": 2,
    "standard": 3,
}


def _rank(level: str) -> int:
    return EXPRESSION_RANK.get(str(level), 0)


def evaluate_expression_regression_guard(
    items: list[dict[str, Any]],
    *,
    replay_mode: str,
    allow_low_expression: bool = False,
) -> dict[str, Any]:
    if replay_mode == "smoke_replay":
        return {
            "schemaVersion": 1,
            "status": "not_applicable",
            "replayMode": replay_mode,
            "allowLowExpression": bool(allow_low_expression),
            "reason": "smoke_replay keeps legacy low-expression smoke behavior.",
            "acceptedExemption": "explicit_minimal_smoke",
            "comparisonPolicy": {
                "semanticFeatures": False,
                "machineEvidence": False,
                "scopeAware": True,
                "screenshotOnly": False,
                "handleCountOnly": False,
                "fakeCadOnly": False,
                "workbenchStateOnly": False,
            },
            "failures": [],
            "items": [],
        }

    checked_items = []
    failures = []
    for item in items:
        capability_id = str(item.get("capabilityId", ""))
        target = str(item.get("targetExpressionLevel") or "smoke")
        baseline = str(item.get("baselineExpressionLevel") or target)
        accepted_low = bool(item.get("acceptedLowExpression", False))
        observed_features = {
            str(feature)
            for feature in item.get("observedFeatures", [])
            if feature
        }
        missing_features = [
            str(feature)
            for feature in item.get("requiredFeatures", [])
            if feature and str(feature) not in observed_features
        ]
        regressed = _rank(target) < _rank(baseline)
        blocked = (regressed and not (allow_low_expression or accepted_low)) or bool(missing_features)
        checked = {
            "capabilityId": capability_id,
            "guardType": "expression_regression",
            "minExpressionLevel": baseline,
            "targetExpressionLevel": target,
            "compareMethod": {
                "semanticFeatures": True,
                "machineEvidence": True,
                "scopeAware": True,
                "screenshotOnly": False,
                "handleCountOnly": False,
            },
            "acceptedExemption": bool((allow_low_expression or accepted_low) and regressed),
            "missingFeatures": missing_features,
            "baselineEvidenceStatus": "profile_context_only",
        }
        checked_items.append(checked)
        if blocked:
            reason = "expression_regression" if regressed else "required_features_missing"
            failures.append(
                {
                    "capabilityId": capability_id,
                    "reason": reason,
                    "baselineExpressionLevel": baseline,
                    "targetExpressionLevel": target,
                    "missingFeatures": missing_features,
                    "failureAction": "block_pass",
                }
            )

    return {
        "schemaVersion": 1,
        "guardId": "adaptive-foundation-expression-regression",
        "status": "blocked" if failures else "pass",
        "replayMode": replay_mode,
        "allowLowExpression": bool(allow_low_expression),
        "failureAction": "block_pass",
        "allowedExemptions": ["explicit_allow_low_expression"] if allow_low_expression else [],
        "comparisonPolicy": {
            "semanticFeatures": True,
            "machineEvidence": True,
            "scopeAware": True,
            "screenshotOnly": False,
            "handleCountOnly": False,
            "fakeCadOnly": False,
            "workbenchStateOnly": False,
            "modelJudgmentOnly": False,
        },
        "forbiddenRegressionSignals": [
            "target expression level lower than profile baseline",
            "required semantic features missing",
            "screenshot-only pass",
            "handle-count-only pass",
        ],
        "failures": failures,
        "items": checked_items,
        "reason": "expression regression detected" if failures else "",
    }
