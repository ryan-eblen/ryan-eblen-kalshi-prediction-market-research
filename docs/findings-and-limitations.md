# Findings, Limitations, and Current Conclusions

## Kalshi Prediction-Market Research Platform

This document summarizes the principal findings, verified accomplishments, unresolved limitations, and current economic conclusions produced by the independently developed Kalshi prediction-market execution and quantitative research platform.

The purpose is to distinguish clearly between:

* What the system demonstrably accomplished
* What the research evidence supports
* What remains uncertain
* What the project does not claim

## Executive Conclusion

The project successfully developed a substantial end-to-end prediction-market execution and research environment.

It demonstrated the ability to:

* Connect to Kalshi through REST APIs and WebSockets
* Process real-time market data
* Submit and reconcile live IOC orders
* Maintain order and position state
* Diagnose simulation-versus-live divergence
* Build and validate a structured research dataset
* Evaluate predictive models
* Discover and replay systematic strategy rules
* Construct a research shadow portfolio
* Analyze transaction costs, market sides, tickers, horizons, and strategy families
* Produce deterministic and reproducible analytical outputs

The research did not establish a robust, broadly deployable strategy family that remained positive under the final tested execution-cost assumptions.

That is treated as a valid and important research conclusion.

## Verified Project Accomplishments

## 1. End-to-End Exchange Integration

The private production platform incorporated:

* Kalshi REST API connectivity
* WebSocket market-data ingestion
* Market and contract discovery
* Quote and trade-event processing
* Live order submission
* Exchange acknowledgment handling
* Order-status polling
* Execution reconciliation
* Position creation and cleanup
* Entry and exit processing
* Structured runtime diagnostics

This moved the project beyond a theoretical backtest or isolated notebook.

The system interacted with a live prediction-market exchange and produced evidence about actual execution behavior.

## 2. Live and Simulated Execution Paths

The platform maintained separate simulated and live execution workflows.

This made it possible to investigate:

* Whether a strategy candidate was generated
* Whether the candidate passed the router
* Whether an order was submitted
* Whether the exchange executed the order
* Whether the application created a corresponding position
* Whether simulated assumptions matched observed live behavior

The comparison revealed material divergence between simulation and live execution.

## 3. Execution-System Reliability Improvements

Several execution and state-management problems were resolved or materially improved during development:

* Exit-submission failures
* Exit acknowledgment latency
* Position cleanup
* Ghost-position removal
* Position-registry synchronization
* Queue-gate suppression
* Logging-related disk-space pressure

These corrections improved the system’s ability to maintain internal consistency and narrowed the remaining investigation toward live entry conversion and position hydration.

## 4. Structured Research Dataset

The principal research dataset contained:

| Measure                     |              Value |
| --------------------------- | -----------------: |
| Market decisions            |             33,605 |
| Research features           |                 32 |
| Primary profitability label | `label_profitable` |
| Positive observations       |                204 |

The dataset supported model evaluation, strategy discovery, replay, counterfactual analysis, and segment-level diagnostics.

The rare positive class required careful interpretation of accuracy, recall, precision-recall performance, calibration, and threshold behavior.

## 5. Predictive-Model Evaluation

The principal certified logistic-regression model produced strong discrimination within the evaluated dataset.

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

These results established that the model could rank or identify rare labeled observations effectively within the tested data.

They did not establish that trades based on the model would remain profitable after transaction costs and live execution constraints.

## 6. Systematic Strategy Discovery

The research platform evaluated 154 systematic strategy configurations.

The process included:

* Explicit rule construction
* Feature thresholds
* Predicate diagnostics
* Match-count validation
* Coverage analysis
* Duplicate and overmatch review
* Strategy identifiers
* Strategy-family classification

This replaced informal signal interpretation with structured and reproducible strategy definitions.

## 7. Historical Replay at Scale

The research replay process evaluated approximately 967,800 historical strategy matches.

Selected eligibility and evidence counts included:

| Replay measure                                     | Approximate count |
| -------------------------------------------------- | ----------------: |
| Historical strategy matches                        |           967,800 |
| YES-side eligibility observations                  |           174,664 |
| NO-side eligibility observations                   |             9,912 |
| Historical YES taker-evidence observations         |            41,958 |
| Historical taker outcomes                          |             8,507 |
| YES observations requiring counterfactual analysis |           132,706 |

A strategy match was not automatically treated as an executed trade.

The research required execution or market-path evidence before assigning economic meaning.

## 8. Counterfactual Market-Path Analysis

The platform constructed a counterfactual research path for decisions without sufficient direct historical execution evidence.

Selected results included:

