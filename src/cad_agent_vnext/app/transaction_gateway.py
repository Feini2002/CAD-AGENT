from __future__ import annotations

from typing import Any, Literal

from cad_agent_vnext.domain.patch import CadPatch
from cad_agent_vnext.domain.ports import CadBackend
from cad_agent_vnext.domain.receipt import EntityReadback, ExecutionReceipt
from cad_agent_vnext.policy.safety_policy import Gate0SafetyPolicy
from cad_agent_vnext.policy.transaction_policy import audit_patch_policy, audit_receipt_policy


class CadTransactionGateway:
    def __init__(self, *, backend: CadBackend, policy: Gate0SafetyPolicy | None = None) -> None:
        self.backend = backend
        self.policy = policy or Gate0SafetyPolicy()
        self._completed_transactions: set[str] = set()

    def execute(
        self,
        patch: CadPatch,
        *,
        prior_receipt: ExecutionReceipt | None = None,
        repair: bool = False,
    ) -> ExecutionReceipt:
        if patch.transaction_id in self._completed_transactions:
            return _gateway_receipt(patch, status="blocked", errors=["duplicate_transaction_id"])

        patch_decision = audit_patch_policy(patch, policy=self.policy, prior_receipt=prior_receipt, repair=repair)
        if not patch_decision.allowed:
            return _gateway_receipt(patch, status="blocked", errors=patch_decision.reasons)

        try:
            receipt = self.backend.apply_patch(patch)
        except Exception as exc:
            return _gateway_receipt(patch, status="failed", errors=[f"backend_apply_exception:{type(exc).__name__}:{exc}"])

        try:
            readback = self.backend.readback(transaction_id=patch.transaction_id)
        except Exception as exc:
            readback = _SimpleReadback(entities=[])
            audit_errors = [f"readback_exception:{type(exc).__name__}:{exc}"]
        else:
            audit_errors = []

        receipt_decision = audit_receipt_policy(patch, receipt=receipt, readback=readback, policy=self.policy)
        if audit_errors or not receipt_decision.allowed:
            errors = _errors(receipt) + audit_errors + receipt_decision.reasons
            errors.extend(self._rollback_after_failure(receipt))
            return _gateway_receipt(
                patch,
                status="failed",
                backend=str(_value(receipt, "backend", "transaction-gateway")),
                semantic_to_handles=_dict_of_lists(_value(receipt, "semantic_to_handles", {}) or {}),
                entities=_entities(readback),
                created_handles=_string_list(_value(receipt, "created_handles", []) or []),
                updated_handles=_string_list(_value(receipt, "updated_handles", []) or []),
                deleted_handles=_string_list(_value(receipt, "deleted_handles", []) or []),
                rollback_token=_optional_string(_value(receipt, "rollback_token")),
                errors=errors,
            )

        self._completed_transactions.add(patch.transaction_id)
        return _gateway_receipt(
            patch,
            status="succeeded",
            backend=str(_value(receipt, "backend", "transaction-gateway")),
            semantic_to_handles=_dict_of_lists(_value(receipt, "semantic_to_handles", {}) or {}),
            entities=_entities(readback),
            created_handles=_string_list(_value(receipt, "created_handles", []) or []),
            updated_handles=_string_list(_value(receipt, "updated_handles", []) or []),
            deleted_handles=_string_list(_value(receipt, "deleted_handles", []) or []),
            rollback_token=_optional_string(_value(receipt, "rollback_token")),
            errors=_errors(receipt),
            warnings=_warnings(receipt),
        )

    def _rollback_after_failure(self, receipt: Any) -> list[str]:
        rollback_token = _value(receipt, "rollback_token")
        if not rollback_token:
            return ["rollback_token_missing"]
        try:
            rollback_receipt = self.backend.rollback(rollback_token=str(rollback_token))
        except Exception as exc:
            return [f"rollback_failed:{type(exc).__name__}:{exc}"]
        if _value(rollback_receipt, "status") != "succeeded":
            return ["rollback_failed", *_errors(rollback_receipt)]
        return []


class _SimpleReadback:
    def __init__(self, *, entities: list[EntityReadback]) -> None:
        self.entities = entities


def _gateway_receipt(
    patch: CadPatch,
    *,
    status: Literal["succeeded", "blocked", "failed"],
    backend: str = "transaction-gateway",
    semantic_to_handles: dict[str, list[str]] | None = None,
    entities: list[EntityReadback] | None = None,
    created_handles: list[str] | None = None,
    updated_handles: list[str] | None = None,
    deleted_handles: list[str] | None = None,
    rollback_token: str | None = None,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
) -> ExecutionReceipt:
    return ExecutionReceipt(
        schema_version="execution-receipt/v1",
        run_id=patch.run_id,
        transaction_id=patch.transaction_id,
        backend=backend,
        status=status,
        semantic_to_handles=semantic_to_handles or {},
        entities=entities or [],
        created_handles=created_handles or [],
        updated_handles=updated_handles or [],
        deleted_handles=deleted_handles or [],
        saved_current_dwg=False,
        rollback_token=rollback_token,
        errors=list(errors or []),
        warnings=list(warnings or []),
    )


def _entities(readback: Any) -> list[EntityReadback]:
    entities = _value(readback, "entities", []) or []
    result: list[EntityReadback] = []
    for entity in entities:
        if isinstance(entity, EntityReadback):
            result.append(entity)
        elif isinstance(entity, dict):
            result.append(
                EntityReadback(
                    handle=str(entity.get("handle", "")),
                    entity_type=str(entity.get("entity_type", entity.get("type", "UNKNOWN"))),
                    layer=str(entity.get("layer", "")),
                    bbox=entity.get("bbox"),
                )
            )
    return result


def _value(item: Any, name: str, default: Any = None) -> Any:
    if isinstance(item, dict):
        return item.get(name, default)
    return getattr(item, name, default)


def _string_list(values: Any) -> list[str]:
    return [str(value) for value in values] if isinstance(values, list) else []


def _dict_of_lists(value: Any) -> dict[str, list[str]]:
    if not isinstance(value, dict):
        return {}
    return {str(key): _string_list(list(values) if isinstance(values, tuple) else values) for key, values in value.items()}


def _optional_string(value: Any) -> str | None:
    return str(value) if value else None


def _errors(receipt: Any) -> list[str]:
    return _string_list(_value(receipt, "errors", []) or [])


def _warnings(receipt: Any) -> list[str]:
    return _string_list(_value(receipt, "warnings", []) or [])
