# Assurance — Reliability & continuity

**Status:** frozen vendor-neutral kernel

## Risk signals

Long-running or scheduled work, multiple dependencies, partial failure, retryable tools, duplicate-sensitive effects, latency or freshness commitments, fallback paths, outage exposure, weak stop state, or manual-continuity dependence.

## Control rules

- Define timeout, bounded retry, backoff, idempotency, duplicate prevention, circuit breaking, stop, safe state, and recovery behavior.
- Read target state before and after every material effect; never infer success from tool return alone.
- Treat fallback as a material change when it alters provider, model, data route, tool, or verification assumptions.
- Test interruption, partial effect, stale input, dependency outage, recovery objective, rollback, and manual continuity.
- Contain and contract before recovery when the resulting state is unknown.

## Implementation slots

Execution boundary, scheduler/queue, connector, target system, health/readback service, recovery tooling, and operations/incident process.

## Required evidence

Prestate/poststate; health and liveness readback; failure-injection results; retry/fallback event; duplicate-effect test; stop, rollback, recovery and manual-path results; unresolved dependency and incident records.

## Metrics and triggers

Duplicate material effects = 0; unowned partial effects = 0. Track availability, task age, recovery time, retry/fallback rate, stale-input rate, rollback success, and missed/late effects. Recovery-objective or liveness breach contracts or suspends the affected scope.

## Tier application

- L1: explicit timeout, stop owner, retry limit, health check, and manual recovery route.
- L2: idempotency, failure injection, target readback, tested rollback/recovery, and operating thresholds.
- L3: independent liveness, stronger isolation, disaster/manual continuity rehearsal, dependency-exit paths, and formal recovery evidence.

## Exit rule

The deployment must stop or recover within its declared boundary without duplicate, unobserved, or unowned material effects.
