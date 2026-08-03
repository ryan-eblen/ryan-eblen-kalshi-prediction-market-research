"""Tests for the sanitized prediction-market expected-value example."""

import unittest

from examples.expected_value_example import (
    classify_expected_profit,
    evaluate_contract,
    normalize_side,
    validate_nonnegative_cost,
    validate_probability,
)


class TestExpectedValueExample(unittest.TestCase):
    """Verify expected-value calculations and defensive validation."""

    def test_positive_yes_contract(self) -> None:
        """A 62% belief at a $0.55 price and $0.01 cost has $0.06 net EV."""

        result = evaluate_contract(
            belief_yes_probability=0.62,
            side="YES",
            contract_price=0.55,
            estimated_cost=0.01,
        )

        self.assertEqual(result.side, "YES")
        self.assertAlmostEqual(result.selected_outcome_probability, 0.62)
        self.assertAlmostEqual(result.gross_expected_profit, 0.07)
        self.assertAlmostEqual(result.net_expected_profit, 0.06)
        self.assertAlmostEqual(
            result.expected_return_on_cost,
            0.06 / 0.56,
        )
        self.assertEqual(
            result.classification,
            "POSITIVE_EXPECTED_VALUE",
        )

    def test_negative_no_contract(self) -> None:
        """A 38% NO belief at a $0.41 price and $0.01 cost has negative EV."""

        result = evaluate_contract(
            belief_yes_probability=0.62,
            side="NO",
            contract_price=0.41,
            estimated_cost=0.01,
        )

        self.assertEqual(result.side, "NO")
        self.assertAlmostEqual(result.selected_outcome_probability, 0.38)
        self.assertAlmostEqual(result.gross_expected_profit, -0.03)
        self.assertAlmostEqual(result.net_expected_profit, -0.04)
        self.assertAlmostEqual(
            result.expected_return_on_cost,
            -0.04 / 0.42,
        )
        self.assertEqual(
            result.classification,
            "NEGATIVE_EXPECTED_VALUE",
        )

    def test_side_is_normalized(self) -> None:
        """Whitespace and lowercase letters are normalized."""

        self.assertEqual(normalize_side(" yes "), "YES")
        self.assertEqual(normalize_side("no"), "NO")

    def test_break_even_contract(self) -> None:
        """A contract with zero net expected profit is classified correctly."""

        result = evaluate_contract(
            belief_yes_probability=0.50,
            side="YES",
            contract_price=0.49,
            estimated_cost=0.01,
        )

        self.assertAlmostEqual(result.net_expected_profit, 0.0)
        self.assertEqual(
            result.classification,
            "BREAK_EVEN_EXPECTED_VALUE",
        )

    def test_zero_total_cost_does_not_divide_by_zero(self) -> None:
        """A zero-price, zero-cost example returns zero instead of failing."""

        result = evaluate_contract(
            belief_yes_probability=0.0,
            side="YES",
            contract_price=0.0,
            estimated_cost=0.0,
        )

        self.assertEqual(result.expected_return_on_cost, 0.0)
        self.assertEqual(
            result.classification,
            "BREAK_EVEN_EXPECTED_VALUE",
        )

    def test_invalid_probability_above_one(self) -> None:
        """Probabilities greater than one are rejected."""

        with self.assertRaises(ValueError):
            validate_probability(1.01, "probability")

    def test_invalid_probability_below_zero(self) -> None:
        """Negative probabilities are rejected."""

        with self.assertRaises(ValueError):
            validate_probability(-0.01, "probability")

    def test_boolean_is_not_accepted_as_probability(self) -> None:
        """Python booleans should not be silently treated as 1 or 0."""

        with self.assertRaises(TypeError):
            validate_probability(True, "probability")

    def test_invalid_side(self) -> None:
        """Only YES and NO are valid contract sides."""

        with self.assertRaises(ValueError):
            normalize_side("MAYBE")

    def test_non_string_side(self) -> None:
        """A non-string contract side is rejected."""

        with self.assertRaises(TypeError):
            normalize_side(1)  # type: ignore[arg-type]

    def test_negative_execution_cost(self) -> None:
        """Estimated execution cost cannot be negative."""

        with self.assertRaises(ValueError):
            validate_nonnegative_cost(-0.01)

    def test_non_numeric_execution_cost(self) -> None:
        """Estimated execution cost must be numeric."""

        with self.assertRaises(TypeError):
            validate_nonnegative_cost("0.01")  # type: ignore[arg-type]

    def test_profit_classification_tolerance(self) -> None:
        """Tiny floating-point differences are treated as break-even."""

        self.assertEqual(
            classify_expected_profit(1e-14),
            "BREAK_EVEN_EXPECTED_VALUE",
        )
        self.assertEqual(
            classify_expected_profit(-1e-14),
            "BREAK_EVEN_EXPECTED_VALUE",
        )


if __name__ == "__main__":
    unittest.main()