| Counterfactual measure           |                 Count |
| -------------------------------- | --------------------: |
| Primary eligible decisions       |                24,896 |
| Valid quote events               |     More than 102,000 |
| Primary markout observations     | Approximately 100,000 |
| Selected invalid quotes          |                     0 |
| Source invalid quotes identified |                     4 |

The principal price path was certified for the referenced analysis.

Complete liquidity-path evidence was not available and was not represented as confirmed.

## 9. Historical Taker-Evidence Analysis

One closed taker-evidence subset contained 765 observations.

Selected descriptive results included:

| Measure                     |                      Result |
| --------------------------- | --------------------------: |
| Closed taker observations   |                         765 |
| Mean entry price            |        Approximately 0.3015 |
| Median entry price          |                        0.27 |
| Mean exit price             |        Approximately 0.3841 |
| Median exit price           |                        0.28 |
| Mean observed P&L           |        Approximately 0.0626 |
| Median observed P&L         |                       -0.02 |
| Mean observed hold duration | Approximately 0.364 seconds |

The positive mean and negative median showed that the distribution was skewed.

The sub-second mean hold duration applied only to this specific set of closed historical taker observations. It should not be interpreted as the universal holding period of every strategy evaluated by the platform.

The short observed duration increased the importance of:

* Order-submission latency
* Quote movement
* Immediate fill handling
* Position hydration
* Round-trip execution cost
* Accurate timestamp processing

## 10. Research Shadow Portfolio

The platform constructed a 15-member research shadow portfolio.

Selected portfolio properties included:

| Portfolio measure        |               Result |
| ------------------------ | -------------------: |
| Portfolio members        |                   15 |
| Total research weight    |               1.0000 |
| Minimum strategy weight  |                3.00% |
| Maximum strategy weight  |  Approximately 9.73% |
| Top-three concentration  | Approximately 28.25% |
| Effective strategy count |  Approximately 13.46 |

The portfolio was created for structured research comparison.

It did not represent automatic production deployment or a claim of live portfolio profitability.

## 11. Stability Diagnostics

Within the selected research portfolio:

| Stability classification | Count |
| ------------------------ | ----: |
| Economically stable      |    12 |
| Moderately stable        |     3 |

These classifications described stability according to the platform’s diagnostic rules.

“Economically stable” did not mean that the strategy was positive after all final execution-cost assumptions.

A strategy could be consistently negative and still exhibit stable behavior.

## 12. Deterministic Certification

The research platform used:

* Source hashes
* Output hashes
* Repeated deterministic runs
* Schema validation
* Row-count assertions
* Diagnostic signatures
* Certified output directories
* Explicit pass-or-fail statuses

This demonstrated that analytical results could be regenerated consistently from the same source inputs.

Certification represented reproducibility.

It did not represent automatic approval for capital deployment.

## Principal Economic Findings

## 1. Predictive Strength Did Not Guarantee Trading Profitability

The model produced strong classification metrics, but the economic analysis showed that predictive performance and trading profitability were separate questions.

A model may successfully rank rare outcomes while a strategy based on those outcomes remains uneconomic because of:

* Spread
* Entry cost
* Exit cost
* Fill uncertainty
* Execution delay
* Market selection
* Position limits
* Adverse price movement

## 2. Transaction Costs Changed the Conclusions

Some strategy configurations appeared attractive before full execution-cost analysis.

When progressively less favorable cost assumptions were introduced, the apparent advantage deteriorated.

This demonstrated that strategy evaluation could not stop at pre-cost historical P&L.

## 3. YES-Side Performance Was Structurally Negative

The final side diagnostics classified YES-side performance as structurally negative under the tested cost assumptions.

This was especially important because the production execution architecture remained YES-side only.

The research result therefore did not support automatic promotion of the tested research strategies into the production contract.

## 4. NO-Side Performance Was Less Adverse but Not Robustly Positive

The research environment was permitted to evaluate both YES and NO.

NO-side results were sometimes less adverse than YES-side results.

However:

* NO-side evidence was much smaller.
* The tested cells did not establish broad robust profitability.
* Less adverse did not mean positive.
* Insufficient evidence was not treated as approval.

## 5. No Robust-Positive Ticker Group Was Certified

Ticker-level diagnostics covered 11 observed ticker families.

Selected classifications included:

* Negative at all tested cost levels
* Insufficient sample
* No robust-positive ticker classification

This indicated that favorable aggregate results were not supported by a clearly durable ticker segment under the final tested framework.

## 6. No Robust-Positive Strategy Family Was Certified

The final family-level analysis included:

