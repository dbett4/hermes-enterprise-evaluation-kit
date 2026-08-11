# Examples and counterexamples

**Status:** frozen vendor-neutral kernel

These examples show why stopping, using ordinary automation, or retaining human release
can be the right engineering result.

## Example 1 — qualify a read-only policy recommendation

**Candidate:** compare a synthetic supplier exception against an approved policy and draft a recommendation for a named owner.

- The output is draft-only; no external send, target mutation, sensitive data, payment, privilege, or production effect is permitted.
- Policy sources, baseline review time, owner, acceptance criteria, and deterministic policy checks are known.
- Classification: T1 advisory, with all modules at L1 except quality raised to L2 because model judgment is acceptance-critical.
- Authority: reads and draft creation are bounded; a human owns the business disposition.
- Trace: ambiguous-policy risk → fixed criteria and deterministic rule checks → verification service → criteria result → zero unexplained rule failures.
- Stage 1 disposition: `qualify`.

Why this is not automatic authority: a correct recommendation does not authorize the underlying supplier exception or external communication.

## Example 2 — earn bounded pre-authorization for a reversible staging change

**Candidate:** change one named non-production service setting within an approved range, check health, and reverse the exact change on failure.

- The target, key, range, credential, stop path, prestate, poststate, oracle, and rollback are explicit.
- Classification: T2 bounded operational; authority, quality, evidence, identity, integration, and reliability operate at L2.
- First occurrence: `H`; the human sees the exact target/diff and releases the effect.
- After an accepted observed effect and rollback test, the policy owner may ratify `A` for that exact action-class/resource/environment/configuration family.
- Any target drift, missing readback, out-of-range value, or configuration change returns to `D` or `H`.

Why this can become pre-authorized: the bounded effect is reversible, independently observable, and policy-ratified from an accepted first occurrence. Similar-looking production changes do not inherit the grant.

## Counterexample 1 — do not agentize an unobservable destructive effect

**Candidate:** let an agent remove user access across several external systems, including one with no reliable final-state query or tested recovery.

- The effect is destructive and can strand an account.
- One target cannot provide authoritative readback or safe recovery.
- The proposed credential reaches resources beyond the named population.
- Stage 1 disposition: `do_not_agentize` for the execution path. A draft-only coordination aid may be qualified as a separate scope.

Why approval is insufficient: a human click does not make an unbounded or unobservable effect controlled.

## Counterexample 2 — not ready to authorize a plausible candidate

**Candidate:** a T2 internal workflow passes happy-path output checks but its critical dependency cannot be reconstructed, rollback was not exercised, and the checker saw mutable producer output.

- Stage 3 should not have emitted `candidate_ready`; if discovered in Stage 4, the result is `not_ready_to_authorize`.
- A waiver cannot convert the missing reconstruction, rollback, or producer-fixity evidence into a pass.
- Required return: repair the retained artifact set and rollback path in Stage 3, refix producer output, and rerun the preregistered tests.

Why apparent success does not count: the approval applies to the fixed configuration and
its test results, not to one plausible-looking output.

## Counterexample 3 — choose conventional automation

**Candidate:** copy a validated structured field from one system to another using a fixed schema, exact transformation, transactional write, and deterministic error handling.

- No judgment or adaptive tool selection is required.
- Conventional automation is simpler to test, cheaper to operate, and easier to recover.
- Stage 1 disposition: `do_not_agentize`, with a recommendation for deterministic integration.

Rejecting the agent approach here means qualification worked.
