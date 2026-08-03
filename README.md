# Kalshi Prediction-Market Research Platform

A sanitized case study of an independently developed Python platform for prediction-market execution, quantitative research, and live-system diagnostics.

> **Project status:** Private portfolio construction
> **Author:** Ryan Eblen
> **Contact:** [ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)

## Project Overview

This repository documents the architecture, research methodology, debugging process, and selected reproducible components of a substantial prediction-market trading and quantitative research platform developed for Kalshi.

The project combines exchange connectivity, real-time market data, simulated and live order processing, position management, execution reconciliation, predictive-model evaluation, historical replay, counterfactual analysis, and deterministic research validation.

The public case study is being designed for two audiences:

* Employers and technical reviewers evaluating Python, data-analysis, debugging, and quantitative-system experience
* Prediction-market firms, market makers, platforms, researchers, and institutions interested in execution infrastructure, market research, or potential collaboration

This repository is a curated technical case study rather than a release of the complete production trading system.

## Why the Project Was Built

The original objective was to build an automated system capable of:

* Receiving real-time prediction-market data
* Identifying potential trading opportunities
* Evaluating expected value and execution conditions
* Submitting and monitoring orders
* Maintaining accurate position state
* Comparing simulated and live behavior
* Testing predictive models and systematic strategies
* Measuring whether apparent performance survived realistic execution costs

As the project developed, its focus expanded from strategy creation into a broader investigation of prediction-market execution, data quality, model validation, system reliability, and simulation-versus-live divergence.

## Project Scale

Selected project metrics include:

* More than **500 structured AI-assisted development and debugging sessions**
* Approximately **11,000 lines** in the primary production application
* More than **100 supporting research, testing, diagnostic, and certification files**
* **33,605 market decisions** in the principal research dataset
* **154 systematic strategy configurations** evaluated
* A **15-member research shadow portfolio**
* Historical replay, counterfactual markout, side, ticker, horizon, family, stability, and transaction-cost diagnostics
* Live exchange integration using REST APIs and WebSocket market data

These figures describe the scale of the engineering and research work. They are not claims of profitable trading performance.

## Core System Capabilities

### Exchange and Market Data

* REST API integration
* WebSocket market-data ingestion
* Market and contract discovery
* Quote and trade-event processing
* Price and side normalization
* Timestamped event handling
* Market-data validation

### Execution and Position Management

* Simulated and live execution paths
* IOC taker-order submission
* Order registry and lifecycle tracking
* Exchange acknowledgment processing
* Partial- and full-fill reconciliation
* Position creation and hydration
* Entry and exit processing
* Position cleanup and ghost-position removal
* Per-market position controls
* Structured execution logging

### Quantitative Research

* Structured research-dataset construction
* Feature analysis
* Predictive-model evaluation
* Historical strategy replay
* Counterfactual price markouts
* Transaction-cost sensitivity testing
* Strategy discovery and classification
* Portfolio construction and allocation
* Side, ticker, family, and time-horizon diagnostics
* Stability and concentration analysis
* Deterministic output certification

### Reliability and Validation

* Defensive input validation
* Exception handling
* Structured logging
* Unit and contract testing
* Source hashing
* Output-signature verification
* Deterministic reruns
* Regression analysis
* Simulation-versus-live comparison
* Technical handoff documentation

## Selected Technical Investigation

One of the project’s most important investigations involved a material divergence between simulated and live execution.

The system generated substantial live order-submission activity, but only a small percentage of submitted IOC orders resulted in exchange-confirmed executions. A further gap existed between exchange-confirmed executions and positions successfully created inside the application.

The investigation required tracing several interconnected components:

1. Order submission
2. Exchange acknowledgment
3. Order-registry state
4. Execution reconciliation
5. Filled-quantity interpretation
6. Position hydration
7. Active-position registration
8. Cleanup and recovery behavior

The work identified that execution quality could not be evaluated solely from strategy signals. Order behavior, exchange acknowledgments, internal state synchronization, and position reconciliation were equally important.

