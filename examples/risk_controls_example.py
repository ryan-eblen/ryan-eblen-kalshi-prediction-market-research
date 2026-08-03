"""Sanitized pre-trade risk-control example.

This standalone module demonstrates configurable order, position, exposure,
duplicate-submission, and daily-loss controls for a prediction-market system.

It uses synthetic state only and contains no production account information,
credentials, private market data, or proprietary strategy parameters.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class ProposedOrder:
    """One order submitted for pre-trade risk evaluation."""

    order_id: str
    ticker: str
    side: str
    quantity: int
    price: float
    estimated_cost_per_contract: float = 0.0


@dataclass(frozen=True)
class OpenPosition:
    """One synthetic open prediction-market position."""

    position_id: str
    ticker: str
    side: str
    quantity: int
    entry_price: float


@dataclass(frozen=True)
class RiskLimits:
    """Configurable limits applied before order submission."""

    max_order_quantity: int
    max_ticker_quantity: int
    max_gross_exposure: float
    max_daily_loss: float
    max_open_positions: int
    allowed_sides: tuple[str, ...] = ("YES", "NO")


@dataclass(frozen=True)
class RiskSnapshot:
    """Current synthetic account state used by the risk engine."""

    realized_pnl: float
    open_positions: tuple[OpenPosition, ...]
    processed_order_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class RiskCheck:
    """Result of one individual risk rule."""

    name: str
    passed: bool
    observed_value: str
    limit_value: str
    message: str


@dataclass(frozen=True)
class RiskEvaluation:
    """Complete pre-trade risk decision."""

    decision: str
    normalized_side: str
    projected_ticker_quantity: int
    projected_open_positions: int
    projected_gross_exposure: float
    checks: tuple[RiskCheck, ...]

    @property
    def failed_check_names(self) -> tuple[str, ...]:
        """Return the names of every failed risk check."""

        return tuple(
            check.name
            for check in self.checks
            if not check.passed
        )


def validate_nonempty_text(value: str, field_name: str) -> str:
    """Validate and normalize a required text field."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")

    normalized = value.strip()

    if not normalized:
        raise ValueError(f"{field_name} cannot be empty.")

    return normalized


def validate_positive_integer(value: int, field_name: str) -> int:
    """Validate a strictly positive integer."""

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer.")

    if value <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")

    return value


def validate_nonnegative_number(
    value: float,
    field_name: str,
) -> float:
    """Validate a finite number greater than or equal to zero."""

    if isinstance(value, bool) or not isinstance(
        value,
        (int, float),
    ):
        raise TypeError(f"{field_name} must be numeric.")

    normalized = float(value)

    if not isfinite(normalized):
        raise ValueError(f"{field_name} must be finite.")

    if normalized < 0.0:
        raise ValueError(f"{field_name} cannot be negative.")

    return normalized


def validate_contract_price(value: float, field_name: str) -> float:
    """Validate a prediction-market price between zero and one."""

    normalized = validate_nonnegative_number(
        value,
        field_name,
    )

    if normalized > 1.0:
        raise ValueError(
            f"{field_name} must be between 0.0 and 1.0."
        )

    return normalized


def normalize_side(value: str) -> str:
    """Normalize a contract side without silently accepting invalid text."""

    return validate_nonempty_text(value, "side").upper()


def validate_limits(limits: RiskLimits) -> tuple[str, ...]:
    """Validate risk-limit configuration and normalize allowed sides."""

    validate_positive_integer(
        limits.max_order_quantity,
        "max_order_quantity",
    )
    validate_positive_integer(
        limits.max_ticker_quantity,
        "max_ticker_quantity",
    )
    validate_nonnegative_number(
        limits.max_gross_exposure,
        "max_gross_exposure",
    )
    validate_nonnegative_number(
        limits.max_daily_loss,
        "max_daily_loss",
    )
    validate_positive_integer(
        limits.max_open_positions,
        "max_open_positions",
    )

    if not limits.allowed_sides:
        raise ValueError("At least one allowed side is required.")

    normalized_sides = tuple(
        normalize_side(side)
        for side in limits.allowed_sides
    )

   if len(set(normalized_sides)) != len(normalized_sides):
       raise ValueError("allowed_sides cannot contain duplicates.")

    invalid_sides = set(normalized_sides).difference(
        {"YES", "NO"}
    )

    if invalid_sides:
        raise ValueError(
            "allowed_sides may contain only YES and NO."
        )

    return normalized_sides

def validate_position(position: OpenPosition) -> None:
    """Validate one existing synthetic position."""

    validate_nonempty_text(
        position.position_id,
        "position_id",
    )
    validate_nonempty_text(
        position.ticker,
        "ticker",
    )

    normalized_side = normalize_side(position.side)

    if normalized_side not in {"YES", "NO"}:
        raise ValueError("Position side must be YES or NO.")

    validate_positive_integer(
        position.quantity,
        "position quantity",
    )
    validate_contract_price(
        position.entry_price,
        "entry_price",
    )