| Family diagnostic measure                   | Count |
| ------------------------------------------- | ----: |
| Strategy-family groups evaluated            |    44 |
| Family classifications                      |   352 |
| Insufficient-sample classifications         |   232 |
| Negative-at-all-cost-levels classifications |   119 |
| Robust-positive classifications             |     0 |

Selected final dispositions included:

| Disposition               | Count |
| ------------------------- | ----: |
| Insufficient evidence     |    29 |
| Less adverse but negative |     4 |

No strategy family was approved as robustly positive across the tested cost framework.

## 7. Strategy-Horizon Diagnostics Were Negative

The primary strategy-horizon diagnostic matrix classified the tested strategy-horizon groups as negative across the evaluated cost levels.

This reduced the likelihood that the aggregate result was hiding a clearly superior holding horizon.

## 8. Apparent Portfolio P&L Required Qualification

One research attribution run produced aggregate historical P&L of approximately 33.6006 under its defined assumptions.

That result was useful for portfolio attribution and debugging.

It was not sufficient evidence of deployable profitability because later diagnostics showed:

* Cost sensitivity
* Negative side-level results
* Negative ticker-level results
* No robust-positive family
* Incomplete liquidity-path evidence
* Live execution divergence

The project therefore does not present the attribution result as confirmed alpha.

## Live Execution Findings

## 1. IOC Execution Conversion Was Very Low

During one diagnostic session:

| Event                               | Count |
| ----------------------------------- | ----: |
| Live order-registry creations       | 1,741 |
| Exchange-reconciled executed orders |    14 |
| Recorded live-entry events          |     7 |

The approximate exchange execution conversion was:

```text
14 / 1,741 ≈ 0.80%
```

This showed that generating and submitting candidates did not guarantee successful live execution.

## 2. Many IOC Orders Canceled Without Execution

IOC orders legitimately cancel when sufficient marketable liquidity is not available immediately.

The high cancellation rate raised questions about:

* Price marketability
* Quote lifetime
* Submission latency
* Available quantity
* Queue competition
* Simulation assumptions
* Market movement between decision and arrival

Not every cancellation represented a software defect.

Some represented the real execution environment that the simulation needed to model more accurately.

## 3. Exchange Execution and Internal Position State Diverged

The difference between 14 exchange-reconciled executions and 7 live-entry events indicated that the execution-to-position lifecycle required deeper inspection.

Potential causes included:

* Filled-quantity interpretation
* Incremental-versus-cumulative fill handling
* Trade-identifier mismatch
* Existing position state
* Position-limit rejection
* Missing pending-fill context
* Immediate-fill path behavior
* Cleanup timing
* Incomplete instrumentation

The counts established an investigation target.

They did not independently prove that all seven missing events represented software defects.

## 4. Candidate-Side Initialization Was Ordered Too Late

Candidate-side information was assigned after some diagnostics that depended on it.

This could produce incomplete side-aware logging and potentially interfere with pressure or queue logic.

The corrective direction was to initialize the side before dependent evaluation and diagnostics.

## 5. Some Logic Appeared Present but Not Fully Connected

Pressure-follow concepts and logs existed, but observed runtime behavior suggested that the signal was not consistently influencing final routing.

This demonstrated an important engineering distinction:

* A value can be calculated.
* A value can be logged.
* A value can still fail to affect the final system decision.

## Primary Limitations

## 1. Full Liquidity-Path Evidence Was Unavailable

The counterfactual analysis had stronger evidence for price movement than for executable quantity.

A future quote price does not prove that the intended order size could have executed at that price.

## 2. Counterfactual Markouts Were Not Exchange Fills

Counterfactual analysis measured subsequent market paths.

It did not prove:

* Order priority
* Queue position
* Available quantity
* Exact fill timing
* Full-size execution
* Realized slippage

## 3. Live and Simulated Fill Models Diverged

Simulation produced more successful trade conversion than the live IOC path.

Until the simulation reflected live execution more accurately, simulated performance required substantial discounting.

## 4. The Positive Class Was Rare

Only 204 of 33,605 principal dataset decisions carried the positive profitability label.

This created risks involving:

* Unstable minority-class estimates
* Threshold sensitivity
* Overstated accuracy
* Small-sample segmentation
* Strategy overfitting

## 5. NO-Side Evidence Was Limited

NO-side eligibility was far smaller than YES-side eligibility.

NO-side results therefore required stronger sample accumulation before broad conclusions could be supported.

## 6. Many Family Cells Had Insufficient Samples

A large share of the family-level classifications lacked enough evidence for a strong conclusion.

The platform preserved those cells as insufficient rather than treating missing evidence as positive.

## 7. Related Strategies Were Not Fully Independent

