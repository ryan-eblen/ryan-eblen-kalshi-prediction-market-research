"""Synthetic SQL reconciliation and P&L diagnostic example.

This module loads the SQLite schema and diagnostic views stored in the
repository, inserts deterministic synthetic records using parameterized
queries, and reports reconciliation defects.

It uses no exchange credentials, account information, private production
records, or proprietary strategy parameters.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPOSITORY_ROOT / "sql" / "schema.sql"
QUERY_PATH = REPOSITORY_ROOT / "sql" / "reconciliation_queries.sql"


@dataclass(frozen=True)
class ReconciliationReport:
    """Complete result of one synthetic SQL diagnostic run."""

    order_count: int
    execution_row_count: int
    position_count: int
    pnl_record_count: int
    executed_without_position: tuple[dict[str, Any], ...]
    position_execution_mismatches: tuple[dict[str, Any], ...]
    duplicate_executions: tuple[dict[str, Any], ...]
    daily_realized_pnl: tuple[dict[str, Any], ...]


def read_sql_file(path: Path) -> str:
    """Read one required SQL file from disk."""

    if not path.is_file():
        raise FileNotFoundError(f"Required SQL file not found: {path}")

    sql_text = path.read_text(encoding="utf-8").strip()

    if not sql_text:
        raise ValueError(f"SQL file cannot be empty: {path}")

    return sql_text


def create_database(
    database_path: str | Path = ":memory:",
) -> sqlite3.Connection:
    """Create and initialize an SQLite reconciliation database."""

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON;")
    connection.executescript(read_sql_file(SCHEMA_PATH))
    connection.executescript(read_sql_file(QUERY_PATH))

    return connection


def insert_many(
    connection: sqlite3.Connection,
    sql: str,
    records: Iterable[tuple[Any, ...]],
) -> None:
    """Insert records using a parameterized SQL statement."""

    connection.executemany(sql, tuple(records))


def load_synthetic_records(
    connection: sqlite3.Connection,
) -> None:
    """Insert deterministic synthetic orders, executions, positions, and P&L."""

    orders = (
        (
            "order-001",
            "trade-001",
            "KX-RATE",
            "YES",
            2,
            "2026-01-05T14:30:00Z",
        ),
        (
            "order-002",
            "trade-002",
            "KX-INFLATION",
            "NO",
            3,
            "2026-01-05T14:31:00Z",
        ),
        (
            "order-003",
            "trade-003",
            "KX-ECONOMY",
            "YES",
            2,
            "2026-01-05T14:32:00Z",
        ),
        (
            "order-004",
            "trade-004",
            "KX-RATE",
            "NO",
            2,
            "2026-01-05T14:33:00Z",
        ),
        (
            "order-005",
            "trade-005",
            "KX-INFLATION",
            "YES",
            1,
            "2026-01-05T14:34:00Z",
        ),
        (
            "order-006",
            "trade-006",
            "KX-ECONOMY",
            "NO",
            1,
            "2026-01-05T14:35:00Z",
        ),
    )

    executions = (
        (
            "execution-001",
            "order-001",
            2,
            0.42,
            "2026-01-05T14:30:01Z",
        ),
        (
            "execution-002a",
            "order-002",
            1,
            0.61,
            "2026-01-05T14:31:01Z",
        ),
        (
            "execution-002b",
            "order-002",
            2,
            0.60,
            "2026-01-05T14:31:02Z",
        ),
        (
            "execution-003",
            "order-003",
            1,
            0.35,
            "2026-01-05T14:32:01Z",
        ),
        (
            "execution-003",
            "order-003",
            1,
            0.35,
            "2026-01-05T14:32:01Z",
        ),
        (
            "execution-004",
            "order-004",
            2,
            0.58,
            "2026-01-05T14:33:01Z",
        ),
        (
            "execution-006",
            "order-006",
            1,
            0.47,
            "2026-01-05T14:35:01Z",
        ),
    )

    positions = (
        (
            "position-001",
            "order-001",
            "KX-RATE",
            "YES",
            2,
            0.42,
            "2026-01-05T14:30:02Z",
        ),
        (
            "position-003",
            "order-003",
            "KX-ECONOMY",
            "YES",
            1,
            0.35,
            "2026-01-05T14:32:02Z",
        ),
        (
            "position-004",
            "order-004",
            "KX-RATE",
            "NO",
            3,
            0.58,
            "2026-01-05T14:33:02Z",
        ),
        (
            "position-006",
            "order-006",
            "KX-ECONOMY",
            "YES",
            1,
            0.47,
            "2026-01-05T14:35:02Z",
        ),
    )

    pnl_records = (
        (
            "pnl-001",
            "trade-001",
            0.08,
            "2026-01-05T16:00:00Z",
        ),
        (
            "pnl-002",
            "trade-002",
            -0.03,
            "2026-01-05T16:10:00Z",
        ),
        (
            "pnl-003",
            "trade-003",
            0.02,
            "2026-01-05T16:20:00Z",
        ),
        (
            "pnl-004",
            "trade-004",
            -0.04,
            "2026-01-06T16:00:00Z",
        ),
        (
            "pnl-005",
            "trade-006",
            0.01,
            "2026-01-06T16:10:00Z",
        ),
    )

    try:
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
                orders,
            )

            insert_many(
                connection,
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
                executions,
            )

            insert_many(
                connection,
                """
                INSERT INTO positions (
                    position_id,
                    order_id,
                    ticker,
                    side,
                    quantity,
                    average_entry_price,
                    hydrated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                positions,
            )

            insert_many(
                connection,
                """
                INSERT INTO pnl_ledger (
                    pnl_id,
                    trade_id,
                    realized_pnl,
                    realized_at
                )
                VALUES (?, ?, ?, ?)
                """,
                pnl_records,
            )
    except sqlite3.DatabaseError:
        connection.rollback()
        raise