def validate_snapshot(snapshot: RiskSnapshot) -> None:
    """Validate current account state before calculating risk."""

    if isinstance(snapshot.realized_pnl, bool) or not isinstance(
        snapshot.realized_pnl,
        (int, float),
    ):
        raise TypeError("realized_pnl must be numeric.")

    if not isfinite(float(snapshot.realized_pnl)):
        raise ValueError("realized_pnl must be finite.")

    position_ids: list[str] = []

    for position in snapshot.open_positions:
        validate_position(position)
        position_ids.append(position.position_id.strip())

    if len(set(position_ids)) != len(position_ids):
        raise ValueError("Open position IDs must be unique.")

    normalized_order_ids = [
        validate_nonempty_text(order_id, "processed order ID")
        for order_id in snapshot.processed_order_ids
    ]

    if len(set(normalized_order_ids)) != len(
        normalized_order_ids
    ):
        raise ValueError(
            "Processed order IDs must be unique."
        )


def calculate_current_gross_exposure(
    positions: tuple[OpenPosition, ...],
) -> float:
    """Calculate capital committed at position entry prices."""

    return float(
        sum(
            position.quantity * position.entry_price
            for position in positions
        )
    )


def evaluate_order_risk(
    *,
    order: ProposedOrder,
    snapshot: RiskSnapshot,
    limits: RiskLimits,
) -> RiskEvaluation:
    """Evaluate a proposed order against configurable risk controls."""

    order_id = validate_nonempty_text(
        order.order_id,
        "order_id",
    )
    ticker = validate_nonempty_text(
        order.ticker,
        "ticker",
    ).upper()
    side = normalize_side(order.side)

    quantity = validate_positive_integer(
        order.quantity,
        "quantity",
    )
    price = validate_contract_price(
        order.price,
        "price",
    )
    estimated_cost = validate_nonnegative_number(
        order.estimated_cost_per_contract,
        "estimated_cost_per_contract",
    )

    allowed_sides = validate_limits(limits)
    validate_snapshot(snapshot)

    existing_ticker_quantity = sum(
        position.quantity
        for position in snapshot.open_positions
        if position.ticker.strip().upper() == ticker
    )

    projected_ticker_quantity = (
        existing_ticker_quantity + quantity
    )

    matching_position_exists = any(
        position.ticker.strip().upper() == ticker
        and normalize_side(position.side) == side
        for position in snapshot.open_positions
    )

    projected_open_positions = (
        len(snapshot.open_positions)
        if matching_position_exists
        else len(snapshot.open_positions) + 1
    )

    current_exposure = calculate_current_gross_exposure(
        snapshot.open_positions
    )

    proposed_capital = quantity * (
        price + estimated_cost
    )

    projected_gross_exposure = (
        current_exposure + proposed_capital
    )

    current_daily_loss = max(
        0.0,
        -float(snapshot.realized_pnl),
    )

    normalized_processed_order_ids = tuple(
        validate_nonempty_text(
            processed_order_id,
            "processed order ID",
        )
        for processed_order_id in snapshot.processed_order_ids
    )

    unique_order_passed = (
        order_id not in normalized_processed_order_ids
    )
    side_passed = side in allowed_sides
    order_quantity_passed = (
        quantity <= limits.max_order_quantity
    )
    ticker_quantity_passed = (
        projected_ticker_quantity
        <= limits.max_ticker_quantity
    )
    exposure_passed = (
        projected_gross_exposure
        <= limits.max_gross_exposure
    )
    position_count_passed = (
        projected_open_positions
        <= limits.max_open_positions
    )

    daily_loss_passed = (
        current_daily_loss < limits.max_daily_loss
    )

    checks = (
        RiskCheck(
            name="UNIQUE_ORDER_ID",
            passed=unique_order_passed,
            observed_value=order_id,
            limit_value="not previously processed",
            message=(
                "Order identifier has not been processed."
                if unique_order_passed
                else "Duplicate order identifier detected."
            ),
        ),
        RiskCheck(
            name="ALLOWED_SIDE",
            passed=side_passed,
            observed_value=side,
            limit_value=", ".join(allowed_sides),
            message=(
                "Contract side is permitted."
                if side_passed
                else "Contract side is not permitted."
            ),
        ),
        RiskCheck(
            name="MAX_ORDER_QUANTITY",
            passed=order_quantity_passed,
            observed_value=str(quantity),
            limit_value=str(limits.max_order_quantity),
            message=(
                "Order quantity is within the limit."
                if order_quantity_passed
                else "Order quantity exceeds the limit."
            ),
        ),
        RiskCheck(
            name="MAX_TICKER_QUANTITY",
            passed=ticker_quantity_passed,
            observed_value=str(projected_ticker_quantity),
            limit_value=str(limits.max_ticker_quantity),
            message=(
                "Projected ticker quantity is within the limit."
                if ticker_quantity_passed
                else "Projected ticker quantity exceeds the limit."
            ),
        ),
        RiskCheck(
            name="MAX_GROSS_EXPOSURE",
            passed=exposure_passed,
            observed_value=f"{projected_gross_exposure:.4f}",
            limit_value=f"{limits.max_gross_exposure:.4f}",
            message=(
                "Projected exposure is within the limit."
                if exposure_passed
                else "Projected exposure exceeds the limit."
            ),
        ),
        RiskCheck(
            name="MAX_OPEN_POSITIONS",
            passed=position_count_passed,
            observed_value=str(projected_open_positions),
            limit_value=str(limits.max_open_positions),
            message=(
                "Projected position count is within the limit."
                if position_count_passed
                else "Projected position count exceeds the limit."
            ),
        ),
        RiskCheck(
            name="MAX_DAILY_LOSS",
            passed=daily_loss_passed,
            observed_value=f"{current_daily_loss:.4f}",
            limit_value=f"{limits.max_daily_loss:.4f}",
            message=(
                "Daily loss remains below the stop level."
                if daily_loss_passed
                else "Daily loss stop has been reached."
            ),
        ),
    )

    decision = (
        "APPROVE"
        if all(check.passed for check in checks)
        else "REJECT"
    )

    return RiskEvaluation(
        decision=decision,
        normalized_side=side,
        projected_ticker_quantity=(
            projected_ticker_quantity
        ),
        projected_open_positions=(
            projected_open_positions
        ),
        projected_gross_exposure=(
            projected_gross_exposure
        ),
        checks=checks,
    )


