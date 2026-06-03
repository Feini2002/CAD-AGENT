"""Optional streaming-demo pacing helpers for fake/unit CAD training runs."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Callable

from core.safety.policy import PREVIEW_LAYER


DEFAULT_STREAM_OPERATIONS = (
    "rect",
    "line",
    "polyline",
    "circle",
    "arc",
    "dimension",
    "hatch",
    "block",
)

SleepFn = Callable[[float], None]
ClockFn = Callable[[], float]


@dataclass
class StreamingCadDemoConfig:
    enabled: bool = False
    mode: str = "disabled"
    item_delay_seconds: float = 0.0
    operation_delay_seconds: float = 0.0
    operation_budget_per_item: int = 0
    zoom_each_item: bool = False
    zoom_padding_ratio: float = 0.2
    critical_operations: tuple[str, ...] = field(default_factory=lambda: DEFAULT_STREAM_OPERATIONS)

    def __post_init__(self) -> None:
        self.item_delay_seconds = max(0.0, float(self.item_delay_seconds))
        self.operation_delay_seconds = max(0.0, float(self.operation_delay_seconds))
        self.operation_budget_per_item = max(0, int(self.operation_budget_per_item))
        self.zoom_padding_ratio = max(0.0, float(self.zoom_padding_ratio))
        self.critical_operations = tuple(self.critical_operations)

    @classmethod
    def disabled(cls) -> "StreamingCadDemoConfig":
        return cls()

    @classmethod
    def hybrid(
        cls,
        *,
        item_delay_seconds: float = 0.35,
        operation_delay_seconds: float = 0.12,
        operation_budget_per_item: int = 5,
        zoom_each_item: bool = True,
        zoom_padding_ratio: float = 0.2,
        critical_operations: tuple[str, ...] = DEFAULT_STREAM_OPERATIONS,
    ) -> "StreamingCadDemoConfig":
        return cls(
            enabled=True,
            mode="hybrid",
            item_delay_seconds=item_delay_seconds,
            operation_delay_seconds=operation_delay_seconds,
            operation_budget_per_item=operation_budget_per_item,
            zoom_each_item=zoom_each_item,
            zoom_padding_ratio=zoom_padding_ratio,
            critical_operations=critical_operations,
        )


class StreamingCadDemoRecorder:
    def __init__(
        self,
        config: StreamingCadDemoConfig | None = None,
        *,
        driver: Any | None = None,
        sleep_fn: SleepFn = time.sleep,
        clock_fn: ClockFn = time.monotonic,
    ) -> None:
        self.config = config or StreamingCadDemoConfig.disabled()
        self.driver = driver
        self.sleep_fn = sleep_fn
        self.clock_fn = clock_fn
        self.events: list[dict[str, Any]] = []
        self.operation_delay_count = 0
        self.item_delay_count = 0
        self.refresh_count = 0
        self.operation_delay_seconds_total = 0.0
        self.item_delay_seconds_total = 0.0
        self._remaining_operation_budget = self.config.operation_budget_per_item

    @property
    def delay_seconds_total(self) -> float:
        return self.operation_delay_seconds_total + self.item_delay_seconds_total

    def _sleep(self, seconds: float) -> float:
        started = self.clock_fn()
        self.sleep_fn(seconds)
        return max(0.0, self.clock_fn() - started)

    def start_item(self, capability_id: str, index: int | None = None) -> None:
        if not self.config.enabled:
            return
        self._remaining_operation_budget = self.config.operation_budget_per_item
        self.events.append(
            {
                "event": "item_start",
                "capabilityId": capability_id,
                "index": index,
                "timestamp": self.clock_fn(),
                "operationBudget": self._remaining_operation_budget,
            }
        )

    def after_operation(self, operation: str, created_handles: list[str] | tuple[str, ...] | None) -> None:
        if not self.config.enabled:
            return

        handles = list(created_handles or [])
        should_delay = (
            bool(handles)
            and operation in self.config.critical_operations
            and self.config.operation_delay_seconds > 0
            and self._remaining_operation_budget > 0
        )
        refresh = {"status": "skipped", "reason": "operation delay not applied"}
        actual_delay_seconds = 0.0
        if should_delay:
            refresh = self._refresh_view()
            actual_delay_seconds = self._sleep(self.config.operation_delay_seconds)
            self.operation_delay_count += 1
            self.operation_delay_seconds_total += actual_delay_seconds
            self._remaining_operation_budget -= 1

        self.events.append(
            {
                "event": "operation",
                "operation": operation,
                "handles": handles,
                "handle_count": len(handles),
                "delayed": should_delay,
                "delaySeconds": self.config.operation_delay_seconds if should_delay else 0.0,
                "actualDelaySeconds": round(actual_delay_seconds, 10),
                "remainingOperationBudget": self._remaining_operation_budget,
                "refresh": refresh,
                "timestamp": self.clock_fn(),
            }
        )

    def after_item(
        self,
        created_handles: list[str] | tuple[str, ...] | None,
        *,
        capability_id: str | None = None,
    ) -> None:
        if not self.config.enabled:
            return

        handles = list(created_handles or [])
        zoom = {"status": "skipped"}
        if self.config.zoom_each_item and handles:
            zoom_to_handles = getattr(self.driver, "zoom_to_handles", None)
            if callable(zoom_to_handles):
                try:
                    zoom_result = zoom_to_handles(
                        handles=handles,
                        layer=PREVIEW_LAYER,
                        padding_ratio=self.config.zoom_padding_ratio,
                    )
                except Exception as exc:  # pragma: no cover - exercised via unit test
                    zoom = {"status": "failed", "error": str(exc)}
                else:
                    if isinstance(zoom_result, dict):
                        zoom = dict(zoom_result)
                    else:
                        zoom = {"status": "success", "result": zoom_result}
            else:
                zoom = {"status": "skipped", "reason": "driver has no zoom_to_handles"}

        delayed = False
        refresh = {"status": "skipped", "reason": "item delay not applied"}
        actual_delay_seconds = 0.0
        if handles and self.config.item_delay_seconds > 0:
            refresh = self._refresh_view()
            actual_delay_seconds = self._sleep(self.config.item_delay_seconds)
            self.item_delay_count += 1
            self.item_delay_seconds_total += actual_delay_seconds
            delayed = True

        self.events.append(
            {
                "event": "item_complete",
                "capabilityId": capability_id,
                "handles": handles,
                "handle_count": len(handles),
                "zoom": zoom,
                "delayed": delayed,
                "delaySeconds": self.config.item_delay_seconds if delayed else 0.0,
                "actualDelaySeconds": round(actual_delay_seconds, 10),
                "refresh": refresh,
                "timestamp": self.clock_fn(),
            }
        )

    def _refresh_view(self) -> dict[str, Any]:
        refresh_view = getattr(self.driver, "refresh_view", None)
        if callable(refresh_view):
            try:
                result = refresh_view()
            except Exception as exc:  # pragma: no cover - exercised via unit test
                return {"status": "failed", "error": str(exc)}
            else:
                self.refresh_count += 1
                if isinstance(result, dict):
                    return dict(result)
                return {"status": "success", "result": result}
        return {"status": "skipped", "reason": "driver has no refresh_view"}

    def summary(self) -> dict[str, Any]:
        return {
            "enabled": self.config.enabled,
            "mode": self.config.mode,
            "itemDelaySeconds": self.config.item_delay_seconds,
            "operationDelaySeconds": self.config.operation_delay_seconds,
            "operationBudgetPerItem": self.config.operation_budget_per_item,
            "zoomEachItem": self.config.zoom_each_item,
            "delayTelemetryBasis": "measured_sleep",
            "event_count": len(self.events),
            "operation_delay_count": self.operation_delay_count,
            "item_delay_count": self.item_delay_count,
            "operationDelaySecondsTotal": round(self.operation_delay_seconds_total, 10),
            "itemDelaySecondsTotal": round(self.item_delay_seconds_total, 10),
            "delaySecondsTotal": round(self.delay_seconds_total, 10),
            "refresh_count": self.refresh_count,
            "events": list(self.events),
        }