def query_rows(
    connection: sqlite3.Connection,
    sql: str,
    parameters: tuple[Any, ...] = (),
) -> tuple[dict[str, Any], ...]:
    """Execute a query and return immutable dictionary records."""

    cursor = connection.execute(sql, parameters)

    return tuple(dict(row) for row in cursor.fetchall())


def count_rows(
    connection: sqlite3.Connection,
    table_name: str,
) -> int:
    """Count rows from one approved synthetic table."""

    allowed_tables = {
        "orders",
        "executions",
        "positions",
        "pnl_ledger",
    }

    if table_name not in allowed_tables:
        raise ValueError(f"Unsupported table name: {table_name}")

    row = connection.execute(
        f"SELECT COUNT(*) AS row_count FROM {table_name}"
    ).fetchone()

    if row is None:
        raise RuntimeError(f"Unable to count rows in {table_name}")

    return int(row["row_count"])


def build_reconciliation_report(
    connection: sqlite3.Connection,
) -> ReconciliationReport:
    """Run all SQL diagnostic views and build a structured report."""

    return ReconciliationReport(
        order_count=count_rows(connection, "orders"),
        execution_row_count=count_rows(connection, "executions"),
        position_count=count_rows(connection, "positions"),
        pnl_record_count=count_rows(connection, "pnl_ledger"),
        executed_without_position=query_rows(
            connection,
            """
            SELECT *
            FROM executed_without_position
            ORDER BY order_id
            """,
        ),
        position_execution_mismatches=query_rows(
            connection,
            """
            SELECT *
            FROM position_execution_mismatches
            ORDER BY order_id
            """,
        ),
        duplicate_executions=query_rows(
            connection,
            """
            SELECT *
            FROM duplicate_executions
            ORDER BY execution_id, order_id
            """,
        ),
        daily_realized_pnl=query_rows(
            connection,
            """
            SELECT *
            FROM daily_realized_pnl
            ORDER BY pnl_date
            """,
        ),
    )


def print_records(
    title: str,
    records: tuple[dict[str, Any], ...],
) -> None:
    """Print one collection of SQL diagnostic records."""

    print(title)

    if not records:
        print("  None")
        print()
        return

    for record in records:
        values = " | ".join(
            f"{key}={value}"
            for key, value in record.items()
        )
        print(f"  {values}")

    print()


def print_report(report: ReconciliationReport) -> None:
    """Print the complete synthetic SQL reconciliation report."""

    print("=" * 78)
    print("Synthetic SQL Reconciliation Diagnostic")
    print("=" * 78)
    print(f"Orders:                     {report.order_count}")
    print(
        "Execution rows:             "
        f"{report.execution_row_count}"
    )
    print(f"Positions:                  {report.position_count}")
    print(f"P&L records:                {report.pnl_record_count}")
    print()

    print_records(
        "Executed orders without positions:",
        report.executed_without_position,
    )

    print_records(
        "Position/execution mismatches:",
        report.position_execution_mismatches,
    )

    print_records(
        "Duplicate execution identifiers:",
        report.duplicate_executions,
    )

    print_records(
        "Daily realized P&L:",
        report.daily_realized_pnl,
    )

    unresolved_count = (
        len(report.executed_without_position)
        + len(report.position_execution_mismatches)
        + len(report.duplicate_executions)
    )

    print(f"Diagnostic record count:    {unresolved_count}")

    if unresolved_count:
        print(
            "Interpretation: execution records, position state, and "
            "duplicate-event handling require reconciliation."
        )
    else:
        print("Interpretation: no reconciliation defects detected.")


def main() -> None:
    """Run the complete in-memory SQL reconciliation example."""

    connection = create_database()

    try:
        load_synthetic_records(connection)
        report = build_reconciliation_report(connection)
        print_report(report)
    finally:
        connection.close()


if __name__ == "__main__":
    main()
