"""Tests for the sanitized pre-trade risk-control example."""

import unittest
from dataclasses import replace

from examples.risk_controls_example import (
    OpenPosition,
    ProposedOrder,
    build_example_limits,
    build_example_snapshot,
    calculate_current_gross_exposure,
    evaluate_order_risk,
)


class TestRiskControls(unittest.TestCase):
    """Verify approvals, rejections, calculations, and validation."""

    def setUp(self) -> None:
        """Create standard synthetic risk state."""

        self.snapshot = build_example_snapshot()
        self.limits = build_example_limits()

        self.approved_order = ProposedOrder(
            order_id="order-approved",
            ticker="KX-RATE",
            side=" yes ",
            quantity=3,
            price=0.40,
            estimated_cost_per_contract=0.01,
        )

    def test_approved_order_passes_all_checks(self) -> None:
        result = evaluate_order_risk(
            order=self.approved_order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertEqual(result.decision, "APPROVE")
        self.assertEqual(result.failed_check_names, ())
        self.assertTrue(all(check.passed for check in result.checks))

    def test_order_side_is_normalized(self) -> None:
        result = evaluate_order_risk(
            order=self.approved_order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertEqual(result.normalized_side, "YES")

    def test_exposure_limit_rejects_order(self) -> None:
        order = ProposedOrder(
            order_id="order-exposure",
            ticker="KX-ECONOMY",
            side="YES",
            quantity=10,
            price=0.50,
            estimated_cost_per_contract=0.01,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertEqual(result.decision, "REJECT")
        self.assertIn(
            "MAX_GROSS_EXPOSURE",
            result.failed_check_names,
        )

    def test_duplicate_order_id_is_rejected(self) -> None:
        order = ProposedOrder(
            order_id="order-previous",
            ticker="KX-RATE",
            side="YES",
            quantity=1,
            price=0.40,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertIn(
            "UNIQUE_ORDER_ID",
            result.failed_check_names,
        )

    def test_daily_loss_at_limit_rejects_order(self) -> None:
        stopped_snapshot = replace(
            self.snapshot,
            realized_pnl=-1.50,
        )

        order = ProposedOrder(
            order_id="order-loss-stop",
            ticker="KX-RATE",
            side="YES",
            quantity=1,
            price=0.40,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=stopped_snapshot,
            limits=self.limits,
        )

        self.assertEqual(result.decision, "REJECT")
        self.assertIn(
            "MAX_DAILY_LOSS",
            result.failed_check_names,
        )

    def test_maximum_order_quantity_is_enforced(self) -> None:
        limits = replace(
            self.limits,
            max_ticker_quantity=100,
            max_gross_exposure=100.0,
        )

        order = ProposedOrder(
            order_id="order-too-large",
            ticker="KX-RATE",
            side="YES",
            quantity=11,
            price=0.10,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=limits,
        )

        self.assertIn(
            "MAX_ORDER_QUANTITY",
            result.failed_check_names,
        )

    def test_maximum_ticker_quantity_is_enforced(self) -> None:
        order = ProposedOrder(
            order_id="order-ticker-limit",
            ticker="KX-RATE",
            side="YES",
            quantity=9,
            price=0.10,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertEqual(result.projected_ticker_quantity, 13)
        self.assertIn(
            "MAX_TICKER_QUANTITY",
            result.failed_check_names,
        )

    def test_maximum_open_positions_is_enforced(self) -> None:
        limits = replace(
            self.limits,
            max_open_positions=2,
        )

        order = ProposedOrder(
            order_id="order-new-position",
            ticker="KX-ECONOMY",
            side="YES",
            quantity=1,
            price=0.10,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=limits,
        )

        self.assertEqual(result.projected_open_positions, 3)
        self.assertIn(
            "MAX_OPEN_POSITIONS",
            result.failed_check_names,
        )

    def test_disallowed_side_is_rejected(self) -> None:
        limits = replace(
            self.limits,
            allowed_sides=("YES",),
        )

        order = ProposedOrder(
            order_id="order-no-side",
            ticker="KX-RATE",
            side="NO",
            quantity=1,
            price=0.40,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=limits,
        )

        self.assertIn(
            "ALLOWED_SIDE",
            result.failed_check_names,
        )

    def test_matching_position_does_not_increase_count(self) -> None:
        result = evaluate_order_risk(
            order=self.approved_order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertEqual(result.projected_open_positions, 2)

    def test_opposite_side_creates_separate_position(self) -> None:
        order = ProposedOrder(
            order_id="order-opposite-side",
            ticker="KX-RATE",
            side="NO",
            quantity=1,
            price=0.40,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertEqual(result.projected_open_positions, 3)

    def test_current_gross_exposure_calculation(self) -> None:
        exposure = calculate_current_gross_exposure(
            self.snapshot.open_positions
        )

        self.assertAlmostEqual(exposure, 3.60)

    def test_projected_exposure_includes_estimated_cost(self) -> None:
        result = evaluate_order_risk(
            order=self.approved_order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertAlmostEqual(
            result.projected_gross_exposure,
            4.83,
        )

    def test_price_above_one_is_rejected(self) -> None:
        order = replace(
            self.approved_order,
            price=1.01,
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=order,
                snapshot=self.snapshot,
                limits=self.limits,
            )

    def test_negative_estimated_cost_is_rejected(self) -> None:
        order = replace(
            self.approved_order,
            estimated_cost_per_contract=-0.01,
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=order,
                snapshot=self.snapshot,
                limits=self.limits,
            )

    def test_boolean_quantity_is_rejected(self) -> None:
        order = replace(
            self.approved_order,
            quantity=True,
        )

        with self.assertRaises(TypeError):
            evaluate_order_risk(
                order=order,
                snapshot=self.snapshot,
                limits=self.limits,
            )

    def test_invalid_configured_side_is_rejected(self) -> None:
        limits = replace(
            self.limits,
            allowed_sides=("MAYBE",),
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=self.approved_order,
                snapshot=self.snapshot,
                limits=limits,
            )

    def test_duplicate_allowed_sides_are_rejected(self) -> None:
        limits = replace(
            self.limits,
            allowed_sides=("YES", " yes "),
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=self.approved_order,
                snapshot=self.snapshot,
                limits=limits,
            )

    def test_duplicate_position_ids_are_rejected(self) -> None:
        duplicate_position = OpenPosition(
            position_id="position-001",
            ticker="KX-ECONOMY",
            side="YES",
            quantity=1,
            entry_price=0.20,
        )

        snapshot = replace(
            self.snapshot,
            open_positions=(
                *self.snapshot.open_positions,
                duplicate_position,
            ),
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=self.approved_order,
                snapshot=snapshot,
                limits=self.limits,
            )

    def test_duplicate_processed_order_ids_are_rejected(self) -> None:
        snapshot = replace(
            self.snapshot,
            processed_order_ids=("order-a", "order-a"),
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=self.approved_order,
                snapshot=snapshot,
                limits=self.limits,
            )

    def test_processed_order_whitespace_is_normalized(self) -> None:
        snapshot = replace(
            self.snapshot,
            processed_order_ids=(" order-approved ",),
        )

        result = evaluate_order_risk(
            order=self.approved_order,
            snapshot=snapshot,
            limits=self.limits,
        )

        self.assertIn(
            "UNIQUE_ORDER_ID",
            result.failed_check_names,
        )

    def test_failed_check_names_contains_only_failures(self) -> None:
        order = ProposedOrder(
            order_id="order-exposure",
            ticker="KX-ECONOMY",
            side="YES",
            quantity=10,
            price=0.50,
            estimated_cost_per_contract=0.01,
        )

        result = evaluate_order_risk(
            order=order,
            snapshot=self.snapshot,
            limits=self.limits,
        )

        self.assertEqual(
            result.failed_check_names,
            ("MAX_GROSS_EXPOSURE",),
        )

    def test_zero_daily_loss_passes_positive_limit(self) -> None:
        snapshot = replace(
            self.snapshot,
            realized_pnl=0.0,
        )

        result = evaluate_order_risk(
            order=self.approved_order,
            snapshot=snapshot,
            limits=self.limits,
        )

        self.assertNotIn(
            "MAX_DAILY_LOSS",
            result.failed_check_names,
        )

    def test_nonfinite_realized_pnl_is_rejected(self) -> None:
        snapshot = replace(
            self.snapshot,
            realized_pnl=float("inf"),
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=self.approved_order,
                snapshot=snapshot,
                limits=self.limits,
            )

    def test_empty_order_id_is_rejected(self) -> None:
        order = replace(
            self.approved_order,
            order_id="   ",
        )

        with self.assertRaises(ValueError):
            evaluate_order_risk(
                order=order,
                snapshot=self.snapshot,
                limits=self.limits,
            )


if __name__ == "__main__":
    unittest.main()
