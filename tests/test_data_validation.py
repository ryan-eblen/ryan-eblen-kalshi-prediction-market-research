"""Tests for the synthetic prediction-market data-validation example."""

import unittest

import numpy as np
import pandas as pd

from examples.data_validation_example import (
    build_synthetic_decision_data,
    validate_decision_data,
    validate_required_columns,
)


class TestDataValidation(unittest.TestCase):
    """Verify schema checks, normalization, and issue reporting."""

    def setUp(self) -> None:
        """Create the standard source data and one valid example row."""

        self.source = build_synthetic_decision_data()
        self.valid_row = self.source.iloc[[0]].copy()

    def test_source_data_contains_eleven_rows(self) -> None:
        """The synthetic source contains the expected number of records."""

        self.assertEqual(len(self.source), 11)

    def test_default_validation_counts(self) -> None:
        """The standard example produces the expected summary counts."""

        report = validate_decision_data(self.source)

        self.assertEqual(report.total_rows, 11)
        self.assertEqual(report.valid_rows, 5)
        self.assertEqual(report.invalid_rows, 6)
        self.assertEqual(report.issue_count, 6)

    def test_cleaned_data_contains_only_valid_decisions(self) -> None:
        """Invalid records are excluded from the cleaned dataset."""

        report = validate_decision_data(self.source)

        self.assertEqual(
            report.cleaned_data["decision_id"].tolist(),
            [
                "decision-001",
                "decision-002",
                "decision-003",
                "decision-004",
                "decision-005",
            ],
        )

    def test_ticker_and_side_are_normalized(self) -> None:
        """Whitespace and lowercase text are normalized safely."""

        report = validate_decision_data(self.source)

        normalized = report.cleaned_data.loc[
            report.cleaned_data["decision_id"] == "decision-003"
        ].iloc[0]

        self.assertEqual(normalized["ticker"], "KX-INFLATION")
        self.assertEqual(normalized["side"], "YES")

    def test_cleaned_timestamps_are_utc(self) -> None:
        """Valid timestamps are converted into UTC-aware values."""

        report = validate_decision_data(self.source)

        timestamp_series = report.cleaned_data["timestamp_utc"]

        self.assertIsInstance(
            timestamp_series.dtype,
            pd.DatetimeTZDtype,
        )
        self.assertEqual(
            str(timestamp_series.dtype.tz),
            "UTC",
        )

    def test_duplicate_identifiers_report_both_rows(self) -> None:
        """Both records sharing a duplicate identifier are rejected."""

        report = validate_decision_data(self.source)

        duplicate_issues = [
            issue
            for issue in report.issues
            if issue.code == "DUPLICATE_DECISION_ID"
        ]

        self.assertEqual(len(duplicate_issues), 2)
        self.assertTrue(
            all(
                issue.decision_id == "decision-006"
                for issue in duplicate_issues
            )
        )

    def test_invalid_side_is_reported(self) -> None:
        """An unsupported contract side produces an issue."""

        report = validate_decision_data(self.source)

        codes = {issue.code for issue in report.issues}

        self.assertIn("INVALID_SIDE", codes)

    def test_out_of_range_price_is_reported(self) -> None:
        """A price above one is rejected."""

        report = validate_decision_data(self.source)

        codes = {issue.code for issue in report.issues}

        self.assertIn("PRICE_OUT_OF_RANGE", codes)

    def test_missing_probability_is_reported(self) -> None:
        """A missing model probability is rejected."""

        report = validate_decision_data(self.source)

        codes = {issue.code for issue in report.issues}

        self.assertIn("INVALID_PROBABILITY", codes)

    def test_invalid_timestamp_is_reported(self) -> None:
        """Malformed timestamp text is rejected."""

        report = validate_decision_data(self.source)

        codes = {issue.code for issue in report.issues}

        self.assertIn("INVALID_TIMESTAMP", codes)

    def test_missing_required_column_is_rejected(self) -> None:
        """An incomplete input schema raises an error."""

        invalid_frame = self.source.drop(columns=["yes_price"])

        with self.assertRaises(ValueError):
            validate_required_columns(invalid_frame)

    def test_empty_frame_is_rejected(self) -> None:
        """An empty dataset cannot be validated as research evidence."""

        empty_frame = self.source.iloc[0:0].copy()

        with self.assertRaises(ValueError):
            validate_required_columns(empty_frame)

    def test_missing_ticker_is_reported(self) -> None:
        """A blank ticker invalidates the record."""

        invalid_frame = self.valid_row.copy()
        invalid_frame.loc[invalid_frame.index[0], "ticker"] = ""

        report = validate_decision_data(invalid_frame)

        self.assertEqual(report.valid_rows, 0)
        self.assertEqual(report.invalid_rows, 1)
        self.assertEqual(report.issues[0].code, "MISSING_TICKER")

    def test_nonfinite_price_is_reported(self) -> None:
        """An infinite market price is rejected."""

        invalid_frame = self.valid_row.copy()
        invalid_frame.loc[invalid_frame.index[0], "yes_price"] = np.inf

        report = validate_decision_data(invalid_frame)

        self.assertEqual(report.issues[0].code, "NONFINITE_PRICE")

    def test_nonfinite_probability_is_reported(self) -> None:
        """An infinite model probability is rejected."""

        invalid_frame = self.valid_row.copy()
        invalid_frame.loc[
            invalid_frame.index[0],
            "model_probability_yes",
        ] = np.inf

        report = validate_decision_data(invalid_frame)

        self.assertEqual(
            report.issues[0].code,
            "NONFINITE_PROBABILITY",
        )

    def test_nonfinite_pnl_is_reported(self) -> None:
        """An infinite realized P&L value is rejected."""

        invalid_frame = self.valid_row.copy()
        invalid_frame.loc[invalid_frame.index[0], "realized_pnl"] = np.inf

        report = validate_decision_data(invalid_frame)

        self.assertEqual(report.issues[0].code, "NONFINITE_PNL")

    def test_one_row_can_have_multiple_issues(self) -> None:
        """Every material defect is reported, even within one record."""

        invalid_frame = self.valid_row.copy()
        row_index = invalid_frame.index[0]

        invalid_frame.loc[row_index, "side"] = "MAYBE"
        invalid_frame.loc[row_index, "yes_price"] = 1.25

        report = validate_decision_data(invalid_frame)

        codes = {issue.code for issue in report.issues}

        self.assertEqual(report.invalid_rows, 1)
        self.assertEqual(report.issue_count, 2)
        self.assertEqual(
            codes,
            {
                "INVALID_SIDE",
                "PRICE_OUT_OF_RANGE",
            },
        )


if __name__ == "__main__":
    unittest.main()