def print_evaluation(
    label: str,
    evaluation: RiskEvaluation,
) -> None:
    """Print one readable risk decision."""

    print("=" * 78)
    print(label)
    print("=" * 78)
    print(f"Decision:                   {evaluation.decision}")
    print(
        "Projected ticker quantity:  "
        f"{evaluation.projected_ticker_quantity}"
    )
    print(
        "Projected open positions:   "
        f"{evaluation.projected_open_positions}"
    )
    print(
        "Projected gross exposure:   "
        f"{evaluation.projected_gross_exposure:.4f}"
    )
    print(
        "Failed checks:              "
        f"{evaluation.failed_check_names or 'None'}"
    )
    print()

    for check in evaluation.checks:
        status = "PASS" if check.passed else "FAIL"

        print(
            f"{status:4s} | {check.name:22s} | "
            f"{check.message}"
        )

    print()


def build_example_snapshot() -> RiskSnapshot:
    """Create deterministic synthetic account state."""

    return RiskSnapshot(
        realized_pnl=-0.40,
        open_positions=(
            OpenPosition(
                position_id="position-001",
                ticker="KX-RATE",
                side="YES",
                quantity=4,
                entry_price=0.45,
            ),
            OpenPosition(
                position_id="position-002",
                ticker="KX-INFLATION",
                side="NO",
                quantity=3,
                entry_price=0.60,
            ),
        ),
        processed_order_ids=("order-previous",),
    )


def build_example_limits() -> RiskLimits:
    """Create deterministic synthetic risk limits."""

    return RiskLimits(
        max_order_quantity=10,
        max_ticker_quantity=12,
        max_gross_exposure=8.00,
        max_daily_loss=1.50,
        max_open_positions=3,
        allowed_sides=("YES", "NO"),
    )


def main() -> None:
    """Run approved and rejected synthetic risk examples."""

    snapshot = build_example_snapshot()
    limits = build_example_limits()

    approved_order = ProposedOrder(
        order_id="order-approved",
        ticker="KX-RATE",
        side=" yes ",
        quantity=3,
        price=0.40,
        estimated_cost_per_contract=0.01,
    )

    exposure_rejected_order = ProposedOrder(
        order_id="order-exposure-rejected",
        ticker="KX-ECONOMY",
        side="YES",
        quantity=10,
        price=0.50,
        estimated_cost_per_contract=0.01,
    )

    duplicate_order = ProposedOrder(
        order_id="order-previous",
        ticker="KX-RATE",
        side="YES",
        quantity=1,
        price=0.40,
    )

    loss_stopped_snapshot = RiskSnapshot(
        realized_pnl=-1.50,
        open_positions=snapshot.open_positions,
        processed_order_ids=snapshot.processed_order_ids,
    )

    loss_stopped_order = ProposedOrder(
        order_id="order-loss-stopped",
        ticker="KX-RATE",
        side="YES",
        quantity=1,
        price=0.40,
    )

    print_evaluation(
        "Approved example",
        evaluate_order_risk(
            order=approved_order,
            snapshot=snapshot,
            limits=limits,
        ),
    )

    print_evaluation(
        "Exposure-rejected example",
        evaluate_order_risk(
            order=exposure_rejected_order,
            snapshot=snapshot,
            limits=limits,
        ),
    )

    print_evaluation(
        "Duplicate-order example",
        evaluate_order_risk(
            order=duplicate_order,
            snapshot=snapshot,
            limits=limits,
        ),
    )

    print_evaluation(
        "Daily-loss-stop example",
        evaluate_order_risk(
            order=loss_stopped_order,
            snapshot=loss_stopped_snapshot,
            limits=limits,
        ),
    )


if __name__ == "__main__":
    main()