A dedicated debugging case study will document this investigation without exposing account information, private logs, credentials, or complete production logic.

## Research Integrity

The research process intentionally separates attractive historical signals from evidence of deployable profitability.

Later cost-aware diagnostics found that the tested strategy families did not demonstrate robust positive performance under the final execution-cost assumptions.

That result is an important project finding.

The repository does not present backtest results as guaranteed returns, and it does not claim that the system has established durable live profitability. Instead, the project demonstrates:

* How trading hypotheses were tested
* How execution costs changed conclusions
* How simulation and live behavior differed
* How negative findings were documented
* How reproducibility and validation were enforced
* How further research priorities were identified

## Technology

The project uses or has incorporated:

* Python
* pandas
* NumPy
* JSON and CSV data
* REST APIs
* WebSockets
* Object-oriented design
* Logging and diagnostics
* Unit and contract tests
* Git and source control
* Logistic regression
* Classification metrics
* Calibration analysis
* Historical replay
* Data visualization
* Linux command-line workflows

## AI-Assisted Development Methodology

The platform was developed through a structured AI-assisted workflow.

AI tools were used to help propose code, analyze logs, inspect potential causes, design tests, and document system behavior. Development remained directed by explicit requirements, observed runtime evidence, validation checks, and iterative review.

The process emphasized:

* Defining the intended behavior
* Inspecting the relevant source path
* Forming testable hypotheses
* Applying controlled changes
* Compiling and executing the code
* Reviewing runtime evidence
* Comparing expected and observed outputs
* Preserving detailed technical handoffs

This repository will distinguish between demonstrated understanding, AI-assisted implementation, observed evidence, and unresolved limitations.

## Repository Plan

The completed case study is expected to contain:

```text
kalshi-prediction-market-research/
├── README.md
├── docs/
│   ├── technical-case-study.md
│   ├── institutional-overview.md
│   ├── architecture.md
│   ├── execution-debugging-case-study.md
│   ├── research-methodology.md
│   ├── findings-and-limitations.md
│   └── collaboration-overview.md
├── examples/
│   ├── expected-value-example.py
│   ├── order-reconciliation-example.py
│   ├── strategy-evaluation-example.py
│   └── data-validation-example.py
├── tests/
│   ├── test-expected-value.py
│   └── test-reconciliation.py
├── sample-data/
│   └── synthetic-market-data.csv
├── assets/
│   ├── system-architecture.png
│   ├── execution-flow.png
│   └── research-summary.png
├── requirements.txt
├── SECURITY.md
└── LICENSE
```

Files will be added incrementally after review and sanitization.

## Public and Private Boundaries

This repository may include:

* High-level system architecture
* Sanitized code examples
* Synthetic sample data
* Aggregate research results
* Selected charts and tables
* Testing examples
* Debugging methodology
* Research findings
* Known limitations

The following will remain private:

* API credentials and private keys
* Exchange-account information
* Raw live-trading records
* Complete production source code
* Proprietary strategy parameters
* Personally identifiable information
* Confidential third-party information
* Material unrelated to the public case study

## Potential Areas of Interest

The project may be relevant to discussions involving:

* Prediction-market execution research
* Market-data infrastructure
* Order and position reconciliation
* Strategy replay and evaluation
* Transaction-cost analysis
* Simulation-versus-live diagnostics
* Python debugging and technical review
* Quantitative research
* Platform testing and feedback
* Research or technical collaboration
* Contract or employment opportunities

## Disclaimer

This repository is provided for technical, research, educational, and professional-review purposes.

It does not provide financial advice, investment recommendations, or representations of future performance. Any market results discussed in this repository are historical, simulated, experimental, or subject to the limitations stated in the supporting documentation.

This is an independent project and is not affiliated with or endorsed by Kalshi.

## Contact

**Ryan Eblen**
AI-Assisted Python Developer and Prediction-Market Systems Researcher
Louisville, Kentucky
[ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)