Many of the 154 strategies used related features, thresholds, or rule structures.

The number of strategy configurations should not be interpreted as 154 independent discoveries.

## 8. Historical Conditions May Not Generalize

Prediction-market structure, participants, liquidity, spreads, and exchange behavior may change.

Historical evidence may therefore weaken or disappear in a different market regime.

## 9. Transaction-Cost Assumptions Remained Estimates

Even a conservative cost grid may differ from actual live costs.

Realized cost depends on:

* Market conditions
* Time of entry
* Time of exit
* Available liquidity
* Order size
* Price movement
* Partial fills
* Exchange behavior

## 10. The Project Was Extensively AI-Assisted

AI tools contributed to code drafting, debugging, research design, and documentation.

The project demonstrates substantial system direction, investigation, validation, and technical reasoning.

It should not be represented as equivalent to years of fully independent professional software-engineering experience.

Improving independently demonstrable Python fluency remains an active development objective.

## 11. The Complete Production System Is Not Public

The public repository intentionally excludes:

* Complete production code
* Credentials
* Raw live logs
* Private account records
* Proprietary strategy parameters
* Private infrastructure
* Confidential third-party information

Public reviewers can assess the architecture, research methodology, debugging process, and sanitized examples.

They cannot independently reproduce every private production result from this repository alone.

## Claims the Project Supports

The project supports statements such as:

* A substantial Python-based Kalshi execution and research platform was developed.
* The system integrated REST APIs and WebSockets.
* The platform supported live and simulated execution.
* Complex order and position-state problems were investigated.
* A 33,605-decision research dataset was analyzed.
* A structured predictive-model workflow was built.
* 154 systematic strategy configurations were evaluated.
* Deterministic research and certification workflows were implemented.
* Transaction-cost diagnostics materially changed the strategy conclusions.
* No robust-positive family was certified under the final tested cost framework.
* The project produced meaningful engineering and market-structure knowledge.

## Claims the Project Does Not Support

The project does not support statements such as:

* The platform is a proven profitable trading system.
* Historical results guarantee future returns.
* The model’s ROC-AUC establishes economic profitability.
* All simulated trades could have executed live.
* The shadow portfolio represents deployed capital.
* The 33.6006 attribution figure represents confirmed live profit.
* The live system achieved reliable production-scale execution.
* Every identified discrepancy was a confirmed exchange or software defect.
* The public repository contains the complete system.
* AI assistance played no role in development.

## Current Conclusions

The current evidence supports five broad conclusions.

### 1. The engineering and research platform is substantial

The project moved beyond a basic trading script and developed into a broad execution, data, modeling, replay, diagnostic, and certification environment.

### 2. The strongest value is currently technical and analytical

The platform demonstrates:

* Prediction-market domain experience
* Python and data-analysis work
* API integration
* Execution-system debugging
* Research discipline
* Documentation
* Negative-result preservation
* Reproducibility

### 3. The final tested strategies were not ready for live promotion

The cost-aware side, ticker, horizon, and family diagnostics did not support automatic deployment of a robust-positive strategy group.

### 4. Execution realism remains a central research problem

Low IOC conversion and execution-to-position divergence showed that live implementation quality could dominate theoretical strategy quality.

### 5. Further value may come from collaboration

The platform could become more valuable when combined with:

* Stronger independent quantitative modeling
* Better execution data
* Market-making expertise
* Additional capital-market experience
* More complete liquidity evidence
* Institutional infrastructure
* Broader prediction-market datasets
* Improved manual Python fluency

## Appropriate Next Research Steps

Potential next steps include:

* Resolve exchange execution-to-position hydration
* Improve immediate-fill interpretation
* Reorder candidate-side initialization
* Verify pressure-follow integration
* Reassess routing thresholds
* Build a live-informed IOC fill model
* Expand NO-side evidence
* Improve liquidity-path reconstruction
* Test alternative strategy families
* Reevaluate holding horizons
* Build a clean standalone public notebook
* Add synthetic reproducible examples
* Continue developing independent Python and statistical fluency

## Related Documentation

* [Main Project Overview](../README.md)
* [Institutional Overview](institutional-overview.md)
* [System Architecture](architecture.md)
* [Live Execution Debugging Case Study](execution-debugging-case-study.md)
* [Quantitative Research Methodology](research-methodology.md)
* [Repository Security Policy](../SECURITY.md)

## Contact

**Ryan Eblen**
AI-Assisted Python Developer
Prediction-Market Systems Researcher
Louisville, Kentucky
[ryan.eblen.work@gmail.com](mailto:ryan.eblen.work@gmail.com)
