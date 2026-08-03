# Local Reproducibility Verification

## Purpose

This document records an independent local execution of the sanitized portfolio
repository on macOS.

The objective was to confirm that a reviewer can create an isolated Python
environment, install the declared dependencies, run the complete unit-test
suite, and execute every included example without exchange credentials or
account access.

## Verification Environment

| Component           | Verified configuration                           |
| ------------------- | ------------------------------------------------ |
| Operating system    | macOS                                            |
| Python              | 3.13.14                                          |
| Virtual environment | Python `venv` located inside the repository root |
| pip                 | 26.2                                             |
| NumPy               | 2.3.5                                            |
| pandas              | 3.0.5                                            |
| Test framework      | Python `unittest`                                |

The virtual environment was created from the repository root using:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
```

The active interpreter was verified as the Python executable inside:

```text
kalshi-prediction-market-research/.venv/bin/python
```

Dependencies were installed using:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Unit-Test Verification

The complete suite was executed with:

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

Verified result:

```text
Ran 112 tests in 0.191s

OK
```

All tests passed without failures or errors.

The suite covers:

* Expected-value and transaction-cost calculations
* YES and NO contract handling
* Defensive input validation
* Partial and complete fills
* Cumulative-fill reconciliation
* Idempotent duplicate-event handling
* Synthetic strategy evaluation
* Transaction-cost sensitivity
* Data cleaning and malformed-record rejection
* Position and exposure controls
* Duplicate-order prevention
* Daily-loss limits
* Execution-funnel conversion diagnostics

## Executable Example Verification

All six sanitized examples were executed locally.

### Expected-Value Evaluation

```bash
python examples/expected_value_example.py
```

Verified behavior:

* A synthetic YES contract was classified as positive expected value.
* A synthetic NO contract was classified as negative expected value.
* Estimated execution costs were included in the calculations.

### Order Reconciliation

```bash
python examples/order_reconciliation_example.py
```

Verified behavior:

* A partial fill created a position with quantity two.
* Reprocessing the same cumulative snapshot added no duplicate quantity.
* A later full-fill snapshot added only the remaining quantity.
* The final position quantity matched the requested order quantity.

### Strategy Evaluation

```bash
python examples/strategy_evaluation_example.py
```

Verified output:

```text
Synthetic trade rows:       240
Cost-adjusted rows:         720
Strategy-side segments:     6
Robust-positive segments:   0
```

Classification result:

```text
COST_SENSITIVE                 5
NEGATIVE_AT_ALL_COST_LEVELS    1
```

The example demonstrated that positive pre-cost performance did not guarantee
robust post-cost performance.

### Data Validation

```bash
python examples/data_validation_example.py
```

Verified output:

```text
Total rows:   11
Valid rows:   5
Invalid rows: 6
Issues found: 6
```

The validation process correctly identified:

* Duplicate decision identifiers
* An invalid contract side
* An out-of-range market price
* A missing model probability
* An invalid timestamp

### Pre-Trade Risk Controls

```bash
python examples/risk_controls_example.py
```

Verified decisions:

```text
Approved example:          APPROVE
Exposure-rejected example: REJECT
Duplicate-order example:   REJECT
Daily-loss-stop example:   REJECT
```

The correct failed risk rule was reported for each rejected order.

### Execution-Funnel Diagnostic

```bash
python examples/execution_funnel_example.py
```

Verified output:

```text
Submitted orders:           20
Executed orders:            5
Hydrated positions:         3
Submission-to-execution:    25.00%
Execution-to-hydration:     60.00%
End-to-end conversion:      15.00%
```

The diagnostic correctly identified:

```text
Executed, not hydrated:     ('order-004', 'order-005')
Duplicate events ignored:   ('order-001:ORDER_EXECUTED',)
```

## Verification Result

```text
Local macOS verification: PASS
Python 3.13.14: PASS
Unit tests: 112 of 112 passed
Executable examples: 6 of 6 completed successfully
```

The local results were consistent with the automated GitHub Actions workflow,
which separately validates the repository under Python 3.11, 3.12, and 3.13.

## Scope and Limitations

This verification applies only to the sanitized portfolio repository.

It does not verify:

* Live exchange connectivity
* Private production infrastructure
* Exchange credentials or account access
* Proprietary strategy parameters
* Durable trading profitability

All locally executed examples use synthetic or sanitized information.
