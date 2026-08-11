# Composable packs

**Status:** architecture contract; **nimbus-synthetic org pack landed** (2026-08-07); capability packs still pending

Packs customize the Field Kit without forking its portable control kernel.

| Pack type | Contains | Cannot do |
|---|---|---|
| `organizations/` | Operating envelopes, bundle catalogs, identity bindings, data/provider/authority/budget/retention rules | Grant authority above the policy owner's approved ceiling |
| `capabilities/` | Connectors, verifier patterns, evidence adapters, recovery mechanisms, permissions, failure modes, tests | Redefine lifecycle or authority semantics |
| `workflows/` | Mission language, inputs/outputs, action maps, oracles, exceptions, examples, negative fixtures | Weaken organization policy or conceal runtime choices from receipts |

Every pack is versioned, owned, review-dated, and explicitly compatible with a kernel schema and one or more adapter versions. A resolved Assembly Blueprint records the selected pack versions and canonical manifest hash.

## Blueprint validation invariants

Composition fails closed before execution unless all of these are true:

1. Every pack declares its compatible kernel schema, Hermes adapter versions, dependencies, conflicts, owner, and review/expiry date.
2. Dependencies form an acyclic graph. Organization policy has final precedence; a capability or workflow pack may narrow but never override or widen it. Conflicting declarations are not resolved by load order.
3. Every action-capable pack declares its action classes, authority outcomes, enforcement points, known bypasses, stop behavior, and target readback.
4. Every acceptance-critical output or effect has a compatible oracle, verifier requirement, evidence contract, and terminal disposition. A missing or incompatible declaration produces `needs_policy_decision`, never a permissive default.
5. Referenced artifacts and versions exist and match the resolved manifest before Hermes starts.

Compatibility metadata and hashes provide provenance only. They do not prove signing, enforcement, custody, or trust.

Public-sector finance, if pursued later, belongs under `workflows/public-finance/`. It is not part of the generalized preview critical path.

No capability pack ships in this preview; the table row documents the pack type for completeness.
