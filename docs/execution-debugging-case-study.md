# Live Execution and Position-Reconciliation Debugging Case Study

## Executive Summary

This case study documents a major investigation into divergence between simulated and live execution in an independently developed Kalshi prediction-market trading system.

The system was generating substantial live order-submission activity, but only a small percentage of submitted IOC orders produced exchange-confirmed executions. A second discrepancy appeared between exchange-confirmed executions and positions successfully represented inside the application.

The investigation required tracing the complete order lifecycle across exchange communication, internal registries, fill interpretation, position hydration, cleanup, and recovery logic.

The work demonstrated that trading-system performance cannot be evaluated solely from signal quality, expected value, or simulated fills. Exchange behavior, order-state reconciliation, position-state consistency, and internal lifecycle management can materially determine whether an apparent opportunity becomes an actual position.

## System Context

The production application included:

* Real-time Kalshi market data
* REST API order submission
* WebSocket data processing
* Signal and opportunity evaluation
* Side and price resolution
* IOC taker-order execution
* Internal order registry
* Active-position registry
* Exchange-order polling
* Partial- and full-fill processing
* Position creation
* Exit processing
* Cleanup and recovery routines
* Structured diagnostic logging

The production contract remained intentionally constrained:

* Live production entries used the YES side
* Entry and exit execution remained taker-only
* IOC orders were used for live taker execution
* Research logic was isolated from the production execution contract

## Initial Problem

Simulation showed substantially more successful trade conversion than live execution.

The initial question was:

> Why were opportunities that appeared executable in simulation failing to become live positions?

The investigation eventually separated that broad question into two distinct problems:

1. Why were so few submitted live orders receiving confirmed exchange executions?
2. Why did some exchange-confirmed executions not appear to become active internal positions?

These problems required different forms of evidence and could not be treated as a single fill-rate issue.

## Observed Diagnostic Metrics

During one live diagnostic session, the structured logs showed:

| Diagnostic event                                | Observed count |
| ----------------------------------------------- | -------------: |
| Live order-registry creation events             |          1,741 |
| Exchange-reconciled orders reported as executed |             14 |
| Live position-entry events                      |              7 |

The approximate exchange execution conversion during that session was:

```text
14 executed orders / 1,741 submitted orders ≈ 0.80%
```

The difference between 14 exchange-reconciled executions and 7 recorded live-entry events required further investigation.

The counts did not automatically prove that every executed event should have created a new position. They established that the lifecycle needed to be traced at the individual-order level.

## Why the Metrics Mattered

The three counts represented different stages:

### Order-Registry Creation

An order-registry event showed that the application had created an internal record associated with a live order-submission attempt.

It did not prove that:

* The exchange accepted the order
* The order remained active
* The order executed
* The application created a position

### Exchange-Reconciled Execution

An executed reconciliation event indicated that the exchange status was interpreted as executed.

It did not automatically prove that:

* The correct filled quantity was captured
* The order was associated with the correct trade identifier
* A position object was created
* The position entered the active-position registry
* Per-ticker limits permitted registration
* Cleanup logic did not later remove the position

### Live Position Entry

A live-entry event indicated that the application had reached its position-creation or entry-registration path.

This was the closest of the three metrics to an internally recognized live position, but it still required validation against:

* Exchange execution records
* Active-position state
* Position-by-ticker state
* Order-registry state
* Exit and cleanup behavior

## Investigation Map

The debugging process traced the lifecycle through the following sequence:

1. Candidate opportunity generated
2. Candidate side selected
3. Entry price resolved
4. Execution mode selected
5. IOC order submitted
6. Internal order record created
7. Exchange acknowledgment received
8. Order polled or reconciled
9. Exchange status interpreted
10. Filled quantity calculated
11. Partial- or full-fill branch selected
12. Position object created
13. Position stored in the active-position registry
14. Per-ticker registry updated
15. Entry event logged
16. Cleanup and recovery logic monitored

This prevented the investigation from treating “order sent” and “position opened” as equivalent events.

## Previously Resolved Reliability Problems

Before the live-entry divergence investigation became the primary focus, several separate execution and state-management issues had already been addressed:

* Exit-submission pipeline failures
* Exit acknowledgment latency
* Position cleanup
* Ghost-position removal
* Position-registry synchronization
* Queue-gate suppression
* Excessive logging that contributed to disk-space pressure

