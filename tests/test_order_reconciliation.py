"""Tests for the sanitized order-reconciliation example."""

import unittest

from examples.order_reconciliation_example import (
    ExchangeOrderSnapshot,
    OrderState,
    PositionState,
    determine_internal_status,
    reconcile_order,
    validate_nonnegative_integer,
    validate_positive_integer,
)


class TestOrderReconciliation(unittest.TestCase):
    """Verify fill processing, idempotency, and defensive validation."""

    def setUp(self) -> None:
        """Create a standard order and empty position for each test."""

        self.order = OrderState(
            order_id="test-order-001",
            ticker="TEST-MARKET",
            side="YES",
            requested_quantity=5,
        )

        self.position = PositionState(
            ticker="TEST-MARKET",
            side="YES",
        )

    def test_partial_fill_creates_position(self) -> None:
        """The first partial fill creates a position for the new quantity."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=2,
            status="PARTIALLY_FILLED",
        )

        result = reconcile_order(
            order=self.order,
            position=self.position,
            snapshot=snapshot,
        )

        self.assertEqual(result.newly_filled_quantity, 2)
        self.assertEqual(result.position.quantity, 2)
        self.assertEqual(result.order.processed_filled_quantity, 2)
        self.assertEqual(result.order.status, "PARTIALLY_FILLED")
        self.assertEqual(result.action, "POSITION_CREATED")

    def test_repeated_snapshot_is_idempotent(self) -> None:
        """Processing the same cumulative fill twice does not duplicate it."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=2,
            status="PARTIALLY_FILLED",
        )

        first_result = reconcile_order(
            order=self.order,
            position=self.position,
            snapshot=snapshot,
        )

        repeated_result = reconcile_order(
            order=first_result.order,
            position=first_result.position,
            snapshot=snapshot,
        )

        self.assertEqual(repeated_result.newly_filled_quantity, 0)
        self.assertEqual(repeated_result.position.quantity, 2)
        self.assertEqual(
            repeated_result.order.processed_filled_quantity,
            2,
        )
        self.assertEqual(repeated_result.action, "NO_NEW_FILL")

    def test_final_fill_adds_only_incremental_quantity(self) -> None:
        """A final cumulative fill adds only the unprocessed difference."""

        partial_snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=2,
            status="PARTIALLY_FILLED",
        )

        partial_result = reconcile_order(
            order=self.order,
            position=self.position,
            snapshot=partial_snapshot,
        )

        final_snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=5,
            status="FILLED",
        )

        final_result = reconcile_order(
            order=partial_result.order,
            position=partial_result.position,
            snapshot=final_snapshot,
        )

        self.assertEqual(final_result.newly_filled_quantity, 3)
        self.assertEqual(final_result.position.quantity, 5)
        self.assertEqual(
            final_result.order.processed_filled_quantity,
            5,
        )
        self.assertEqual(final_result.order.status, "FILLED")
        self.assertEqual(final_result.action, "POSITION_INCREASED")

    def test_full_fill_from_zero_creates_position(self) -> None:
        """An immediately full order creates the complete position."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=5,
            status="FILLED",
        )

        result = reconcile_order(
            order=self.order,
            position=self.position,
            snapshot=snapshot,
        )

        self.assertEqual(result.newly_filled_quantity, 5)
        self.assertEqual(result.position.quantity, 5)
        self.assertEqual(result.order.status, "FILLED")
        self.assertEqual(result.action, "POSITION_CREATED")

    def test_unfilled_open_order_becomes_acked(self) -> None:
        """An open order with no fill is internally acknowledged."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=0,
            status="OPEN",
        )

        result = reconcile_order(
            order=self.order,
            position=self.position,
            snapshot=snapshot,
        )

        self.assertEqual(result.newly_filled_quantity, 0)
        self.assertEqual(result.position.quantity, 0)
        self.assertEqual(result.order.status, "ACKED")
        self.assertEqual(result.action, "NO_NEW_FILL")

    def test_unfilled_canceled_order_remains_without_position(self) -> None:
        """A canceled order with no fill does not create a position."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=0,
            status="CANCELED",
        )

        result = reconcile_order(
            order=self.order,
            position=self.position,
            snapshot=snapshot,
        )

        self.assertEqual(result.newly_filled_quantity, 0)
        self.assertEqual(result.position.quantity, 0)
        self.assertEqual(result.order.status, "CANCELED")
        self.assertEqual(result.action, "NO_NEW_FILL")

    def test_canceled_order_can_preserve_partial_fill(self) -> None:
        """A canceled remainder can still contain an executed partial fill."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=2,
            status="CANCELED",
        )

        result = reconcile_order(
            order=self.order,
            position=self.position,
            snapshot=snapshot,
        )

        self.assertEqual(result.newly_filled_quantity, 2)
        self.assertEqual(result.position.quantity, 2)
        self.assertEqual(result.order.status, "CANCELED")
        self.assertEqual(result.action, "POSITION_CREATED")

    def test_open_snapshot_with_fill_is_partial(self) -> None:
        """A positive cumulative fill is partial until quantity is complete."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=2,
            status="OPEN",
        )

        status = determine_internal_status(
            snapshot,
            requested_quantity=5,
        )

        self.assertEqual(status, "PARTIALLY_FILLED")

    def test_exchange_order_id_must_match(self) -> None:
        """A snapshot for another exchange order is rejected."""

        snapshot = ExchangeOrderSnapshot(
            order_id="different-order",
            cumulative_filled_quantity=1,
            status="PARTIALLY_FILLED",
        )

        with self.assertRaises(ValueError):
            reconcile_order(
                order=self.order,
                position=self.position,
                snapshot=snapshot,
            )

    def test_exchange_fill_cannot_exceed_requested_quantity(self) -> None:
        """An impossible cumulative fill is rejected."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=6,
            status="FILLED",
        )

        with self.assertRaises(ValueError):
            reconcile_order(
                order=self.order,
                position=self.position,
                snapshot=snapshot,
            )

    def test_exchange_fill_cannot_move_backward(self) -> None:
        """A cumulative exchange quantity cannot decrease."""

        partially_processed_order = OrderState(
            order_id="test-order-001",
            ticker="TEST-MARKET",
            side="YES",
            requested_quantity=5,
            processed_filled_quantity=3,
            status="PARTIALLY_FILLED",
        )

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=2,
            status="PARTIALLY_FILLED",
        )

        with self.assertRaises(ValueError):
            reconcile_order(
                order=partially_processed_order,
                position=PositionState(
                    ticker="TEST-MARKET",
                    side="YES",
                    quantity=3,
                ),
                snapshot=snapshot,
            )

    def test_filled_status_requires_complete_quantity(self) -> None:
        """A FILLED exchange status cannot report an incomplete quantity."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=4,
            status="FILLED",
        )

        with self.assertRaises(ValueError):
            reconcile_order(
                order=self.order,
                position=self.position,
                snapshot=snapshot,
            )

    def test_position_ticker_must_match_order(self) -> None:
        """A position from a different market cannot receive the fill."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=1,
            status="PARTIALLY_FILLED",
        )

        invalid_position = PositionState(
            ticker="OTHER-MARKET",
            side="YES",
        )

        with self.assertRaises(ValueError):
            reconcile_order(
                order=self.order,
                position=invalid_position,
                snapshot=snapshot,
            )

    def test_position_side_must_match_order(self) -> None:
        """A position on the opposite side cannot receive the fill."""

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=1,
            status="PARTIALLY_FILLED",
        )

        invalid_position = PositionState(
            ticker="TEST-MARKET",
            side="NO",
        )

        with self.assertRaises(ValueError):
            reconcile_order(
                order=self.order,
                position=invalid_position,
                snapshot=snapshot,
            )

    def test_processed_quantity_cannot_exceed_requested_quantity(self) -> None:
        """Corrupt internal order state is rejected before reconciliation."""

        invalid_order = OrderState(
            order_id="test-order-001",
            ticker="TEST-MARKET",
            side="YES",
            requested_quantity=5,
            processed_filled_quantity=6,
            status="FILLED",
        )

        snapshot = ExchangeOrderSnapshot(
            order_id="test-order-001",
            cumulative_filled_quantity=5,
            status="FILLED",
        )

        with self.assertRaises(ValueError):
            reconcile_order(
                order=invalid_order,
                position=self.position,
                snapshot=snapshot,
            )

    def test_positive_integer_rejects_boolean(self) -> None:
        """A Python boolean is not accepted as an order quantity."""

        with self.assertRaises(TypeError):
            validate_positive_integer(True, "quantity")

    def test_nonnegative_integer_rejects_negative_value(self) -> None:
        """Negative cumulative quantities are rejected."""

        with self.assertRaises(ValueError):
            validate_nonnegative_integer(-1, "quantity")


if __name__ == "__main__":
    unittest.main()
