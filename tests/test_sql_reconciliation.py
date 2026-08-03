"""Tests for the synthetic SQLite reconciliation example."""

import sqlite3
import tempfile
import unittest
from pathlib import Path

from examples.sql_reconciliation_example import (
    QUERY_PATH,
    SCHEMA_PATH,
    build_reconciliation_report,
    count_rows,
    create_database,
    insert_many,
    load_synthetic_records,
    query_rows,
    read_sql_file,
)


class TestSQLReconciliation(unittest.TestCase):
    """Verify schema controls, transactions, queries, and findings."""

    def setUp(self) -> None:
        """Create and populate an in-memory database."""

        self.connection = create_database()
        load_synthetic_records(self.connection)

    def tearDown(self) -> None:
        """Close the in-memory database."""

        self.connection.close()

    def test_required_sql_files_are_readable(self) -> None:
        """Both repository SQL files exist and contain statements."""

        schema_sql = read_sql_file(SCHEMA_PATH)
        query_sql = read_sql_file(QUERY_PATH)

        self.assertIn("CREATE TABLE orders", schema_sql)
        self.assertIn(
            "CREATE VIEW executed_without_position",
            query_sql,
        )

    def test_default_report_row_counts(self) -> None:
        """The synthetic database contains the expected records."""

        report = build_reconciliation_report(self.connection)

        self.assertEqual(report.order_count, 6)
        self.assertEqual(report.execution_row_count, 7)
        self.assertEqual(report.position_count, 4)
        self.assertEqual(report.pnl_record_count, 5)

    def test_executed_order_without_position_is_identified(
        self,
    ) -> None:
        """An executed order lacking a position is reported."""

        report = build_reconciliation_report(self.connection)

        self.assertEqual(
            report.executed_without_position,
            (
                {
                    "order_id": "order-002",
                    "trade_id": "trade-002",
                    "ticker": "KX-INFLATION",
                    "side": "NO",
                    "requested_quantity": 3,
                    "executed_quantity": 3,
                },
            ),
        )

    def test_mismatch_order_ids_are_identified(self) -> None:
        """All quantity, ticker, and side mismatches are reported."""

        report = build_reconciliation_report(self.connection)

        order_ids = tuple(
            record["order_id"]
            for record in report.position_execution_mismatches
        )

        self.assertEqual(
            order_ids,
            (
                "order-003",
                "order-004",
                "order-006",
            ),
        )

    def test_duplicate_rows_create_quantity_mismatch(self) -> None:
        """Duplicate execution rows inflate executed quantity."""

        report = build_reconciliation_report(self.connection)

        record = next(
            item
            for item in report.position_execution_mismatches
            if item["order_id"] == "order-003"
        )

        self.assertEqual(record["executed_quantity"], 2)
        self.assertEqual(record["position_quantity"], 1)

    def test_position_quantity_mismatch_is_identified(self) -> None:
        """A position larger than executed quantity is reported."""

        report = build_reconciliation_report(self.connection)

        record = next(
            item
            for item in report.position_execution_mismatches
            if item["order_id"] == "order-004"
        )

        self.assertEqual(record["executed_quantity"], 2)
        self.assertEqual(record["position_quantity"], 3)

    def test_position_side_mismatch_is_identified(self) -> None:
        """A position on the wrong side is reported."""

        report = build_reconciliation_report(self.connection)

        record = next(
            item
            for item in report.position_execution_mismatches
            if item["order_id"] == "order-006"
        )

        self.assertEqual(record["order_side"], "NO")
        self.assertEqual(record["position_side"], "YES")
        self.assertEqual(record["executed_quantity"], 1)
        self.assertEqual(record["position_quantity"], 1)

    def test_duplicate_execution_identifier_is_identified(
        self,
    ) -> None:
        """A repeated exchange execution identifier is reported."""

        report = build_reconciliation_report(self.connection)

        self.assertEqual(
            report.duplicate_executions,
            (
                {
                    "execution_id": "execution-003",
                    "order_id": "order-003",
                    "occurrence_count": 2,
                    "reported_quantity": 2,
                },
            ),
        )

    def test_daily_realized_pnl_is_aggregated(self) -> None:
        """P&L records are summarized by UTC calendar date."""

        report = build_reconciliation_report(self.connection)

        self.assertEqual(
            report.daily_realized_pnl,
            (
                {
                    "pnl_date": "2026-01-05",
                    "pnl_records": 3,
                    "total_realized_pnl": 0.07,
                },
                {
                    "pnl_date": "2026-01-06",
                    "pnl_records": 2,
                    "total_realized_pnl": -0.03,
                },
            ),
        )

    def test_count_rows_accepts_approved_tables(self) -> None:
        """The table-count helper supports the declared tables."""

        self.assertEqual(
            count_rows(self.connection, "orders"),
            6,
        )
        self.assertEqual(
            count_rows(self.connection, "executions"),
            7,
        )

    def test_count_rows_rejects_unknown_table(self) -> None:
        """Dynamic table names are restricted to an allowlist."""

        with self.assertRaises(ValueError):
            count_rows(self.connection, "sqlite_master")

    def test_query_rows_uses_parameters(self) -> None:
        """Parameterized filtering returns only matching records."""

        records = query_rows(
            self.connection,
            """
            SELECT order_id
            FROM orders
            WHERE ticker = ?
            ORDER BY order_id
            """,
            ("KX-RATE",),
        )

        self.assertEqual(
            records,
            (
                {"order_id": "order-001"},
                {"order_id": "order-004"},
            ),
        )

    def test_foreign_key_constraint_is_enforced(self) -> None:
        """An execution cannot reference a missing order."""

        connection = create_database()

        try:
            with self.assertRaises(sqlite3.IntegrityError):
                with connection:
                    connection.execute(
                        """
                        INSERT INTO executions (
                            execution_id,
                            order_id,
                            filled_quantity,
                            fill_price,
                            executed_at
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            "execution-invalid",
                            "missing-order",
                            1,
                            0.50,
                            "2026-01-05T14:00:00Z",
                        ),
                    )
        finally:
            connection.close()

    def test_invalid_order_side_is_rejected(self) -> None:
        """The schema accepts only YES and NO order sides."""

        connection = create_database()

        try:
            with self.assertRaises(sqlite3.IntegrityError):
                with connection:
                    connection.execute(
                        """
                        INSERT INTO orders (
                            order_id,
                            trade_id,
                            ticker,
                            side,
                            requested_quantity,
                            submitted_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            "order-invalid",
                            "trade-invalid",
                            "KX-TEST",
                            "MAYBE",
                            1,
                            "2026-01-05T14:00:00Z",
                        ),
                    )
        finally:
            connection.close()

    def test_nonpositive_order_quantity_is_rejected(self) -> None:
        """An order quantity must be greater than zero."""

        connection = create_database()

        try:
            with self.assertRaises(sqlite3.IntegrityError):
                with connection:
                    connection.execute(
                        """
                        INSERT INTO orders (
                            order_id,
                            trade_id,
                            ticker,
                            side,
                            requested_quantity,
                            submitted_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (
                            "order-invalid",
                            "trade-invalid",
                            "KX-TEST",
                            "YES",
                            0,
                            "2026-01-05T14:00:00Z",
                        ),
                    )
        finally:
            connection.close()

    def test_out_of_range_fill_price_is_rejected(self) -> None:
        """Execution prices must remain between zero and one."""

        connection = create_database()

        try:
            with connection:
                connection.execute(
                    """
                    INSERT INTO orders (
                        order_id,
                        trade_id,
                        ticker,
                        side,
                        requested_quantity,
                        submitted_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        "order-100",
                        "trade-100",
                        "KX-TEST",
                        "YES",
                        1,
                        "2026-01-05T14:00:00Z",
                    ),
                )

            with self.assertRaises(sqlite3.IntegrityError):
                with connection:
                    connection.execute(
                        """
                        INSERT INTO executions (
                            execution_id,
                            order_id,
                            filled_quantity,
                            fill_price,
                            executed_at
                        )
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (
                            "execution-100",
                            "order-100",
                            1,
                            1.25,
                            "2026-01-05T14:00:01Z",
                        ),
                    )
        finally:
            connection.close()

    def test_failed_batch_insert_rolls_back(self) -> None:
        """A failed transaction does not preserve partial inserts."""

        connection = create_database()

        records = (
            (
                "order-100",
                "trade-100",
                "KX-TEST",
                "YES",
                1,
                "2026-01-05T14:00:00Z",
            ),
            (
                "order-100",
                "trade-101",
                "KX-TEST",
                "NO",
                1,
                "2026-01-05T14:00:01Z",
            ),
        )

        try:
            with self.assertRaises(sqlite3.IntegrityError):
                with connection:
                    insert_many(
                        connection,
                        """
                        INSERT INTO orders (
                            order_id,
                            trade_id,
                            ticker,
                            side,
                            requested_quantity,
                            submitted_at
                        )
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        records,
                    )

            self.assertEqual(
                count_rows(connection, "orders"),
                0,
            )
        finally:
            connection.close()

    def test_missing_sql_file_is_rejected(self) -> None:
        """A required SQL file must exist."""

        missing_path = Path(
            "/tmp/nonexistent-reconciliation-file.sql"
        )

        with self.assertRaises(FileNotFoundError):
            read_sql_file(missing_path)

    def test_empty_sql_file_is_rejected(self) -> None:
        """A SQL file containing only whitespace is invalid."""

        with tempfile.TemporaryDirectory() as directory:
            sql_path = Path(directory) / "empty.sql"
            sql_path.write_text(" \n\t", encoding="utf-8")

            with self.assertRaises(ValueError):
                read_sql_file(sql_path)

    def test_second_data_load_preserves_original_counts(self) -> None:
        """A duplicate load fails without corrupting existing records."""

        original_counts = (
            count_rows(self.connection, "orders"),
            count_rows(self.connection, "executions"),
            count_rows(self.connection, "positions"),
            count_rows(self.connection, "pnl_ledger"),
        )

        with self.assertRaises(sqlite3.IntegrityError):
            load_synthetic_records(self.connection)

        current_counts = (
            count_rows(self.connection, "orders"),
            count_rows(self.connection, "executions"),
            count_rows(self.connection, "positions"),
            count_rows(self.connection, "pnl_ledger"),
        )

        self.assertEqual(current_counts, original_counts)


if __name__ == "__main__":
    unittest.main()