Resolving these issues narrowed the investigation toward live entry conversion and position hydration.

## Principal Findings

## 1. Live Entry Conversion Was Extremely Low

The observed executed-order conversion was approximately 0.80% during the referenced session.

This suggested that the primary live constraint was not simply whether the strategy produced candidates. The system was submitting orders, but most IOC orders were not becoming confirmed executions.

This shifted attention toward:

* IOC price selection
* Available displayed liquidity
* Quote movement
* Submission latency
* Marketability at arrival
* Exchange cancellation behavior
* Stale or optimistic simulation assumptions

## 2. Many IOC Orders Canceled Immediately

IOC orders are designed to execute immediately against available liquidity and cancel any unfilled quantity.

A high cancellation rate can therefore be valid exchange behavior rather than an application error.

However, the difference between simulated and live conversion raised questions about whether the simulation accurately represented:

* Available quantity
* Queue competition
* Quote lifetime
* Price movement before arrival
* Partial fills
* Taker execution conditions

The investigation therefore treated immediate IOC cancellation as both an execution-quality issue and a simulation-modeling issue.

## 3. Some Executed Orders Appeared Not to Hydrate Into Positions

Structured reconciliation logs included executed orders for which no active position was visible at the time of reconciliation.

This indicated a possible gap between:

```text
Exchange execution
        ↓
Filled-quantity interpretation
        ↓
Position creation
        ↓
Active-position registration
```

Potential failure points included:

* Incorrect `filled_qty` interpretation
* A zero or stale `filled_now` calculation
* Trade-identifier mismatch
* Missing pending-fill context
* Entry and exit order confusion
* Position-limit rejection
* Existing ticker-position state
* Failure to update all position registries
* Cleanup logic running before state became consistent

The highest-value next investigation was to explain why the observed exchange-executed events did not produce the same number of live-entry events.

## 4. Candidate-Side Initialization Occurred Too Late

The candidate-side hint was assigned after some pressure and queue diagnostics had already executed.

As a result, diagnostic output could show:

```text
candidate_side = null
```

even when a side was later available.

This ordering issue could affect:

* Pressure-follow evaluation
* Queue diagnostics
* Side-specific filters
* Interpretation of why a candidate was accepted or rejected

The corrective direction was to initialize the candidate side before any logic that depended on it.

## 5. Pressure-Follow Logic Appeared Partially Disconnected

The code contained pressure-follow concepts and diagnostics, but observed behavior suggested that the pressure signal was not consistently influencing the final live-entry path.

The investigation therefore distinguished among:

* Signal computed
* Signal logged
* Signal included in candidate evaluation
* Signal used by routing
* Signal used by final execution selection

A component can appear present in code without being functionally connected to the final decision path.

## 6. The Router Expected-Value Floor Was Active but Not the Primary Bottleneck

An expected-value floor remained active in the router and rejected some opportunities.

This was a valid area for review, but the session evidence showed that a much larger number of orders were already reaching submission and then failing to execute.

Therefore:

* The router threshold could suppress valid candidates.
* It did not explain the very low conversion of already-submitted orders.
* It was treated as a secondary constraint rather than the principal cause of live divergence.

## Immediate Fill and Reconciliation Paths

Two code regions became especially important.

### Immediate Fill Path

The immediate-fill logic needed to determine:

* Whether the order response already contained execution information
* Whether `filled_now` was calculated correctly
* Whether an immediately executed IOC order bypassed later hydration logic
* Whether partial fills were preserved
* Whether position creation occurred exactly once

### Reconciliation Path

The reconciliation logic needed to determine:

* Whether exchange status values were normalized correctly
* Whether `EXECUTED` and `FILLED` were treated consistently
* Whether cumulative and incremental quantities were distinguished
* Whether order-registry records contained the required trade context
* Whether a position already existed
* Whether a missing position should be created during reconciliation
* Whether repeated polling could duplicate a fill

The critical design requirement was idempotency:

> Reprocessing an exchange execution should restore missing internal state without creating duplicate positions or double-counting quantity.

## Debugging Methodology

The investigation followed a structured process.

### 1. Instrument the Lifecycle

Structured log events were used to count and connect:

* Order creation
* Exchange acknowledgment
* Exchange status
* Filled quantity
* Position existence
* Position creation
* Cleanup

