"""Deterministic strategy-evaluation example using synthetic data.

This module demonstrates a simplified cost-aware research workflow with
pandas and NumPy. It does not contain production data, private strategy
parameters, live account information, or exchange credentials.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "trade_id",
    "strategy_id",
    "ticker",
    "side",
    "gross_pnl",
}


@dataclass(frozen=True)
class StrategySpec:
    """Synthetic strategy segment used to generate example observations."""

    strategy_id: str
    ticker: str
    side: str
    mean_gross_pnl: float


def build_synthetic_trade_data(
    *,
    observations_per_group: int = 40,
    seed: int = 491,
) -> pd.DataFrame:
    """Create deterministic synthetic trade outcomes.

    Random noise is centered within each strategy segment so the observed
    sample mean matches the configured synthetic mean exactly.
    """

    if observations_per_group < 2:
        raise ValueError("observations_per_group must be at least 2.")

    specs = [
        StrategySpec("momentum_signal", "KX-RATE", "YES", 0.014),
        StrategySpec("momentum_signal", "KX-RATE", "NO", 0.007),
        StrategySpec(
            "mean_reversion",
            "KX-INFLATION",
            "YES",
            0.018,
        ),
        StrategySpec(
            "mean_reversion",
            "KX-INFLATION",
            "NO",
            0.011,
        ),
        StrategySpec(
            "liquidity_filter",
            "KX-ECONOMY",
            "YES",
            -0.003,
        ),
        StrategySpec(
            "liquidity_filter",
            "KX-ECONOMY",
            "NO",
            0.016,
        ),
    ]

    rng = np.random.default_rng(seed)
    records: list[dict[str, object]] = []

    for spec in specs:
        noise = rng.normal(
            loc=0.0,
            scale=0.025,
            size=observations_per_group,
        )

        centered_noise = noise - noise.mean()
        gross_outcomes = spec.mean_gross_pnl + centered_noise

        for observation_number, gross_pnl in enumerate(
            gross_outcomes,
            start=1,
        ):
            records.append(
                {
                    "trade_id": (
                        f"{spec.strategy_id}-{spec.side}-"
                        f"{observation_number:03d}"
                    ),
                    "strategy_id": spec.strategy_id,
                    "ticker": spec.ticker,
                    "side": spec.side,
                    "gross_pnl": float(gross_pnl),
                }
            )

    frame = pd.DataFrame.from_records(records)
    validate_trade_data(frame)
    return frame


def validate_trade_data(frame: pd.DataFrame) -> None:
    """Validate the schema and basic values of the synthetic trade data."""

    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_text}")

    if frame.empty:
        raise ValueError("Trade data cannot be empty.")

    if frame["trade_id"].duplicated().any():
        raise ValueError("trade_id values must be unique.")

    invalid_sides = set(
        frame["side"].dropna().unique()
    ).difference({"YES", "NO"})

    if invalid_sides:
        raise ValueError(
            f"Invalid contract sides: {sorted(invalid_sides)}"
        )

    if frame["gross_pnl"].isna().any():
        raise ValueError("gross_pnl cannot contain missing values.")

    gross_values = frame["gross_pnl"].to_numpy(dtype=float)

    if not np.isfinite(gross_values).all():
        raise ValueError(
            "gross_pnl must contain only finite values."
        )


def apply_cost_scenarios(
    frame: pd.DataFrame,
    *,
    round_trip_costs: tuple[float, ...] = (
        0.0,
        0.01,
        0.02,
    ),
) -> pd.DataFrame:
    """Expand each trade across explicit round-trip cost scenarios."""

    validate_trade_data(frame)

    if not round_trip_costs:
        raise ValueError("At least one cost scenario is required.")

    scenario_frames: list[pd.DataFrame] = []

    for cost in round_trip_costs:
        if isinstance(cost, bool) or not isinstance(
            cost,
            (int, float),
        ):
            raise TypeError(
                "Each round-trip cost must be numeric."
            )

        normalized_cost = float(cost)

        if normalized_cost < 0.0:
            raise ValueError(
                "Round-trip costs cannot be negative."
            )

        scenario = frame.copy()
        scenario["round_trip_cost"] = normalized_cost
        scenario["net_pnl"] = (
            scenario["gross_pnl"]
            - scenario["round_trip_cost"]
        )
        scenario_frames.append(scenario)

    return pd.concat(
        scenario_frames,
        ignore_index=True,
    )


def summarize_strategy_costs(
    cost_frame: pd.DataFrame,
) -> pd.DataFrame:
    """Aggregate each strategy segment at each cost level."""

    required = REQUIRED_COLUMNS.union(
        {
            "round_trip_cost",
            "net_pnl",
        }
    )

    missing_columns = required.difference(
        cost_frame.columns
    )

    if missing_columns:
        missing_text = ", ".join(
            sorted(missing_columns)
        )
        raise ValueError(
            f"Missing required columns: {missing_text}"
        )

    summary = (
        cost_frame.groupby(
            [
                "strategy_id",
                "ticker",
                "side",
                "round_trip_cost",
            ],
            as_index=False,
        )
        .agg(
            observations=("trade_id", "count"),
            mean_gross_pnl=("gross_pnl", "mean"),
            mean_net_pnl=("net_pnl", "mean"),
            median_net_pnl=("net_pnl", "median"),
            positive_net_rate=(
                "net_pnl",
                lambda values: (values > 0).mean(),
            ),
        )
        .sort_values(
            [
                "strategy_id",
                "side",
                "round_trip_cost",
            ],
            ignore_index=True,
        )
    )

    return summary


def classify_strategy_segments(
    summary: pd.DataFrame,
    *,
    minimum_observations: int = 30,
) -> pd.DataFrame:
    """Classify performance across all tested cost levels."""

    if minimum_observations <= 0:
        raise ValueError(
            "minimum_observations must be positive."
        )

    records: list[dict[str, object]] = []

    grouped = summary.groupby(
        [
            "strategy_id",
            "ticker",
            "side",
        ],
        sort=True,
    )

    for keys, group in grouped:
        strategy_id, ticker, side = keys

        minimum_sample = int(
            group["observations"].min()
        )

        means = group["mean_net_pnl"].to_numpy(
            dtype=float
        )

        if minimum_sample < minimum_observations:
            classification = "INSUFFICIENT_SAMPLE"
        elif np.all(means > 0.0):
            classification = "ROBUST_POSITIVE"
        elif np.all(means <= 0.0):
            classification = (
                "NEGATIVE_AT_ALL_COST_LEVELS"
            )
        else:
            classification = "COST_SENSITIVE"

        records.append(
            {
                "strategy_id": strategy_id,
                "ticker": ticker,
                "side": side,
                "minimum_observations": minimum_sample,
                "best_mean_net_pnl": float(means.max()),
                "worst_mean_net_pnl": float(means.min()),
                "classification": classification,
            }
        )

    return pd.DataFrame.from_records(
        records
    ).sort_values(
        [
            "strategy_id",
            "side",
        ],
        ignore_index=True,
    )


def format_summary_for_display(
    frame: pd.DataFrame,
) -> pd.DataFrame:
    """Return a rounded copy suitable for console display."""

    display_frame = frame.copy()

    numeric_columns = display_frame.select_dtypes(
        include=[np.number]
    ).columns

    display_frame[numeric_columns] = display_frame[
        numeric_columns
    ].round(4)

    return display_frame


def main() -> None:
    """Run the complete synthetic strategy-evaluation workflow."""

    trades = build_synthetic_trade_data()

    cost_frame = apply_cost_scenarios(
        trades
    )

    summary = summarize_strategy_costs(
        cost_frame
    )

    classifications = classify_strategy_segments(
        summary
    )

    print("=" * 78)
    print(
        "Synthetic Prediction-Market Strategy Evaluation"
    )
    print("=" * 78)
    print(
        f"Synthetic trade rows:       {len(trades)}"
    )
    print(
        f"Cost-adjusted rows:         {len(cost_frame)}"
    )
    print(
        "Strategy-side segments:     "
        f"{len(classifications)}"
    )
    print()

    print("Cost-level summary:")
    print(
        format_summary_for_display(
            summary
        ).to_string(index=False)
    )
    print()

    print("Cross-cost classifications:")
    print(
        format_summary_for_display(
            classifications
        ).to_string(index=False)
    )
    print()

    print("Classification counts:")
    print(
        classifications["classification"]
        .value_counts()
        .sort_index()
        .to_string()
    )

    robust_count = int(
        (
            classifications["classification"]
            == "ROBUST_POSITIVE"
        ).sum()
    )

    print()
    print(
        f"Robust-positive segments:   {robust_count}"
    )
    print(
        "Interpretation: pre-cost strength does not "
        "guarantee post-cost robustness."
    )


if __name__ == "__main__":
    main()
