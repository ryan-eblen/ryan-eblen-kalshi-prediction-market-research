"""Sanitized order-reconciliation example.

This standalone example demonstrates how an application can reconcile
cumulative exchange fills with internal order and position state.

It does not connect to an exchange and does not contain production code,
credentials, account data, or proprietary trading logic.
"""

from dataclasses import dataclass, replace
from typing import Literal


Side = Literal["YES", "NO"]
InternalStatus = Literal[
    "SUBMITTED",
    "ACKED",
    "PARTIALLY_FILLED",
    "FILLED",
    "CANCELED",
]
ExchangeStatus = Literal[
    "OPEN",
    "PARTIALLY_FILLED",
    "FILLED",
    "CANCELED",
]


@dataclass(frozen=True)
class OrderState:
    """Internal application state for one order."""

    order_id: str
    ticker: str
    side: Side
    requested_quantity: int
    processed_filled_quantity: int = 0
    status: InternalStatus = "SUBMITTED"


@dataclass(frozen=True)
class PositionState:
    """Internal application position associated with an order."""

    ticker: str
    side: Side
    quantity: int = 0


@dataclass(frozen=True)
class ExchangeOrderSnapshot:
    """Cumulative order state reported by an exchange."""

    order_id: str
    cumulative_filled_quantity: int
    status: ExchangeStatus


@dataclass(frozen=True)
class ReconciliationResult:
    """Result returned by one reconciliation pass."""

    order: OrderState
    position: PositionState
    newly_filled_quantity: int
    action: str


def validate_positive_integer(value: int, field_name: str) -> int:
    """Validate a strictly positive integer."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return value


def validate_nonnegative_integer(value: int, field_name: str) -> int:
    """Validate an integer greater than or equal to zero."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")

    if value < 0:
        raise ValueError(f"{field_name} cannot be negative.")

    return value


def validate_order_state(order: OrderState) -> None:
    """Validate the internal order before reconciliation."""

    validate_positive_integer(
        order.requested_quantity,
        "requested_quantity",
    )
    validate_nonnegative_integer(
        order.processed_filled_quantity,
        "processed_filled_quantity",
    )

    if order.processed_filled_quantity > order.requested_quantity:
        raise ValueError(
            "processed_filled_quantity cannot exceed requested_quantity."
        )


def validate_position_state(
    order: OrderState,
    position: PositionState,
) -> None:
    """Confirm that the position belongs to the reconciled order."""

    validate_nonnegative_integer(position.quantity, "position quantity")

    if position.ticker != order.ticker:
        raise ValueError("Position ticker does not match the order ticker.")

    if position.side != order.side:
        raise ValueError("Position side does not match the order side.")


def validate_exchange_snapshot(
    order: OrderState,
    snapshot: ExchangeOrderSnapshot,
) -> None:
    """Validate cumulative exchange state."""

    if snapshot.order_id != order.order_id:
        raise ValueError("Exchange order ID does not match internal order ID.")

    validate_nonnegative_integer(
        snapshot.cumulative_filled_quantity,
        "cumulative_filled_quantity",
    )

    if snapshot.cumulative_filled_quantity > order.requested_quantity:
        raise ValueError(
            "Exchange fill quantity cannot exceed requested quantity."
        )

    if (
        snapshot.cumulative_filled_quantity
        < order.processed_filled_quantity
    ):
        raise ValueError(
            "Exchange cumulative fill cannot move backward."
        )

    if (
        snapshot.status == "FILLED"
        and snapshot.cumulative_filled_quantity
        != order.requested_quantity
    ):
        raise ValueError(
            "A FILLED snapshot must equal the requested quantity."
        )


def determine_internal_status(
    snapshot: ExchangeOrderSnapshot,
    requested_quantity: int,
) -> InternalStatus:
    """Translate exchange state into an internal status."""

    filled_quantity = snapshot.cumulative_filled_quantity

    if filled_quantity == requested_quantity:
        return "FILLED"

    if snapshot.status == "CANCELED":
        return "CANCELED"

    if filled_quantity > 0:
        return "PARTIALLY_FILLED"

    return "ACKED"


def reconcile_order(
    *,
    order: OrderState,
    position: PositionState,
    snapshot: ExchangeOrderSnapshot,
) -> ReconciliationResult:
    """Reconcile cumulative exchange fills with internal application state.

    The function calculates only the quantity that has not already been
    processed. Replaying the same exchange snapshot therefore produces no
    additional position quantity.
    """

    validate_order_state(order)
    validate_position_state(order, position)
    validate_exchange_snapshot(order, snapshot)

    newly_filled_quantity = (
        snapshot.cumulative_filled_quantity
        - order.processed_filled_quantity
    )

    updated_status = determine_internal_status(
        snapshot,
        order.requested_quantity,
    )

    updated_order = replace(
        order,
        processed_filled_quantity=(
            snapshot.cumulative_filled_quantity
        ),
        status=updated_status,
    )

    if newly_filled_quantity == 0:
        return ReconciliationResult(
            order=updated_order,
            position=position,
            newly_filled_quantity=0,
            action="NO_NEW_FILL",
        )

    updated_position = replace(
        position,
        quantity=position.quantity + newly_filled_quantity,
    )

    if position.quantity == 0:
        action = "POSITION_CREATED"
    else:
        action = "POSITION_INCREASED"

    return ReconciliationResult(
        order=updated_order,
        position=updated_position,
        newly_filled_quantity=newly_filled_quantity,
        action=action,
    )


def print_result(label: str, result: ReconciliationResult) -> None:
    """Display one reconciliation result."""

    print("=" * 68)
    print(label)
    print(f"Action:                    {result.action}")
    print(
        "Newly filled quantity:     "
        f"{result.newly_filled_quantity}"
    )
    print(
        "Processed filled quantity: "
        f"{result.order.processed_filled_quantity}"
    )
    print(f"Order status:              {result.order.status}")
    print(f"Position quantity:         {result.position.quantity}")


def main() -> None:
    """Demonstrate partial, repeated, and final-fill reconciliation."""

    order = OrderState(
        order_id="example-order-001",
        ticker="EXAMPLE-MARKET",
        side="YES",
        requested_quantity=5,
    )

    position = PositionState(
        ticker="EXAMPLE-MARKET",
        side="YES",
    )

    partial_snapshot = ExchangeOrderSnapshot(
        order_id="example-order-001",
        cumulative_filled_quantity=2,
        status="PARTIALLY_FILLED",
    )

    partial_result = reconcile_order(
        order=order,
        position=position,
        snapshot=partial_snapshot,
    )
    print_result("First reconciliation: partial fill", partial_result)

    repeated_result = reconcile_order(
        order=partial_result.order,
        position=partial_result.position,
        snapshot=partial_snapshot,
    )
    print_result("Second reconciliation: repeated snapshot", repeated_result)

    final_snapshot = ExchangeOrderSnapshot(
        order_id="example-order-001",
        cumulative_filled_quantity=5,
        status="FILLED",
    )

    final_result = reconcile_order(
        order=repeated_result.order,
        position=repeated_result.position,
        snapshot=final_snapshot,
    )
    print_result("Third reconciliation: final fill", final_result)


if __name__ == "__main__":
    main()
