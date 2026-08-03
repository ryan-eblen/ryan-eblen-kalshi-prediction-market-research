# Institutional Overview

## Kalshi Prediction-Market Execution and Quantitative Research Platform

**Project lead:** Ryan Eblen
**Location:** Louisville, Kentucky
**Contact:** [ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)
**Repository status:** Private construction and review

## Executive Summary

This project is an independently directed, AI-assisted Python platform for prediction-market execution, quantitative research, and live-system diagnostics on Kalshi.

The platform began as an automated trading system and developed into a broader research environment for investigating:

* Exchange connectivity and market-data processing
* Live and simulated order execution
* Order and position reconciliation
* Prediction-market strategy evaluation
* Predictive-model performance
* Transaction-cost sensitivity
* Portfolio construction
* Simulation-versus-live divergence
* Deterministic and reproducible research workflows

The work combines practical exchange integration with structured quantitative research. It documents not only successful system components, but also execution constraints, research failures, and limitations that materially affected conclusions about deployable profitability.

The public repository is being prepared as a sanitized case study. Complete production code, credentials, private account information, raw trading records, and proprietary strategy details are intentionally excluded.

## Why the Project May Be Relevant

The platform may be relevant to organizations interested in:

* Prediction-market execution infrastructure
* Kalshi API and WebSocket integrations
* Order-state and position-state reconciliation
* Market-data validation
* Live-versus-simulated execution analysis
* Taker-order behavior
* Strategy replay and research tooling
* Transaction-cost and markout analysis
* Predictive-model evaluation
* Platform testing and operational feedback
* Independent prediction-market research
* Technical consulting, contract work, or employment discussions

The project is not presented as a finished commercial trading product or as evidence of guaranteed trading profitability.

Its primary value is the engineering, research, operational knowledge, and documented investigation produced while building and testing a substantial end-to-end prediction-market system.

## Platform Scope

### Exchange Connectivity

The production platform incorporated:

* Kalshi REST API connectivity
* WebSocket market-data ingestion
* Market and contract discovery
* Quote and trade-event processing
* Order submission
* Exchange acknowledgment handling
* Order-status polling
* Execution reconciliation
* Position creation and cleanup
* Structured runtime logging

### Execution Architecture

The execution system was designed to support both simulated and live workflows.

Key components included:

* Signal and opportunity evaluation
* Side and price resolution
* Entry and exit routing
* IOC taker-order submission
* Order-registry creation
* Exchange-order tracking
* Partial- and full-fill interpretation
* Active-position hydration
* Position limits
* Exit processing
* Registry synchronization
* Recovery and cleanup routines

The production execution architecture remained intentionally conservative:

* Production execution used the **YES side only**
* Production entry and exit remained **taker-only**
* The research environment was permitted to evaluate **YES or NO**
* Research execution assumptions remained **taker-only** for both entry and exit

This separation prevented experimental research logic from silently changing the operating production contract.

## Quantitative Research Platform

The research environment expanded beyond the live trading application into a deterministic analytical platform.

It included:

* Dataset construction
* Feature preparation
* Predictive-model training and evaluation
* Strategy-rule discovery
* Historical replay
* Counterfactual price analysis
* Transaction-cost testing
* Side diagnostics
* Ticker diagnostics
* Strategy-family diagnostics
* Time-horizon analysis
* Stability analysis
* Portfolio construction
* Capital allocation
* Performance attribution
* Reproducibility checks
* Source and output certification

## Selected Project Metrics

The following figures describe the scale of the work:

| Measure                                                   |              Project scale |
| --------------------------------------------------------- | -------------------------: |
| Structured AI-assisted development and debugging sessions |              More than 500 |
| Primary production application                            | Approximately 11,000 lines |
| Supporting research, testing, and diagnostic files        |              More than 100 |
| Principal research-dataset decisions                      |                     33,605 |
| Research features                                         |                         32 |
| Systematic strategy configurations evaluated              |                        154 |
| Research portfolio members                                |                         15 |
| Historical strategy matches evaluated                     |      Approximately 967,800 |
| Counterfactual decisions eligible for primary analysis    |                     24,896 |
| Valid quote events used in counterfactual research        |          More than 102,000 |
| Primary markout observations                              |      Approximately 100,000 |
| Distinct observed ticker families                         |                         11 |

These figures are provided to describe engineering and research scope. They are not representations of live profitability.

## Predictive-Model Work

The project replaced an earlier probability model with a structured predictive-model workflow.

The principal certified model used logistic regression and included evaluation of:

* ROC-AUC
* Precision-recall performance
* Accuracy
* Recall
* F1 score
* Probability calibration
* Threshold selection
* Class imbalance
* Feature behavior
* Validation methodology
* Data leakage
* Overfitting risk
* Statistical robustness

The research framework distinguished between model discrimination and economically deployable performance.

A model could classify rare profitable observations effectively while the associated trading strategy still failed to survive transaction costs, execution friction, or market-selection effects.

## Live Execution Investigation

A major portion of the project involved diagnosing divergence between simulated and live execution.

Observed issues included:

* Very low conversion from submitted IOC orders to confirmed executions
* Exchange-confirmed executions that did not always become active internal positions
* Order-registry and active-position synchronization gaps
* Candidate-side initialization ordering
* Pressure-follow logic that appeared partially disconnected
* Internal routing filters that rejected some otherwise eligible opportunities
* The need to distinguish exchange execution status from successful application-state hydration

The investigation required tracing the complete path from:

1. Market signal
2. Candidate selection
3. Side and price resolution
4. Order submission
5. Exchange acknowledgment
6. Order polling
7. Filled-quantity interpretation
8. Position creation
9. Registry synchronization
10. Cleanup and recovery

The work reinforced that prediction-market performance cannot be evaluated solely through signal quality or backtested expected value. Execution conversion, exchange behavior, state consistency, and operational reliability can dominate the result.

A separate sanitized case study will document this investigation in greater detail.

## Research Findings

The research process produced several important conclusions.

### Historical attractiveness did not establish deployable profitability

Some strategy configurations appeared favorable before full execution-cost analysis. Later diagnostics showed that those results did not remain robust under the final tested cost assumptions.

### Execution costs materially changed conclusions

Side, ticker, family, and horizon analysis showed that apparent pre-cost opportunities could become economically negative after realistic entry and exit costs.

### No robust-positive strategy family was certified

The final family-level diagnostics did not identify a strategy family that remained robustly positive across the tested cost levels.

This is treated as a valid research result rather than concealed as a project failure.

### YES and NO required separate analysis

The research environment evaluated both contract sides. NO-side performance was sometimes less adverse than YES-side performance, but the tested cells did not establish a broadly robust positive opportunity.

### Sample size and evidence quality mattered

Many market segments lacked sufficient observations for strong conclusions. The platform therefore separated:

* Negative evidence
* Insufficient evidence
* Moderate stability
* Economic stability
* Research eligibility
* Promotion eligibility

### Simulation could not substitute for live evidence

The live system revealed execution and reconciliation issues that were not fully visible in simulation. This made simulation-versus-live comparison a central component of the platform.

## Research Integrity

The project follows several principles:

* Backtests are not presented as live results.
* Simulated fills are not treated as exchange executions.
* Model quality is not treated as proof of strategy profitability.
* Historical performance is evaluated after estimated costs.
* Negative findings are preserved.
* Insufficient evidence is not converted into a positive conclusion.
* Research and production contracts remain separate.
* Deterministic reruns are used where practical.
* Material limitations are documented.
* Unresolved issues remain visible in technical handoffs.

The objective is to produce defensible research rather than persuasive but unsupported performance claims.

## AI-Assisted Development

The platform was developed through an extensive AI-assisted engineering workflow.

AI tools contributed to:

* Code drafting
* Debugging hypotheses
* Log analysis
* Test design
* Research architecture
* Data-analysis workflows
* Documentation
* Technical handoffs

The project remained directed by explicit requirements, runtime evidence, source inspection, compilation, testing, deterministic reruns, and review of observed outputs.

The repository will be transparent about the distinction between:

* AI-proposed implementation
* Human-directed architecture and requirements
* Observed runtime evidence
* Independently explainable technical understanding
* Remaining areas requiring stronger manual Python fluency

## Current Project Status

The platform has reached a mature research and diagnostic stage.

Completed work includes:

* Exchange integration
* Live and simulated execution paths
* Order and position lifecycle management
* Predictive-model evaluation
* Historical strategy replay
* Counterfactual market-path analysis
* Research portfolio construction
* Capital allocation
* Stability testing
* Side, ticker, horizon, and family diagnostics
* Deterministic research certification
* Extensive debugging of live execution behavior

Current priorities include:

* Curating a safe public case study
* Sanitizing representative code examples
* Building a standalone research notebook
* Documenting execution reconciliation
* Producing architecture diagrams
* Improving independently demonstrable Python fluency
* Evaluating appropriate collaboration, employment, or research discussions

## Potential Discussion Paths

The project may support discussions involving:

### Employment or Contract Work

* Prediction-market research
* Python debugging
* Quantitative analysis
* AI-assisted software development
* Execution-system diagnostics
* Data-quality investigation
* Technical documentation
* Financial-technology analysis

### Institutional or Industry Collaboration

* Kalshi execution research
* Market-maker infrastructure
* Live-versus-simulated execution studies
* Order and position reconciliation
* Transaction-cost research
* Market-data analysis
* Strategy-evaluation tooling
* Platform feedback and testing

### Private Technical Review

Selected additional materials may be discussed privately where appropriate, subject to security, confidentiality, ownership, and commercial considerations.

Public repository access does not include:

* Production credentials
* Complete production source code
* Raw account or order data
* Private infrastructure
* Confidential third-party information
* Complete proprietary strategy parameters

## Independent Status

This is an independent project created by Ryan Eblen.

It is not affiliated with, sponsored by, or endorsed by Kalshi.

References to Kalshi describe the exchange environment for which the system was developed and tested.

## Contact

**Ryan Eblen**
AI-Assisted Python Developer
Prediction-Market Systems Researcher
Louisville, Kentucky
[ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)
