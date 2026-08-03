"""Sanitized execution-funnel diagnostic example.

This module demonstrates how to distinguish order submission, exchange
execution, and internal position hydration when investigating a live-versus-
simulation execution gap.

It uses synthetic events only and contains no credentials, account data,
production logs, or proprietary trading logic.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


EventType = Literal[
    "ORDER_SUBMITTED",
    "ORDER_EXECUTED",
    "POSITION_HYDRATED",
]


@dataclass(frozen=True)
class ExecutionEvent:
    """One synthetic event in the order-to-position lifecycle."""

    order_id: str
    trade_id: str
    event_type: EventType


@dataclass(frozen=True)
class FunnelMetrics:
    """Summary statistics for one execution funnel."""

    submitted_orders: int
    executed_orders: int
    hydrated_positions: int
    execution_rate: float
    hydration_rate: float
    end_to_end_conversion_rate: float
    executed_not_hydrated: tuple[str, ...]
    duplicate_events: tuple[str, ...]


def validate_identifier(value: str, field_name: str) -> str:
    """Validate and normalize a required identifier."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} cannot be empty.")

    return normalized


def validate_event(event: ExecutionEvent) -> None:
    """Validate one execution-funnel event."""

    validate_identifier(event.order_id, "order_id")
    validate_identifier(event.trade_id, "trade_id")

    valid_event_types = {
        "ORDER_SUBMITTED",
        "ORDER_EXECUTED",
        "POSITION_HYDRATED",
    }

    if event.event_type not in valid_event_types:
        raise ValueError(
            f"Unsupported execution event: {event.event_type}"
        )


def safe_rate(numerator: int, denominator: int) -> float:
    """Calculate a rate without dividing by zero."""

    if denominator == 0:
        return 0.0

    return numerator / denominator


def analyze_execution_funnel(
    events: tuple[ExecutionEvent, ...],
) -> FunnelMetrics:
    """Analyze order submission, execution, and hydration conversion.

    Duplicate lifecycle events are reported but counted only once.
    """

    submitted_order_ids: set[str] = set()
    executed_order_ids: set[str] = set()
    hydrated_order_ids: set[str] = set()

    seen_event_keys: set[tuple[str, str]] = set()
    duplicate_event_keys: list[str] = []

    for event in events:
        validate_event(event)

        order_id = event.order_id.strip()
        event_key = (order_id, event.event_type)

        if event_key in seen_event_keys:
            duplicate_event_keys.append(
                f"{order_id}:{event.event_type}"
            )
            continue

        seen_event_keys.add(event_key)

        if event.event_type == "ORDER_SUBMITTED":
            submitted_order_ids.add(order_id)
        elif event.event_type == "ORDER_EXECUTED":
            executed_order_ids.add(order_id)
        elif event.event_type == "POSITION_HYDRATED":
            hydrated_order_ids.add(order_id)

    executed_without_submission = (
        executed_order_ids - submitted_order_ids
    )

    if executed_without_submission:
        invalid_orders = ", ".join(
            sorted(executed_without_submission)
        )
        raise ValueError(
            "Executed orders require a submission event: "
            f"{invalid_orders}"
        )

    hydrated_without_execution = (
        hydrated_order_ids - executed_order_ids
    )

    if hydrated_without_execution:
        invalid_orders = ", ".join(
            sorted(hydrated_without_execution)
        )
        raise ValueError(
            "Hydrated positions require an execution event: "
            f"{invalid_orders}"
        )

    submitted_count = len(submitted_order_ids)
    executed_count = len(executed_order_ids)
    hydrated_count = len(hydrated_order_ids)

    executed_not_hydrated = tuple(
        sorted(executed_order_ids - hydrated_order_ids)
    )

    return FunnelMetrics(
        submitted_orders=submitted_count,
        executed_orders=executed_count,
        hydrated_positions=hydrated_count,
        execution_rate=safe_rate(
            executed_count,
            submitted_count,
        ),
        hydration_rate=safe_rate(
            hydrated_count,
            executed_count,
        ),
        end_to_end_conversion_rate=safe_rate(
            hydrated_count,
            submitted_count,
        ),
        executed_not_hydrated=executed_not_hydrated,
        duplicate_events=tuple(
            sorted(duplicate_event_keys)
        ),
    )


def build_synthetic_events() -> tuple[ExecutionEvent, ...]:
    """Create deterministic synthetic execution events."""

    events: list[ExecutionEvent] = []

    for order_number in range(1, 21):
        order_id = f"order-{order_number:03d}"
        trade_id = f"trade-{order_number:03d}"

        events.append(
            ExecutionEvent(
                order_id=order_id,
                trade_id=trade_id,
                event_type="ORDER_SUBMITTED",
            )
        )

    for order_number in range(1, 6):
        order_id = f"order-{order_number:03d}"
        trade_id = f"trade-{order_number:03d}"

        events.append(
            ExecutionEvent(
                order_id=order_id,
                trade_id=trade_id,
                event_type="ORDER_EXECUTED",
            )
        )

    for order_number in range(1, 4):
        order_id = f"order-{order_number:03d}"
        trade_id = f"trade-{order_number:03d}"

        events.append(
            ExecutionEvent(
                order_id=order_id,
                trade_id=trade_id,
                event_type="POSITION_HYDRATED",
            )
        )

    events.append(
        ExecutionEvent(
            order_id="order-001",
            trade_id="trade-001",
            event_type="ORDER_EXECUTED",
        )
    )

    return tuple(events)


def print_funnel(metrics: FunnelMetrics) -> None:
    """Display a readable execution-funnel report."""

    print("=" * 78)
    print("Synthetic Execution-Funnel Diagnostic")
    print("=" * 78)
    print(
        f"Submitted orders:           {metrics.submitted_orders}"
    )
    print(
        f"Executed orders:            {metrics.executed_orders}"
    )
    print(
        f"Hydrated positions:         {metrics.hydrated_positions}"
    )
    print(
        "Submission-to-execution:    "
        f"{metrics.execution_rate:.2%}"
    )
    print(
        "Execution-to-hydration:     "
        f"{metrics.hydration_rate:.2%}"
    )
    print(
        "End-to-end conversion:      "
        f"{metrics.end_to_end_conversion_rate:.2%}"
    )
    print(
        "Executed, not hydrated:     "
        f"{metrics.executed_not_hydrated or 'None'}"
    )
    print(
        "Duplicate events ignored:  "
        f"{metrics.duplicate_events or 'None'}"
    )

    if metrics.executed_not_hydrated:
        print()
        print(
            "Diagnostic priority: investigate the execution-to-position "
            "hydration path."
        )


def main() -> None:
    """Run the synthetic execution-funnel diagnostic."""

    events = build_synthetic_events()
    metrics = analyze_execution_funnel(events)
    print_funnel(metrics)


if __name__ == "__main__":
    main()
