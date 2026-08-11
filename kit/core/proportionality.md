# Risk tiers

**Status:** frozen vendor-neutral kernel

The tier changes how much control and review a job needs; it does not let a team ignore a
whole review area. Every qualified deployment considers all eight areas. The highest
applicable trigger sets the base tier, and a specific concern can increase its own depth.

## 1. Record the facts

Record these dimensions before assigning a tier:

1. data sensitivity, source authority, purpose, residency, and retention;
2. action class, target, environment, external effect, and privilege;
3. consequence magnitude, affected population, and ability to recall the effect;
4. reversibility, tested rollback, safe state, idempotency, and recovery time;
5. novelty, ambiguity, model judgment, and exception frequency;
6. identity, delegation, credential reach, and segregation-of-duties needs;
7. verifier strength, target readback, custody, and evidence completeness;
8. duration, dependency count, supplier change, adoption burden, and operating cost.

Missing facts are marked `unknown`. An acceptance-critical `unknown` produces `defer` or a higher control floor; it never earns a lower tier.

## 2. Use the highest applicable tier

| Tier | Deterministic trigger | Default authority posture |
|---|---|---|
| **T0 — not qualified** | Prohibited purpose; no accountable owner; impermissible source/data use; unbounded material effect; no viable target readback or safe state; or control cost defeats plausible value | `D`, `do_not_agentize`, or `defer` |
| **T1 — advisory** | Every material output is read-only or draft-only; no external effect, sensitive data, privilege, production change, or irreversible consequence; authoritative sources and owner are known | `D` outside the read/draft scope; human disposition for material use |
| **T2 — bounded operational** | Internal coordination or a narrow reversible noncritical effect; explicit target and range; tested readback and recovery; limited credential and data scope | First occurrence `H`; bounded `A` only after accepted evidence and policy-owner ratification |
| **T3 — material** | External communication or publication; production or customer-facing effect; confidential or regulated data; money; meaningful privilege; broad population; difficult recovery; or material business/legal consequence | `H` by default, with stronger separation and independently controlled release/evidence as required |
| **T4 — critical** | Irreversible or destructive critical effect; critical privilege or authority-system change; high-value payment; legal-hold, employment, safety, or similarly severe consequence; or required dual control | `H2` where implementable; otherwise `D` or `do_not_agentize`; never `A` |

An action may be valuable and still be T0 because its controls are unavailable. A tier does not grant authority; it sets the minimum evidence and control posture for a later authority decision.

## 3. Set the depth for each review area

| Depth | Minimum treatment |
|---|---|
| **L0 — disposition only** | Record why the workflow was rejected or deferred, its owner, evidence, and resume condition |
| **L1 — baseline** | Named owner, explicit rule, bounded implementation slot, retained evidence, one measurable threshold, and exception path |
| **L2 — standard** | L1 plus independent or deterministic checks, negative cases, change/rollback tests, periodic review, and operating metrics |
| **L3 — enhanced** | L2 plus stronger identity/release separation, independently controlled evidence where claimed, adversarial/bypass tests, tested suspension/revocation, and formal recertification |

Base profile:

| Tier | Authority | Quality | Evidence | Identity/security/data/legal | Integration/change | Reliability | Economics | Adoption |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| T0 | L0 | L0 | L1 | L1 | L0 | L0 | L1 | L1 |
| T1 | L1 | L1 | L1 | L1 | L1 | L1 | L1 | L1 |
| T2 | L2 | L2 | L2 | L2 | L2 | L2 | L1 | L1 |
| T3 | L3 | L3 | L3 | L3 | L3 | L2 | L2 | L2 |
| T4 | L3 | L3 | L3 | L3 | L3 | L3 | L3 | L3 |

The base profile is a floor. Apply these mandatory uplifts:

- regulated, privileged, or restricted data → identity/security/data/legal and evidence at L3;
- any external effect → authority and evidence at least L2;
- production effect, payment, publication, destructive action, or privilege change → authority at L3;
- no immediate safe rollback or long recovery objective → reliability at L3;
- model, provider, tool, integration, policy, or supplier change that can alter outcomes → integration/change at least L2;
- acceptance dependent on model judgment → quality at least L2;
- multi-owner handoff, long-lived operation, or staff displacement → adoption at least L2;
- a public cost, value, or return claim → economics at least L2 with authorized observed cost evidence.

## 4. Save the decision

The record contains:

- classification facts and evidence basis;
- highest trigger and assigned tier;
- all eight module depths and each uplift reason;
- authority posture and hard ceilings;
- unresolved facts and owners;
- reassessment triggers; and
- policy-owner disposition.

Recalculate after any material configuration, action, data, provider, integration, environment, owner, verifier, incident, or legal-policy change.

## Selection checks

- Two evaluators given the same facts must select the same tier and base profile.
- A higher trigger cannot be averaged down by several lower-risk facts.
- Compensating controls may reduce residual risk but do not rewrite the underlying trigger.
- If a required L2 or L3 capability is unavailable, narrow the scope, retain human control, defer, or do not agentize.
