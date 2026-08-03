"""Expected-value example for a binary prediction-market contract.

This module is a sanitized, standalone educational example. It does not
connect to an exchange, submit orders, or reproduce private strategy logic.

Assumptions
-----------
- A correct contract pays $1.00 at settlement.
- An incorrect contract pays $0.00.
- Contract prices are expressed in dollars from 0.00 to 1.00.
- ``estimated_cost`` is a user-supplied estimate per contract.
- The example does not model liquidity, slippage, queue position, partial
  fills, capital constraints, or the current Kalshi fee schedule.
"""

from dataclasses import dataclass
from typing import Literal


Side = Literal["YES", "NO"]


@dataclass(frozen=True)
class ContractEvaluation:
    """Result of evaluating one prediction-market contract."""

    side: Side
    belief_yes_probability: float
    selected_outcome_probability: float
    contract_price: float
    estimated_cost: float
    gross_expected_profit: float
    net_expected_profit: float
    expected_return_on_cost: float
    classification: str


def validate_probability(value: float, field_name: str) -> float:
    """Validate and return a probability expressed from 0.0 to 1.0."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a numeric value.")

    normalized_value = float(value)

    if not 0.0 <= normalized_value <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0.")

    return normalized_value


def validate_nonnegative_cost(value: float) -> float:
    """Validate and return a nonnegative estimated execution cost."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("estimated_cost must be a numeric value.")

    normalized_value = float(value)

    if normalized_value < 0.0:
        raise ValueError("estimated_cost cannot be negative.")

    return normalized_value


def normalize_side(side: str) -> Side:
    """Normalize and validate a contract side."""

    if not isinstance(side, str):
        raise TypeError("side must be a string.")

    normalized_side = side.strip().upper()

    if normalized_side not in {"YES", "NO"}:
        raise ValueError("side must be either 'YES' or 'NO'.")

    return normalized_side  # type: ignore[return-value]


def classify_expected_profit(net_expected_profit: float) -> str:
    """Classify the contract using its net expected profit."""

    tolerance = 1e-12

    if net_expected_profit > tolerance:
        return "POSITIVE_EXPECTED_VALUE"

    if net_expected_profit < -tolerance:
        return "NEGATIVE_EXPECTED_VALUE"

    return "BREAK_EVEN_EXPECTED_VALUE"


def evaluate_contract(
    *,
    belief_yes_probability: float,
    side: str,
    contract_price: float,
    estimated_cost: float = 0.0,
) -> ContractEvaluation:
    """Evaluate the expected profit of purchasing one binary contract.

    For a YES contract:

        gross expected profit = belief_yes_probability - YES price

    For a NO contract:

        gross expected profit = (1 - belief_yes_probability) - NO price

    Estimated execution cost is then subtracted to calculate net expected
    profit.
    """

    validated_yes_probability = validate_probability(
        belief_yes_probability,
        "belief_yes_probability",
    )
    validated_price = validate_probability(contract_price, "contract_price")
    validated_cost = validate_nonnegative_cost(estimated_cost)
    normalized_side = normalize_side(side)

    if normalized_side == "YES":
        selected_outcome_probability = validated_yes_probability
    else:
        selected_outcome_probability = 1.0 - validated_yes_probability

    gross_expected_profit = selected_outcome_probability - validated_price
    net_expected_profit = gross_expected_profit - validated_cost

    total_estimated_cost = validated_price + validated_cost

    if total_estimated_cost == 0.0:
        expected_return_on_cost = 0.0
    else:
        expected_return_on_cost = net_expected_profit / total_estimated_cost

    return ContractEvaluation(
        side=normalized_side,
        belief_yes_probability=validated_yes_probability,
        selected_outcome_probability=selected_outcome_probability,
        contract_price=validated_price,
        estimated_cost=validated_cost,
        gross_expected_profit=gross_expected_profit,
        net_expected_profit=net_expected_profit,
        expected_return_on_cost=expected_return_on_cost,
        classification=classify_expected_profit(net_expected_profit),
    )


def format_dollars(value: float) -> str:
    """Format a per-contract dollar value."""

    return f"${value:,.4f}"


def print_evaluation(evaluation: ContractEvaluation) -> None:
    """Print one evaluation in a readable format."""

    print("=" * 64)
    print(f"Side:                         {evaluation.side}")
    print(
        "Belief YES probability:       "
        f"{evaluation.belief_yes_probability:.2%}"
    )
    print(
        "Selected outcome probability: "
        f"{evaluation.selected_outcome_probability:.2%}"
    )
    print(
        "Contract price:               "
        f"{format_dollars(evaluation.contract_price)}"
    )
    print(
        "Estimated execution cost:     "
        f"{format_dollars(evaluation.estimated_cost)}"
    )
    print(
        "Gross expected profit:        "
        f"{format_dollars(evaluation.gross_expected_profit)}"
    )
    print(
        "Net expected profit:          "
        f"{format_dollars(evaluation.net_expected_profit)}"
    )
    print(
        "Expected return on cost:      "
        f"{evaluation.expected_return_on_cost:.2%}"
    )
    print(f"Classification:               {evaluation.classification}")


def main() -> None:
    """Run two illustrative contract evaluations."""

    yes_example = evaluate_contract(
        belief_yes_probability=0.62,
        side="YES",
        contract_price=0.55,
        estimated_cost=0.01,
    )

    no_example = evaluate_contract(
        belief_yes_probability=0.62,
        side="NO",
        contract_price=0.41,
        estimated_cost=0.01,
    )

    print_evaluation(yes_example)
    print_evaluation(no_example)


if __name__ == "__main__":
    main()
