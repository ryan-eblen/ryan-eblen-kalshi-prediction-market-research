DROP VIEW IF EXISTS daily_realized_pnl;
DROP VIEW IF EXISTS duplicate_executions;
DROP VIEW IF EXISTS position_execution_mismatches;
DROP VIEW IF EXISTS executed_without_position;
DROP VIEW IF EXISTS order_execution_totals;

CREATE VIEW order_execution_totals AS
SELECT
    o.order_id,
    o.trade_id,
    o.ticker,
    o.side,
    o.requested_quantity,
    COUNT(e.execution_row_id) AS execution_rows,
    COUNT(DISTINCT e.execution_id) AS distinct_execution_ids,
    COALESCE(SUM(e.filled_quantity), 0) AS executed_quantity
FROM orders AS o
LEFT JOIN executions AS e
    ON e.order_id = o.order_id
GROUP BY
    o.order_id,
    o.trade_id,
    o.ticker,
    o.side,
    o.requested_quantity;

CREATE VIEW executed_without_position AS
SELECT
    totals.order_id,
    totals.trade_id,
    totals.ticker,
    totals.side,
    totals.requested_quantity,
    totals.executed_quantity
FROM order_execution_totals AS totals
LEFT JOIN positions AS position
    ON position.order_id = totals.order_id
WHERE
    totals.executed_quantity > 0
    AND position.position_id IS NULL;

CREATE VIEW position_execution_mismatches AS
SELECT
    totals.order_id,
    totals.trade_id,
    totals.ticker AS order_ticker,
    position.ticker AS position_ticker,
    totals.side AS order_side,
    position.side AS position_side,
    totals.executed_quantity,
    position.quantity AS position_quantity
FROM order_execution_totals AS totals
INNER JOIN positions AS position
    ON position.order_id = totals.order_id
WHERE
    position.quantity <> totals.executed_quantity
    OR position.ticker <> totals.ticker
    OR position.side <> totals.side;

CREATE VIEW duplicate_executions AS
SELECT
    execution_id,
    order_id,
    COUNT(*) AS occurrence_count,
    SUM(filled_quantity) AS reported_quantity
FROM executions
GROUP BY
    execution_id,
    order_id
HAVING COUNT(*) > 1;

CREATE VIEW daily_realized_pnl AS
SELECT
    substr(realized_at, 1, 10) AS pnl_date,
    COUNT(*) AS pnl_records,
    ROUND(SUM(realized_pnl), 6) AS total_realized_pnl
FROM pnl_ledger
GROUP BY substr(realized_at, 1, 10);
