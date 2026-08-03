# Technical Case Study

## Building and Diagnosing a Python Prediction-Market Platform

**Project lead:** Ryan Eblen
**Project type:** Independent, AI-assisted software development and quantitative research
**Primary environment:** Kalshi prediction markets
**Contact:** [ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)

## Case-Study Summary

This case study presents the technical work involved in directing, building, testing, and investigating a substantial Python platform for prediction-market execution and quantitative research.

The project grew from an automated trading application into a broader system containing:

* Real-time exchange connectivity
* Live and simulated execution
* Order and position-state management
* Structured diagnostic logging
* Predictive-model evaluation
* Historical strategy replay
* Counterfactual market-path analysis
* Transaction-cost diagnostics
* Research portfolio construction
* Deterministic output certification

The project was developed through more than 500 structured AI-assisted development and debugging sessions.

AI tools contributed to code drafting, problem analysis, test design, documentation, and research workflows. The project remained directed through explicit requirements, observed runtime evidence, source inspection, compilation, testing, and repeated validation.

## Project Objective

The initial objective was to build a Python system capable of:

1. Receiving live prediction-market data
2. Evaluating market opportunities
3. Calculating expected value
4. Submitting orders
5. Monitoring exchange responses
6. Maintaining accurate positions
7. Managing entries and exits
8. Comparing simulation with live results

As implementation progressed, the project revealed that signal generation was only one part of the problem.

A functioning prediction-market system also required:

* Reliable data normalization
* Correct order-state interpretation
* Position reconciliation
* Defensive error handling
* Realistic fill assumptions
* Transaction-cost analysis
* Reproducible research
* Clear separation between experimental and production logic

## Technical Environment

The project used or incorporated:

* Python
* pandas
* NumPy
* REST APIs
* WebSockets
* JSON
* CSV data
* Object-oriented design
* Exception handling
* Structured logging
* Unit and contract testing
* Git-based source control
* Linux command-line workflows
* Logistic regression
* Classification metrics
* Data visualization
* Historical replay
* Deterministic source and output verification

## Project Scale

Selected project measures include:

| Measure                                                   |                      Scale |
| --------------------------------------------------------- | -------------------------: |
| Structured AI-assisted development and debugging sessions |              More than 500 |
| Primary production application                            | Approximately 11,000 lines |
| Supporting research, testing, and diagnostic files        |              More than 100 |
| Principal research-dataset decisions                      |                     33,605 |
| Research features                                         |                         32 |
| Systematic strategy configurations evaluated              |                        154 |
| Research shadow-portfolio members                         |                         15 |
| Historical strategy matches evaluated                     |      Approximately 967,800 |
| Primary counterfactual decisions                          |                     24,896 |
| Primary markout observations                              |      Approximately 100,000 |

These figures describe the scope of the engineering and research work. They do not represent guaranteed or proven trading profitability.

## Responsibilities and Contributions

The project required directing work across several technical disciplines.

### Requirements and Architecture

Responsibilities included:

* Defining production and research behavior
* Separating live and simulated execution
* Defining YES-side production constraints
* Permitting YES-or-NO research analysis
* Maintaining taker-only execution assumptions
* Designing order and position registries
* Establishing research-validation requirements
* Preserving continuity through detailed technical handoffs

### Development and Integration

The system incorporated:

* Exchange API authentication and requests
* WebSocket market-data processing
* Market and contract discovery
* Candidate evaluation
* Order submission
* Exchange acknowledgment handling
* Order-status polling
* Position creation
* Exit processing
* Cleanup and recovery
* Structured event logging

### Debugging and Root-Cause Analysis

The investigation process included:

* Reading tracebacks and runtime logs
* Comparing expected and observed state
* Counting lifecycle events
* Tracing identifiers across system components
* Inspecting source paths
* Forming testable hypotheses
* Applying controlled changes
* Compiling and executing the revised code
* Reviewing before-and-after evidence
* Identifying regression risks

### Quantitative Research

The research process included:

* Dataset validation
* Feature analysis
* Model evaluation
* Strategy-rule discovery
* Historical replay
* Counterfactual markouts
* Transaction-cost analysis
* Side and ticker segmentation
* Time-horizon analysis
* Strategy-family diagnostics
* Portfolio construction
* Stability testing
* Performance attribution
* Deterministic certification