### 2. Compare Stage Counts

Aggregate counts identified where conversion collapsed.

The large difference between order creation and exchange execution pointed toward execution quality.

The difference between exchange execution and position entry pointed toward state hydration.

### 3. Inspect Individual Orders

Aggregate metrics were insufficient.

Individual executed orders needed to be traced using:

* Exchange order identifier
* Client order identifier
* Internal trade identifier
* Ticker
* Side
* Price
* Requested quantity
* Filled quantity
* Order-registry status
* Active-position status

### 4. Separate Exchange Behavior From Application Behavior

The process distinguished:

* An order that legitimately failed to execute
* An exchange execution that the application failed to record
* An internal position that was created and later removed
* A duplicated or stale registry record
* A simulation assumption that did not match live market behavior

### 5. Preserve Existing Fixes

Changes to entry hydration could not regress:

* Exit handling
* Position cleanup
* Ghost removal
* Per-ticker limits
* Registry synchronization
* Partial-fill handling

### 6. Validate With Runtime Evidence

A proposed code correction was not considered complete merely because it compiled.

Validation required:

* New diagnostic logging
* Controlled live or simulated test cases
* Before-and-after event counts
* Registry inspection
* Position-state inspection
* Duplicate-prevention checks
* Cleanup verification

## Engineering Lessons

## Submitted Does Not Mean Executed

Order-submission count is an activity metric, not an execution-performance metric.

## Executed Does Not Mean Hydrated

The exchange can report execution while the application remains internally inconsistent.

## Simulation Must Model Execution, Not Just Signals

A simulated strategy can appear attractive if it assumes fills that would not occur under live IOC behavior.

## Internal State Requires Reconciliation

Distributed exchange systems cannot rely entirely on a single immediate API response. Polling, reconciliation, recovery, and idempotent state repair are necessary.

## Logs Need Stable Identifiers

Without consistent identifiers across submission, exchange acknowledgment, reconciliation, and position creation, debugging becomes probabilistic rather than deterministic.

## Negative Results Are Operationally Valuable

Discovering that execution conversion is too low, or that a simulated fill model is unrealistic, can prevent capital deployment based on misleading research.

## Skills Demonstrated

This investigation required:

* Python source inspection
* Large-codebase navigation
* API workflow analysis
* Order-lifecycle reasoning
* State-machine debugging
* Structured logging
* Quantitative diagnostics
* Root-cause isolation
* Simulation-versus-live comparison
* Defensive coding
* Regression-risk analysis
* Technical documentation
* AI-assisted debugging with human-directed validation

## Current Status

The following areas were resolved or materially improved before this case study:

* Exit submission
* Exit acknowledgment handling
* Position cleanup
* Ghost-position removal
* Registry synchronization
* Queue-gate suppression
* Logging-related disk pressure

The primary unresolved or partially resolved areas at the referenced handoff were:

* Low IOC execution conversion
* Exchange execution-to-position hydration
* Immediate-fill quantity interpretation
* Candidate-side initialization order
* Pressure-follow integration
* Router-threshold review
* More realistic simulation of live execution

This document records the state of the investigation at that time. It does not claim that every listed issue represented a confirmed software defect; some reflected valid exchange behavior, incomplete instrumentation, or modeling limitations.

## Confidentiality and Sanitization

This case study intentionally excludes:

* API credentials
* Private keys
* Account identifiers
* Raw order identifiers
* Complete live logs
* Exact production configuration
* Complete source code
* Proprietary strategy parameters
* Personal trading records

The aggregate metrics and generalized system paths are presented to demonstrate the debugging and analytical process without exposing the private production environment.

## Conclusion

The central finding was that live trading performance depended on more than identifying attractive market opportunities.

A complete prediction-market execution system had to:

* Submit marketable orders
* Interpret exchange responses correctly
* Reconcile delayed or partial executions
* Create positions reliably
* Maintain consistent registries
* Avoid duplicate hydration
* Recover from incomplete state
* Measure live behavior independently from simulation

The investigation transformed a broad question—“Why is live performance different?”—into specific, testable problems involving execution conversion, state hydration, routing, and simulation realism.

That process became one of the platform’s strongest examples of applied debugging, quantitative investigation, and production-system reasoning.
