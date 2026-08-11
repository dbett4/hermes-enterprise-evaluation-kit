# Assurance — Economics & value

**Status:** frozen vendor-neutral kernel

## Risk signals

Unclear baseline, unmeasured labor or review cost, retry/rejection loops, variable usage price, quality-cost tradeoff, value claim based on activity, scaling before accepted outcomes, or no owner-approved stop threshold.

## Control rules

- Predeclare baseline, unit of accepted value, denominator, quality threshold, measurement window, total-cost boundary, and value owner.
- Count implementation, operation, review, exception, retry, rejection, incident, and exit cost—not only model or infrastructure usage.
- Compare costs only across outputs meeting the same acceptance criteria.
- Keep unavailable cost evidence as `not_run` or `unknown`; never invent a zero or estimate it as observed.
- Stop or redesign when the owner-approved quality-adjusted value or cost ceiling is breached.

## Implementation slots

Usage/cost source, labor/operations record, acceptance evidence service, baseline owner process, and periodic value review.

## Required evidence

Baseline; accepted-output denominator; quality and latency results; authorized cost receipts; labor, review, retry, rejection, incident, and support cost; value-owner disposition and sensitivity limits.

## Metrics and triggers

Track total cost per accepted output/effect, acceptance rate, review time, retry/rejection cost, incident cost, cycle-time change, and owner-defined outcome measure. Breaching the cost or value threshold stops expansion and triggers redesign or retirement review.

## Tier application

- L1: baseline, accepted-value unit, major cost categories, owner, and stop threshold.
- L2: observed cost receipts, quality-adjusted comparison, retry/review/exception costs, and sensitivity analysis.
- L3: independently reviewed measurement, allocation/governance rules, scaling scenarios, and formal benefit-realization cadence.

## Exit rule

No cost, return, “best,” or “cheapest” claim advances from inference price, activity, or unaccepted output alone.