## Selected Engineering Challenge

### Simulation-versus-Live Execution Divergence

One of the project’s most important investigations concerned a major difference between simulated and live trade conversion.

During one diagnostic session, the system recorded:

| Lifecycle event                     | Count |
| ----------------------------------- | ----: |
| Live order-registry creation events | 1,741 |
| Exchange-reconciled executed orders |    14 |
| Recorded live-position entry events |     7 |

The approximate conversion from submitted live orders to exchange-reconciled executions was:

```text
14 / 1,741 ≈ 0.80%
```

This required separating two different questions:

1. Why did so few submitted IOC orders execute?
2. Why did some exchange-reported executions not appear to become active internal positions?

### Investigation Path

The complete lifecycle was traced through:

```text
Candidate generation
        ↓
Side and price resolution
        ↓
Execution routing
        ↓
IOC order submission
        ↓
Internal order-registry creation
        ↓
Exchange acknowledgment
        ↓
Status polling and reconciliation
        ↓
Filled-quantity interpretation
        ↓
Position hydration
        ↓
Active-position registration
        ↓
Cleanup and recovery
```

### Principal Findings

The investigation found or identified evidence of:

* Very low live IOC execution conversion
* Frequent immediate cancellation of unfilled IOC orders
* Gaps between exchange execution and internal position state
* Possible immediate-fill quantity interpretation issues
* Candidate-side information initialized after dependent diagnostics
* Pressure-follow logic that appeared incompletely connected
* A router expected-value floor that rejected some candidates but did not explain the primary execution bottleneck
* Simulation assumptions that required greater live-execution realism

### Engineering Significance

This work demonstrated several important principles:

* Submitted orders are not equivalent to executed orders.
* Exchange executions are not automatically equivalent to valid internal positions.
* Aggregate metrics identify the stage of failure but do not explain individual orders.
* Reconciliation logic must restore missing state without duplicating fills.
* Simulation must model execution conditions rather than only strategy signals.
* Stable identifiers are essential for tracing asynchronous systems.

The full investigation appears in the [Live Execution Debugging Case Study](execution-debugging-case-study.md).

## Previously Resolved Reliability Problems

Before live entry conversion became the primary focus, several other system problems had been resolved or materially improved:

* Exit-submission pipeline failures
* Exit acknowledgment latency
* Position cleanup
* Ghost-position removal
* Position-registry synchronization
* Queue-gate suppression
* Excessive logging that contributed to disk-space pressure

Each correction required protecting related behavior from regression.

For example, modifying position hydration could not be allowed to reintroduce:

* Duplicate positions
* Double-counted fills
* Invalid per-ticker exposure
* Ghost positions
* Broken exits
* Incomplete cleanup

## Predictive-Model Work

The project replaced an earlier probability model with a structured predictive-model workflow.

The principal certified logistic-regression model was evaluated using:

* ROC-AUC
* Precision-recall AUC
* Accuracy
* Precision
* Recall
* F1 score
* Calibration
* Threshold sensitivity
* Class-imbalance analysis
* Overfitting and leakage review

Selected validation results included:

| Metric                     |                Result |
| -------------------------- | --------------------: |
| ROC-AUC                    |                0.9823 |
| Precision-recall AUC       |                0.3435 |
| Accuracy                   |                0.9957 |
| Recall                     |                0.3929 |
| F1 score                   |                0.4314 |
| Expected calibration error | Approximately 0.00044 |
| Selected threshold         |                  0.23 |

The strong classification metrics did not establish trading profitability.

The model was therefore evaluated separately from:

* Execution costs
* Fill probability
* Market selection
* Side behavior
* Holding horizon
* Transaction friction
* Live-system reliability

## Research and Economic Findings

The platform evaluated 154 systematic strategy configurations and constructed a 15-member research shadow portfolio.

Later cost-aware analysis found:

* YES-side results were structurally negative under the tested assumptions.
* NO-side performance was sometimes less adverse but not broadly robust.
* No ticker group was certified as robustly positive.
* No strategy family was certified as robustly positive.
* Many family-level cells lacked sufficient samples.
* Strategy-horizon diagnostics remained negative under the final tested costs.
* Historical portfolio attribution required significant qualification.

These findings were retained rather than removed from the project narrative.

The project demonstrates that negative research can still produce valuable conclusions by identifying:

* Unrealistic fill assumptions
* Weak strategy segments
* Cost sensitivity
* Insufficient samples
* Execution bottlenecks
* Areas requiring stronger evidence

## Data and Research Reliability

The research platform used controls including:

* Required-column validation
* Data-type checks
* Invalid-price detection
* Side validation
* Timestamp validation
* Join-coverage checks
* Expected row counts
* Source hashes
* Output hashes
* Repeated deterministic runs
* Diagnostic signatures
* Explicit pass-or-fail results

A reproducible result was not automatically treated as an economically favorable result.

Certification meant that the output could be regenerated consistently from the specified source—not that the strategy was approved for live capital.

## AI-Assisted Development Process

The project was built using a structured AI-assisted workflow.

A typical development cycle included:

1. Define the intended behavior.
2. Identify the relevant source path.
3. Inspect logs or runtime output.
4. Form one or more hypotheses.
5. Draft or revise an implementation.
6. Compile the affected source.
7. Execute a controlled test.
8. Compare expected and observed results.
9. Inspect downstream effects.
10. Record a detailed technical handoff.

AI assistance accelerated code generation and investigation, but proposed solutions were not treated as correct merely because they appeared plausible.

Validation required observable evidence.

## Skills Demonstrated

The project demonstrates practical experience with:

### Python and Data

* Python application development
* pandas and NumPy analysis
* JSON and CSV handling
* Data validation
* Aggregation
* Joins
* Missing-data analysis
* Analytical reporting

### Systems and APIs

* REST API workflows
* WebSocket processing
* Exchange-order lifecycles
* Polling and reconciliation
* State synchronization
* Position management
* Asynchronous-system reasoning

### Debugging

* Root-cause analysis
* Traceback interpretation
* Structured logging
* Lifecycle-event counting
* Source-path inspection
* Defensive coding
* Regression-risk analysis
* Runtime validation

### Quantitative Research

* Logistic regression
* Classification metrics
* Calibration
* Threshold selection
* Strategy replay
* Counterfactual analysis
* Transaction-cost sensitivity
* Portfolio research
* Stability and concentration analysis

### Documentation

* Technical handoffs
* Architecture documentation
* Research methodology
* Findings and limitations
* Clear separation of verified results from unresolved assumptions

## Limitations

The project also has important limitations:

* The complete production source is private.
* Public examples are sanitized and simplified.
* Full liquidity-path evidence was unavailable.
* Counterfactual markouts were not exchange fills.
* Simulated and live execution diverged materially.
* The positive profitability class was rare.
* NO-side evidence was limited.
* Many strategy segments lacked sufficient samples.
* Transaction-cost assumptions remained estimates.
* The project was extensively AI-assisted.
* Independently demonstrable Python fluency remains an active development objective.
* Durable live profitability was not established.

These limitations are part of the case study rather than omitted from it.

## Relevance to Employment and Contract Work

The project may be relevant to work involving:

* AI-generated-code evaluation
* Python debugging
* Data analysis
* Financial technology
* Prediction-market research
* Trading-system diagnostics
* API integration
* Execution reconciliation
* Research automation
* Technical documentation
* Model evaluation
* Quantitative support

The repository is designed to let a reviewer assess the reasoning, architecture, methodology, and documented evidence without exposing credentials, private account information, or the complete production system.

## Related Documentation

* [Main Project Overview](../README.md)
* [Institutional Overview](institutional-overview.md)
* [System Architecture](architecture.md)
* [Live Execution Debugging Case Study](execution-debugging-case-study.md)
* [Quantitative Research Methodology](research-methodology.md)
* [Findings and Limitations](findings-and-limitations.md)
* [Repository Security Policy](../SECURITY.md)

## Contact

**Ryan Eblen**
AI-Assisted Python Developer
Prediction-Market Systems Researcher
Louisville, Kentucky
[ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)
