"""Tests for the sanitized execution-funnel diagnostic."""

import unittest

from examples.execution_funnel_example import (
    ExecutionEvent,
    analyze_execution_funnel,
    build_synthetic_events,
    safe_rate,
    validate_event,
)


class TestExecutionFunnel(unittest.TestCase):
    """Verify funnel counts, conversion rates, and lifecycle validation."""

    def setUp(self) -> None:
        """Create the standard deterministic synthetic event stream."""

        self.events = build_synthetic_events()

    def test_synthetic_event_count(self) -> None:
        """The example contains 29 lifecycle events."""

        self.assertEqual(len(self.events), 29)

    def test_default_funnel_counts(self) -> None:
        """The example produces the expected lifecycle counts."""

        metrics = analyze_execution_funnel(self.events)

        self.assertEqual(metrics.submitted_orders, 20)
        self.assertEqual(metrics.executed_orders, 5)
        self.assertEqual(metrics.hydrated_positions, 3)

    def test_default_conversion_rates(self) -> None:
        """The example produces the expected conversion rates."""

        metrics = analyze_execution_funnel(self.events)

        self.assertAlmostEqual(
            metrics.execution_rate,
            0.25,
        )
        self.assertAlmostEqual(
            metrics.hydration_rate,
            0.60,
        )
        self.assertAlmostEqual(
            metrics.end_to_end_conversion_rate,
            0.15,
        )

    def test_executed_not_hydrated_orders_are_identified(
        self,
    ) -> None:
        """Executed orders without internal positions are reported."""

        metrics = analyze_execution_funnel(self.events)

        self.assertEqual(
            metrics.executed_not_hydrated,
            (
                "order-004",
                "order-005",
            ),
        )

    def test_duplicate_execution_event_is_reported(self) -> None:
        """The repeated execution event appears in diagnostics."""

        metrics = analyze_execution_funnel(self.events)

        self.assertEqual(
            metrics.duplicate_events,
            ("order-001:ORDER_EXECUTED",),
        )

    def test_duplicate_event_does_not_increase_counts(self) -> None:
        """A duplicate lifecycle event is not counted twice."""

        metrics = analyze_execution_funnel(self.events)

        self.assertEqual(metrics.executed_orders, 5)
        self.assertEqual(metrics.hydrated_positions, 3)

    def test_empty_event_stream_returns_zero_metrics(self) -> None:
        """An empty stream produces safe zero-valued metrics."""

        metrics = analyze_execution_funnel(())

        self.assertEqual(metrics.submitted_orders, 0)
        self.assertEqual(metrics.executed_orders, 0)
        self.assertEqual(metrics.hydrated_positions, 0)
        self.assertEqual(metrics.execution_rate, 0.0)
        self.assertEqual(metrics.hydration_rate, 0.0)
        self.assertEqual(
            metrics.end_to_end_conversion_rate,
            0.0,
        )
        self.assertEqual(metrics.executed_not_hydrated, ())
        self.assertEqual(metrics.duplicate_events, ())

    def test_safe_rate_handles_zero_denominator(self) -> None:
        """A zero denominator does not raise an exception."""

        self.assertEqual(safe_rate(5, 0), 0.0)

    def test_safe_rate_calculates_normal_ratio(self) -> None:
        """A normal numerator and denominator produce a ratio."""

        self.assertAlmostEqual(
            safe_rate(1, 4),
            0.25,
        )

    def test_execution_requires_submission(self) -> None:
        """An execution without a submission event is invalid."""

        events = (
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_EXECUTED",
            ),
        )

        with self.assertRaises(ValueError):
            analyze_execution_funnel(events)

    def test_hydration_requires_execution(self) -> None:
        """A hydrated position requires a prior execution event."""

        events = (
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_SUBMITTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="POSITION_HYDRATED",
            ),
        )

        with self.assertRaises(ValueError):
            analyze_execution_funnel(events)

    def test_empty_order_id_is_rejected(self) -> None:
        """Every event must contain an order identifier."""

        event = ExecutionEvent(
            order_id="   ",
            trade_id="trade-001",
            event_type="ORDER_SUBMITTED",
        )

        with self.assertRaises(ValueError):
            validate_event(event)

    def test_nonstring_order_id_is_rejected(self) -> None:
        """An order identifier must be text."""

        event = ExecutionEvent(
            order_id=123,  # type: ignore[arg-type]
            trade_id="trade-001",
            event_type="ORDER_SUBMITTED",
        )

        with self.assertRaises(TypeError):
            validate_event(event)

    def test_empty_trade_id_is_rejected(self) -> None:
        """Every event must contain a trade identifier."""

        event = ExecutionEvent(
            order_id="order-001",
            trade_id="",
            event_type="ORDER_SUBMITTED",
        )

        with self.assertRaises(ValueError):
            validate_event(event)

    def test_invalid_event_type_is_rejected(self) -> None:
        """Unsupported lifecycle event types are rejected."""

        event = ExecutionEvent(
            order_id="order-001",
            trade_id="trade-001",
            event_type="UNKNOWN",  # type: ignore[arg-type]
        )

        with self.assertRaises(ValueError):
            validate_event(event)

    def test_complete_funnel_has_full_conversion(self) -> None:
        """A fully hydrated order produces 100% conversion."""

        events = (
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_SUBMITTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_EXECUTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="POSITION_HYDRATED",
            ),
        )

        metrics = analyze_execution_funnel(events)

        self.assertEqual(metrics.execution_rate, 1.0)
        self.assertEqual(metrics.hydration_rate, 1.0)
        self.assertEqual(
            metrics.end_to_end_conversion_rate,
            1.0,
        )

    def test_complete_funnel_has_no_hydration_gap(self) -> None:
        """A fully hydrated order has no unresolved execution."""

        events = (
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_SUBMITTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_EXECUTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="POSITION_HYDRATED",
            ),
        )

        metrics = analyze_execution_funnel(events)

        self.assertEqual(
            metrics.executed_not_hydrated,
            (),
        )

    def test_duplicate_submission_is_ignored(self) -> None:
        """Repeated submission events do not inflate order counts."""

        events = (
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_SUBMITTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_SUBMITTED",
            ),
        )

        metrics = analyze_execution_funnel(events)

        self.assertEqual(metrics.submitted_orders, 1)
        self.assertEqual(
            metrics.duplicate_events,
            ("order-001:ORDER_SUBMITTED",),
        )

    def test_duplicate_hydration_is_ignored(self) -> None:
        """Repeated hydration events do not create extra positions."""

        events = (
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_SUBMITTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_EXECUTED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="POSITION_HYDRATED",
            ),
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="POSITION_HYDRATED",
            ),
        )

        metrics = analyze_execution_funnel(events)

        self.assertEqual(metrics.hydrated_positions, 1)
        self.assertEqual(
            metrics.duplicate_events,
            ("order-001:POSITION_HYDRATED",),
        )

    def test_submitted_only_orders_have_zero_execution_rate(
        self,
    ) -> None:
        """Submitted orders without fills produce zero conversion."""

        events = (
            ExecutionEvent(
                order_id="order-001",
                trade_id="trade-001",
                event_type="ORDER_SUBMITTED",
            ),
            ExecutionEvent(
                order_id="order-002",
                trade_id="trade-002",
                event_type="ORDER_SUBMITTED",
            ),
        )

        metrics = analyze_execution_funnel(events)

        self.assertEqual(metrics.submitted_orders, 2)
        self.assertEqual(metrics.executed_orders, 0)
        self.assertEqual(metrics.hydrated_positions, 0)
        self.assertEqual(metrics.execution_rate, 0.0)
        self.assertEqual(metrics.hydration_rate, 0.0)
        self.assertEqual(
            metrics.end_to_end_conversion_rate,
            0.0,
        )


if __name__ == "__main__":
    unittest.main()
