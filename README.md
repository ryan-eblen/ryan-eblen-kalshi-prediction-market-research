# Kalshi Prediction-Market Research Platform

[![Python tests](https://github.com/ryan-eblen/kalshi-prediction-market-research/actions/workflows/python-tests.yml/badge.svg)](https://github.com/ryan-eblen/kalshi-prediction-market-research/actions/workflows/python-tests.yml)

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

## Executable Portfolio Examples

This repository includes sanitized, deterministic examples based on engineering
patterns developed during the larger private platform project.

| Example | Demonstrates |
|---|---|
| `expected_value_example.py` | Cost-aware expected-value calculations for YES and NO contracts |
| `order_reconciliation_example.py` | Partial fills, cumulative fills, position hydration, and idempotent reconciliation |
| `strategy_evaluation_example.py` | Synthetic pandas/NumPy research, transaction-cost scenarios, and cross-cost classification |
| `data_validation_example.py` | Schema validation, normalization, malformed-record rejection, and issue reporting |
| `risk_controls_example.py` | Position limits, exposure limits, duplicate-order prevention, side restrictions, and daily-loss controls |
| `execution_funnel_example.py` | Submitted-order, exchange-execution, and internal-position conversion diagnostics |

All examples use synthetic or sanitized data. They do not contain exchange
credentials, account information, private production logs, or proprietary
strategy parameters.

## Automated Verification

Every push and pull request runs an automated GitHub Actions workflow across:

- Python 3.11
- Python 3.12
- Python 3.13

The current suite contains **112 unique unit tests**, representing **336 test
executions per workflow run** across the three-version matrix.

The tests cover:

- Expected-value and transaction-cost calculations
- Input validation and defensive coding
- Partial and full order fills
- Idempotent duplicate-event handling
- Order-to-position reconciliation
- Synthetic strategy evaluation
- Cost-sensitive performance classification
- Market-data cleaning and normalization
- Pre-trade risk controls
- Execution-funnel conversion diagnostics

The workflow also executes the strategy-evaluation, data-validation, risk-control, and execution-funnel examples and verifies their reported results. The expected-value and order-reconciliation modules are validated through their dedicated unit tests.

Latest verified status:

```text
112 tests passed
Python 3.11: PASS
Python 3.12: PASS
Python 3.13: PASS
```
## Quick Start

The commands below create an isolated Python environment inside the cloned
repository. Run the commands from the macOS Terminal application.

### 1. Install the macOS Command Line Tools

Git and other required command-line utilities are provided through Apple’s
Command Line Tools.

```bash
xcode-select --install
```

Allow the installation to finish, then verify it:

```bash
xcode-select -p
git --version
```

A successful `xcode-select -p` result normally displays:

```text
/Library/Developer/CommandLineTools
```

### 2. Create a Local GitHub Projects Folder

```bash
mkdir -p ~/Documents/GitHub
cd ~/Documents/GitHub
```

Confirm the current location:

```bash
pwd
```

The result should resemble:

```text
/Users/your-username/Documents/GitHub
```

### 3. Clone the Repository

```bash
git clone https://github.com/ryan-eblen/kalshi-prediction-market-research.git
cd kalshi-prediction-market-research
```

Because the repository may be private during portfolio development, GitHub may
request authentication. Follow the GitHub sign-in or browser-authentication
prompt. Do not place credentials or access tokens inside the repository.

After entering the repository, confirm the location:

```bash
pwd
```

The path should end with:

```text
/Documents/GitHub/kalshi-prediction-market-research
```

Confirm the repository files are present:

```bash
ls
```

The output should include:

```text
README.md
SECURITY.md
docs
examples
requirements.txt
tests
```

### 4. Confirm the Python Version

```bash
python3 --version
```

The automated workflow tests Python 3.11, 3.12, and 3.13.

### 5. Create the Virtual Environment

Create the virtual environment from the repository root—the folder containing
`README.md`, `requirements.txt`, `examples/`, and `tests/`.

```bash
python3 -m venv .venv
```

This creates the local environment here:

```text
kalshi-prediction-market-research/.venv/
```

Do not create `.venv` inside `examples/`, `tests/`, or `docs/`. The `.venv`
directory is local development infrastructure and should not be committed to
GitHub.

### 6. Activate the Virtual Environment

On macOS or Linux:

```bash
source .venv/bin/activate
```

A successful activation normally adds `(.venv)` to the Terminal prompt.

Confirm that Python is running from the repository environment:

```bash
which python
```

The path should end with:

```text
kalshi-prediction-market-research/.venv/bin/python
```

On Windows PowerShell, use:

```powershell
.venv\Scripts\Activate.ps1
```

### 7. Install the Dependencies

With the virtual environment active:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 8. Run the Full Test Suite

Run this command from the repository root:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Expected result:

```text
Ran 112 tests

OK
```

### 9. Run the Executable Examples

```bash
python examples/expected_value_example.py
python examples/order_reconciliation_example.py
python examples/strategy_evaluation_example.py
python examples/data_validation_example.py
python examples/risk_controls_example.py
python examples/execution_funnel_example.py
```

All examples use synthetic or sanitized information. They require no exchange
credentials or account access.

### 10. Deactivate the Environment

When finished:

```bash
deactivate
```

The `(.venv)` indicator will disappear from the Terminal prompt.

For a recorded local execution result, see
[Local Reproducibility Verification](docs/local-verification.md).

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

The dedicated execution-debugging case study documents this investigation without exposing account information, private logs, credentials, or complete production logic.

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

## Current Repository Structure

```text
kalshi-prediction-market-research/
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── docs/
│   ├── architecture.md
│   ├── execution-debugging-case-study.md
│   ├── findings-and-limitations.md
│   ├── institutional-overview.md
│   ├── local-verification.md
│   ├── research-methodology.md
│   └── technical-case-study.md
├── examples/
│   ├── data_validation_example.py
│   ├── execution_funnel_example.py
│   ├── expected_value_example.py
│   ├── order_reconciliation_example.py
│   ├── risk_controls_example.py
│   └── strategy_evaluation_example.py
├── tests/
│   ├── test_data_validation.py
│   ├── test_execution_funnel.py
│   ├── test_expected_value.py
│   ├── test_order_reconciliation.py
│   ├── test_risk_controls.py
│   └── test_strategy_evaluation.py
├── README.md
├── requirements.txt
└── SECURITY.md
```

Additional sample data, visual assets, collaboration materials, and licensing information may be added after review and sanitization.

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
