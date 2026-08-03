"""Sanitized prediction-market data-validation example.

This standalone module demonstrates schema validation, normalization, issue
reporting, and rejection of malformed research records.

It uses synthetic data only and contains no private account information,
production records, credentials, or proprietary strategy logic.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = {
    "decision_id",
    "timestamp_utc",
    "ticker",
    "side",
    "yes_price",
    "model_probability_yes",
    "realized_pnl",
}


@dataclass(frozen=True)
class ValidationIssue:
    """One problem discovered in a synthetic decision record."""

    row_number: int
    decision_id: str
    field: str
    code: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """Summary of one validation run."""

    total_rows: int
    valid_rows: int
    invalid_rows: int
    issue_count: int
    issues: tuple[ValidationIssue, ...]
    cleaned_data: pd.DataFrame


def build_synthetic_decision_data() -> pd.DataFrame:
    """Build deterministic records containing valid and invalid examples."""

    records = [
        {
            "decision_id": "decision-001",
            "timestamp_utc": "2026-01-05T14:30:00Z",
            "ticker": "KX-RATE",
            "side": "YES",
            "yes_price": 0.42,
            "model_probability_yes": 0.55,
            "realized_pnl": 0.08,
        },
        {
            "decision_id": "decision-002",
            "timestamp_utc": "2026-01-05T14:30:01Z",
            "ticker": "KX-RATE",
            "side": "NO",
            "yes_price": 0.63,
            "model_probability_yes": 0.48,
            "realized_pnl": -0.03,
        },
        {
            "decision_id": "decision-003",
            "timestamp_utc": "2026-01-05T14:30:02Z",
            "ticker": "kx-inflation",
            "side": " yes ",
            "yes_price": 0.37,
            "model_probability_yes": 0.51,
            "realized_pnl": 0.02,
        },
        {
            "decision_id": "decision-004",
            "timestamp_utc": "2026-01-05T14:30:03Z",
            "ticker": "KX-ECONOMY",
            "side": "NO",
            "yes_price": 0.71,
            "model_probability_yes": 0.66,
            "realized_pnl": -0.01,
        },
        {
            "decision_id": "decision-005",
            "timestamp_utc": "2026-01-05T14:30:04Z",
            "ticker": "KX-ECONOMY",
            "side": "YES",
            "yes_price": 0.28,
            "model_probability_yes": 0.39,
            "realized_pnl": 0.05,
        },
        {
            "decision_id": "decision-006",
            "timestamp_utc": "2026-01-05T14:30:05Z",
            "ticker": "KX-RATE",
            "side": "YES",
            "yes_price": 0.51,
            "model_probability_yes": 0.57,
            "realized_pnl": 0.01,
        },
        {
            "decision_id": "decision-006",
            "timestamp_utc": "2026-01-05T14:30:06Z",
            "ticker": "KX-RATE",
            "side": "YES",
            "yes_price": 0.52,
            "model_probability_yes": 0.58,
            "realized_pnl": 0.02,
        },
        {
            "decision_id": "decision-008",
            "timestamp_utc": "2026-01-05T14:30:07Z",
            "ticker": "KX-INFLATION",
            "side": "MAYBE",
            "yes_price": 0.46,
            "model_probability_yes": 0.49,
            "realized_pnl": 0.00,
        },
        {
            "decision_id": "decision-009",
            "timestamp_utc": "2026-01-05T14:30:08Z",
            "ticker": "KX-INFLATION",
            "side": "NO",
            "yes_price": 1.20,
            "model_probability_yes": 0.44,
            "realized_pnl": -0.02,
        },
        {
            "decision_id": "decision-010",
            "timestamp_utc": "2026-01-05T14:30:09Z",
            "ticker": "KX-ECONOMY",
            "side": "YES",
            "yes_price": 0.35,
            "model_probability_yes": None,
            "realized_pnl": 0.03,
        },
        {
            "decision_id": "decision-011",
            "timestamp_utc": "not-a-timestamp",
            "ticker": "KX-ECONOMY",
            "side": "NO",
            "yes_price": 0.60,
            "model_probability_yes": 0.47,
            "realized_pnl": -0.04,
        },
    ]

    return pd.DataFrame.from_records(records)


def validate_required_columns(frame: pd.DataFrame) -> None:
    """Raise an error when the expected research schema is incomplete."""

    missing_columns = REQUIRED_COLUMNS.difference(frame.columns)

    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_text}")

    if frame.empty:
        raise ValueError("Decision data cannot be empty.")


def validate_decision_data(frame: pd.DataFrame) -> ValidationReport:
    """Validate, normalize, and filter synthetic decision records."""

    validate_required_columns(frame)

    working = frame.copy().reset_index(drop=True)

    decision_ids = (
        working["decision_id"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    tickers = (
        working["ticker"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    sides = (
        working["side"]
        .fillna("")
        .astype(str)
        .str.strip()
        .str.upper()
    )

    timestamps = pd.to_datetime(
        working["timestamp_utc"],
        errors="coerce",
        utc=True,
    )

    yes_prices = pd.to_numeric(
        working["yes_price"],
        errors="coerce",
    )

    probabilities = pd.to_numeric(
        working["model_probability_yes"],
        errors="coerce",
    )

    realized_pnl = pd.to_numeric(
        working["realized_pnl"],
        errors="coerce",
    )

    invalid_rows = pd.Series(
        False,
        index=working.index,
        dtype=bool,
    )

    issues: list[ValidationIssue] = []

    def add_issue(
        *,
        row_number: int,
        field: str,
        code: str,
        message: str,
    ) -> None:
        """Record one issue and mark the row as invalid."""

        invalid_rows.loc[row_number] = True

        issues.append(
            ValidationIssue(
                row_number=row_number,
                decision_id=decision_ids.loc[row_number],
                field=field,
                code=code,
                message=message,
            )
        )

    duplicate_mask = (
        decision_ids.ne("")
        & decision_ids.duplicated(keep=False)
    )

    for row_number in working.index:
        if decision_ids.loc[row_number] == "":
            add_issue(
                row_number=row_number,
                field="decision_id",
                code="MISSING_DECISION_ID",
                message="decision_id is required.",
            )
        elif duplicate_mask.loc[row_number]:
            add_issue(
                row_number=row_number,
                field="decision_id",
                code="DUPLICATE_DECISION_ID",
                message="decision_id must be unique.",
            )

        if pd.isna(timestamps.loc[row_number]):
            add_issue(
                row_number=row_number,
                field="timestamp_utc",
                code="INVALID_TIMESTAMP",
                message="timestamp_utc must be a valid timestamp.",
            )

        if tickers.loc[row_number] == "":
            add_issue(
                row_number=row_number,
                field="ticker",
                code="MISSING_TICKER",
                message="ticker is required.",
            )

        if sides.loc[row_number] not in {"YES", "NO"}:
            add_issue(
                row_number=row_number,
                field="side",
                code="INVALID_SIDE",
                message="side must be either YES or NO.",
            )

        price = yes_prices.loc[row_number]

        if pd.isna(price):
            add_issue(
                row_number=row_number,
                field="yes_price",
                code="INVALID_PRICE",
                message="yes_price must be numeric.",
            )
        elif not np.isfinite(price):
            add_issue(
                row_number=row_number,
                field="yes_price",
                code="NONFINITE_PRICE",
                message="yes_price must be finite.",
            )
        elif not 0.0 <= float(price) <= 1.0:
            add_issue(
                row_number=row_number,
                field="yes_price",
                code="PRICE_OUT_OF_RANGE",
                message="yes_price must be between 0.0 and 1.0.",
            )

        probability = probabilities.loc[row_number]

        if pd.isna(probability):
            add_issue(
                row_number=row_number,
                field="model_probability_yes",
                code="INVALID_PROBABILITY",
                message="model probability must be numeric.",
            )
        elif not np.isfinite(probability):
            add_issue(
                row_number=row_number,
                field="model_probability_yes",
                code="NONFINITE_PROBABILITY",
                message="model probability must be finite.",
            )
        elif not 0.0 <= float(probability) <= 1.0:
            add_issue(
                row_number=row_number,
                field="model_probability_yes",
                code="PROBABILITY_OUT_OF_RANGE",
                message="model probability must be between 0.0 and 1.0.",
            )

        pnl_value = realized_pnl.loc[row_number]

        if pd.isna(pnl_value):
            add_issue(
                row_number=row_number,
                field="realized_pnl",
                code="INVALID_PNL",
                message="realized_pnl must be numeric.",
            )
        elif not np.isfinite(pnl_value):
            add_issue(
                row_number=row_number,
                field="realized_pnl",
                code="NONFINITE_PNL",
                message="realized_pnl must be finite.",
            )

    cleaned_data = pd.DataFrame(
        {
            "decision_id": decision_ids,
            "timestamp_utc": timestamps,
            "ticker": tickers,
            "side": sides,
            "yes_price": yes_prices.astype(float),
            "model_probability_yes": probabilities.astype(float),
            "realized_pnl": realized_pnl.astype(float),
        }
    ).loc[~invalid_rows].reset_index(drop=True)

    ordered_issues = tuple(
        sorted(
            issues,
            key=lambda issue: (
                issue.row_number,
                issue.field,
                issue.code,
            ),
        )
    )

    total_rows = len(working)
    invalid_count = int(invalid_rows.sum())
    valid_count = total_rows - invalid_count

    return ValidationReport(
        total_rows=total_rows,
        valid_rows=valid_count,
        invalid_rows=invalid_count,
        issue_count=len(ordered_issues),
        issues=ordered_issues,
        cleaned_data=cleaned_data,
    )


def print_validation_report(report: ValidationReport) -> None:
    """Print a readable validation summary."""

    print("=" * 78)
    print("Synthetic Prediction-Market Data Validation")
    print("=" * 78)
    print(f"Total rows:   {report.total_rows}")
    print(f"Valid rows:   {report.valid_rows}")
    print(f"Invalid rows: {report.invalid_rows}")
    print(f"Issues found: {report.issue_count}")
    print()

    print("Validation issues:")

    for issue in report.issues:
        print(
            f"row={issue.row_number:02d} "
            f"decision_id={issue.decision_id or '<missing>'} "
            f"field={issue.field} "
            f"code={issue.code}"
        )

    print()
    print("Cleaned valid records:")
    print(report.cleaned_data.to_string(index=False))


def main() -> None:
    """Run the complete synthetic validation example."""

    source_data = build_synthetic_decision_data()
    report = validate_decision_data(source_data)
    print_validation_report(report)


if __name__ == "__main__":
    main()
