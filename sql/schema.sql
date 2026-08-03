PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS pnl_ledger;
DROP TABLE IF EXISTS positions;
DROP TABLE IF EXISTS executions;
DROP TABLE IF EXISTS orders;

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    trade_id TEXT NOT NULL UNIQUE,
    ticker TEXT NOT NULL
        CHECK (length(trim(ticker)) > 0),
    side TEXT NOT NULL
        CHECK (side IN ('YES', 'NO')),
    requested_quantity INTEGER NOT NULL
        CHECK (requested_quantity > 0),
    submitted_at TEXT NOT NULL
);

CREATE TABLE executions (
    execution_row_id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_id TEXT NOT NULL,
    order_id TEXT NOT NULL,
    filled_quantity INTEGER NOT NULL
        CHECK (filled_quantity > 0),
    fill_price REAL NOT NULL
        CHECK (fill_price >= 0.0 AND fill_price <= 1.0),
    executed_at TEXT NOT NULL,
    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE
);

CREATE TABLE positions (
    position_id TEXT PRIMARY KEY,
    order_id TEXT NOT NULL UNIQUE,
    ticker TEXT NOT NULL
        CHECK (length(trim(ticker)) > 0),
    side TEXT NOT NULL
        CHECK (side IN ('YES', 'NO')),
    quantity INTEGER NOT NULL
        CHECK (quantity > 0),
    average_entry_price REAL NOT NULL
        CHECK (
            average_entry_price >= 0.0
            AND average_entry_price <= 1.0
        ),
    hydrated_at TEXT NOT NULL,
    FOREIGN KEY (order_id)
        REFERENCES orders(order_id)
        ON DELETE CASCADE
);

CREATE TABLE pnl_ledger (
    pnl_id TEXT PRIMARY KEY,
    trade_id TEXT NOT NULL,
    realized_pnl REAL NOT NULL,
    realized_at TEXT NOT NULL
);

CREATE INDEX idx_executions_order_id
    ON executions(order_id);

CREATE INDEX idx_executions_execution_id
    ON executions(execution_id);

CREATE INDEX idx_positions_order_id
    ON positions(order_id);

CREATE INDEX idx_pnl_ledger_realized_at
    ON pnl_ledger(realized_at);
