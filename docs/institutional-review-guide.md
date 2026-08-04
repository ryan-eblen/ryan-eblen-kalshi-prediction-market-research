# Institutional Review Guide

## Executive Summary

This repository is a sanitized technical case study derived from an independently
developed prediction-market trading and quantitative research platform.

The underlying project was built to investigate three connected questions:

1. Can prediction-market opportunities be identified systematically?
2. Can those opportunities survive realistic execution costs?
3. Can exchange executions be converted reliably into accurate internal
   positions and P&L records?

The public repository demonstrates selected engineering, research, testing, and
diagnostic patterns without releasing the complete production system,
credentials, account information, proprietary strategy parameters, or raw
live-trading records.

## What the Public Repository Demonstrates

The repository contains seven deterministic Python examples covering:

* Cost-aware expected-value calculations
* Partial-fill and cumulative-fill reconciliation
* Idempotent order-event processing
* Synthetic strategy evaluation with transaction costs
* Market-data validation and normalization
* Pre-trade exposure and loss controls
* Execution-funnel diagnostics
* SQLite-based order, execution, position, and P&L reconciliation

The supporting test suite contains 132 unique unit tests. GitHub Actions executes
the suite under Python 3.11, 3.12, and 3.13, representing 396 test executions
per workflow run.

The workflow also performs Python compilation, Ruff correctness checks, and
execution of the principal synthetic examples.

## Private Platform Scope

The larger private platform includes or has included:

* REST exchange connectivity
* WebSocket market-data ingestion
* Market and contract discovery
* Simulated and live execution paths
* IOC taker-order submission
* Order-registry lifecycle tracking
* Partial- and full-fill reconciliation
* Position creation and cleanup
* Predictive-model evaluation
* Historical strategy replay
* Counterfactual price markouts
* Transaction-cost sensitivity testing
* Strategy discovery and ranking
* Portfolio construction and allocation
* Side, ticker, family, stability, and horizon diagnostics
* Deterministic source and output certification

The primary production application grew to approximately 11,000 lines, with
more than 100 supporting research, testing, diagnostic, and certification
files.

## Principal Execution Finding

One of the most important production investigations concerned a material
difference between simulated and live execution.

A substantial number of live IOC orders were submitted, but only a small
percentage produced exchange-confirmed executions. A second conversion gap
appeared between exchange-confirmed executions and positions successfully
created inside the application.

The investigation separated three stages that must not be treated as one event:

1. Order submission
2. Exchange execution
3. Internal position hydration

This distinction revealed that strategy-signal quality alone could not explain
live performance. Exchange behavior, execution acknowledgments, cumulative-fill
interpretation, internal registry state, duplicate-event handling, and position
creation were also material.

The public execution-funnel, order-reconciliation, and SQL-reconciliation
examples reproduce these engineering concepts using deterministic synthetic
data.

## Principal Research Finding

The research process intentionally tested whether attractive historical signals
remained economically viable after execution costs.

The principal research dataset contained 33,605 market decisions. The broader
research platform evaluated 154 systematic strategy configurations and
constructed a 15-member research shadow portfolio for additional attribution
and stability analysis.

Later side, ticker, strategy, family, horizon, and transaction-cost diagnostics
did not identify a strategy family that remained robustly positive under the
final cost assumptions.

That negative result is treated as an important finding rather than omitted or
reframed as proven profitability.

The repository therefore does not claim:

* Durable live profitability
* Guaranteed predictive performance
* Deployable alpha from the published examples
* Equivalence between simulation and live execution

## Engineering Principles

The project emphasizes:

* Defensive input validation
* Explicit state transitions
* Idempotent reconciliation
* Parameterized SQL
* Transaction rollback
* Foreign-key and schema constraints
* Deterministic synthetic examples
* Automated unit testing
* Multi-version CI
* Reproducible local execution
* Honest documentation of negative results
* Separation of public evidence from proprietary implementation

## AI-Assisted Development

The platform was developed through a structured AI-assisted workflow.

AI tools supported code generation, debugging hypotheses, test design, log
analysis, documentation, and iterative review. The process remained grounded
in explicit requirements, observed runtime output, compilation, testing,
reconciliation evidence, and repeated verification.

The repository is intended to demonstrate the ability to direct, inspect,
validate, debug, and document AI-assisted Python development rather than to
represent that every implementation detail was written without assistance.

## Suitable Review Paths

### Python or AI Engineering

Review:

* `examples/`
* `tests/`
* `.github/workflows/python-tests.yml`
* `pyproject.toml`
* `docs/local-verification.md`

### Trading Systems and Operations

Review:

* `examples/order_reconciliation_example.py`
* `examples/execution_funnel_example.py`
* `examples/sql_reconciliation_example.py`
* `sql/schema.sql`
* `sql/reconciliation_queries.sql`
* `docs/execution-debugging-case-study.md`

### Quantitative Research

Review:

* `examples/expected_value_example.py`
* `examples/strategy_evaluation_example.py`
* `docs/research-methodology.md`
* `docs/findings-and-limitations.md`

## Public and Private Boundary

The repository intentionally excludes:

* API keys and private keys
* Exchange-account information
* Raw live-order and account records
* Complete production source code
* Proprietary strategy thresholds
* Private deployment infrastructure
* Confidential third-party information

All runnable public examples use synthetic or sanitized records and require no
exchange credentials.

## Discussion Areas

The project may support technical discussions involving:

* Prediction-market execution
* Order and position reconciliation
* Simulation-versus-live divergence
* Market-data validation
* Transaction-cost analysis
* Research reproducibility
* Python debugging
* SQL diagnostics
* Risk controls
* AI-assisted software development
* Prediction-market platform infrastructure

## Contact

**Ryan Eblen**
AI-Assisted Python Developer and Prediction-Market Systems Researcher
Louisville, Kentucky
[ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)
