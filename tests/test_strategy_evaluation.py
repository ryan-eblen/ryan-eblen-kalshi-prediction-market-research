"""Tests for the synthetic strategy-evaluation example."""

import unittest

import numpy as np
import pandas as pd

from examples.strategy_evaluation_example import (
    apply_cost_scenarios,
    build_synthetic_trade_data,
    classify_strategy_segments,
    format_summary_for_display,
    summarize_strategy_costs,
    validate_trade_data,
)


class TestStrategyEvaluation(unittest.TestCase):
    """Verify deterministic data, cost analysis, and classifications."""

    def setUp(self) -> None:
        """Create the standard deterministic synthetic dataset."""

        self.trades = build_synthetic_trade_data(
            observations_per_group=40,
            seed=491,
        )

    def test_synthetic_data_shape_and_columns(self) -> None:
        """The default dataset contains 240 rows and required columns."""

        self.assertEqual(len(self.trades), 240)

        self.assertEqual(
            set(self.trades.columns),
            {
                "trade_id",
                "strategy_id",
                "ticker",
                "side",
                "gross_pnl",
            },
        )

    def test_data_generation_is_deterministic(self) -> None:
        """The same seed and configuration produce identical data."""

        repeated = build_synthetic_trade_data(
            observations_per_group=40,
            seed=491,
        )

        pd.testing.assert_frame_equal(
            self.trades,
            repeated,
        )

    def test_configured_group_means_are_preserved(self) -> None:
        """Centered noise preserves each configured synthetic mean."""

        observed = (
            self.trades.groupby(
                [
                    "strategy_id",
                    "side",
                ]
            )["gross_pnl"]
            .mean()
            .to_dict()
        )

        expected = {
            ("liquidity_filter", "NO"): 0.016,
            ("liquidity_filter", "YES"): -0.003,
            ("mean_reversion", "NO"): 0.011,
            ("mean_reversion", "YES"): 0.018,
            ("momentum_signal", "NO"): 0.007,
            ("momentum_signal", "YES"): 0.014,
        }

        for segment, expected_mean in expected.items():
            self.assertAlmostEqual(
                observed[segment],
                expected_mean,
            )

    def test_observation_count_must_be_at_least_two(self) -> None:
        """A segment needs at least two observations."""

        with self.assertRaises(ValueError):
            build_synthetic_trade_data(
                observations_per_group=1,
            )

    def test_trade_ids_are_unique(self) -> None:
        """Every synthetic trade has a unique identifier."""

        self.assertEqual(
            self.trades["trade_id"].nunique(),
            len(self.trades),
        )

    def test_cost_scenarios_expand_rows(self) -> None:
        """Three cost levels expand 240 rows into 720 rows."""

        cost_frame = apply_cost_scenarios(
            self.trades,
            round_trip_costs=(
                0.0,
                0.01,
                0.02,
            ),
        )

        self.assertEqual(len(cost_frame), 720)
        self.assertEqual(
            sorted(
                cost_frame["round_trip_cost"]
                .unique()
                .tolist()
            ),
            [0.0, 0.01, 0.02],
        )

    def test_net_pnl_subtracts_round_trip_cost(self) -> None:
        """Net P&L equals gross P&L minus the selected cost."""

        cost_frame = apply_cost_scenarios(
            self.trades,
            round_trip_costs=(0.02,),
        )

        expected = (
            cost_frame["gross_pnl"]
            - 0.02
        )

        np.testing.assert_allclose(
            cost_frame["net_pnl"],
            expected,
        )

    def test_empty_cost_scenarios_are_rejected(self) -> None:
        """At least one transaction-cost scenario is required."""

        with self.assertRaises(ValueError):
            apply_cost_scenarios(
                self.trades,
                round_trip_costs=(),
            )

    def test_negative_cost_is_rejected(self) -> None:
        """Transaction-cost assumptions cannot be negative."""

        with self.assertRaises(ValueError):
            apply_cost_scenarios(
                self.trades,
                round_trip_costs=(-0.01,),
            )

    def test_boolean_cost_is_rejected(self) -> None:
        """A Python boolean is not accepted as a numeric cost."""

        with self.assertRaises(TypeError):
            apply_cost_scenarios(
                self.trades,
                round_trip_costs=(True,),
            )

    def test_missing_required_column_is_rejected(self) -> None:
        """The validation layer detects incomplete schemas."""

        invalid_frame = self.trades.drop(
            columns=["gross_pnl"]
        )

        with self.assertRaises(ValueError):
            validate_trade_data(invalid_frame)

    def test_invalid_contract_side_is_rejected(self) -> None:
        """Only YES and NO are valid sides."""

        invalid_frame = self.trades.copy()
        invalid_frame.loc[0, "side"] = "MAYBE"

        with self.assertRaises(ValueError):
            validate_trade_data(invalid_frame)

    def test_nonfinite_pnl_is_rejected(self) -> None:
        """Infinite or nonfinite P&L values are invalid."""

        invalid_frame = self.trades.copy()
        invalid_frame.loc[0, "gross_pnl"] = np.inf

        with self.assertRaises(ValueError):
            validate_trade_data(invalid_frame)

    def test_cost_summary_has_expected_shape(self) -> None:
        """Six segments across three costs produce 18 summary rows."""

        cost_frame = apply_cost_scenarios(
            self.trades
        )

        summary = summarize_strategy_costs(
            cost_frame
        )

        self.assertEqual(len(summary), 18)
        self.assertTrue(
            (summary["observations"] == 40).all()
        )

    def test_default_classification_counts(self) -> None:
        """The deterministic example produces the expected classifications."""

        cost_frame = apply_cost_scenarios(
            self.trades
        )

        summary = summarize_strategy_costs(
            cost_frame
        )

        classifications = classify_strategy_segments(
            summary
        )

        counts = (
            classifications["classification"]
            .value_counts()
            .to_dict()
        )

        self.assertEqual(
            counts,
            {
                "COST_SENSITIVE": 5,
                "NEGATIVE_AT_ALL_COST_LEVELS": 1,
            },
        )

        robust_count = int(
            (
                classifications["classification"]
                == "ROBUST_POSITIVE"
            ).sum()
        )

        self.assertEqual(robust_count, 0)

    def test_insufficient_sample_classification(self) -> None:
        """A segment below the minimum sample is not promoted."""

        summary = pd.DataFrame(
            {
                "strategy_id": ["small_sample"] * 3,
                "ticker": ["KX-TEST"] * 3,
                "side": ["YES"] * 3,
                "round_trip_cost": [
                    0.0,
                    0.01,
                    0.02,
                ],
                "observations": [10, 10, 10],
                "mean_net_pnl": [
                    0.03,
                    0.02,
                    0.01,
                ],
            }
        )

        result = classify_strategy_segments(
            summary,
            minimum_observations=30,
        )

        self.assertEqual(
            result.loc[0, "classification"],
            "INSUFFICIENT_SAMPLE",
        )

    def test_robust_positive_classification(self) -> None:
        """A sufficiently sampled positive segment can be robust positive."""

        summary = pd.DataFrame(
            {
                "strategy_id": ["positive"] * 3,
                "ticker": ["KX-TEST"] * 3,
                "side": ["YES"] * 3,
                "round_trip_cost": [
                    0.0,
                    0.01,
                    0.02,
                ],
                "observations": [40, 40, 40],
                "mean_net_pnl": [
                    0.03,
                    0.02,
                    0.01,
                ],
            }
        )

        result = classify_strategy_segments(
            summary
        )

        self.assertEqual(
            result.loc[0, "classification"],
            "ROBUST_POSITIVE",
        )

    def test_negative_at_all_cost_levels_classification(
        self,
    ) -> None:
        """A nonpositive segment at every cost is classified negative."""

        summary = pd.DataFrame(
            {
                "strategy_id": ["negative"] * 3,
                "ticker": ["KX-TEST"] * 3,
                "side": ["NO"] * 3,
                "round_trip_cost": [
                    0.0,
                    0.01,
                    0.02,
                ],
                "observations": [40, 40, 40],
                "mean_net_pnl": [
                    0.0,
                    -0.01,
                    -0.02,
                ],
            }
        )

        result = classify_strategy_segments(
            summary
        )

        self.assertEqual(
            result.loc[0, "classification"],
            "NEGATIVE_AT_ALL_COST_LEVELS",
        )

    def test_minimum_observations_must_be_positive(self) -> None:
        """The classification sample threshold must exceed zero."""

        cost_frame = apply_cost_scenarios(
            self.trades
        )

        summary = summarize_strategy_costs(
            cost_frame
        )

        with self.assertRaises(ValueError):
            classify_strategy_segments(
                summary,
                minimum_observations=0,
            )

    def test_display_format_rounds_numeric_columns(self) -> None:
        """Display formatting rounds numeric values to four places."""

        frame = pd.DataFrame(
            {
                "label": ["example"],
                "value": [0.123456],
            }
        )

        result = format_summary_for_display(
            frame
        )

        self.assertEqual(
            result.loc[0, "value"],
            0.1235,
        )


if __name__ == "__main__":
    unittest.main()
