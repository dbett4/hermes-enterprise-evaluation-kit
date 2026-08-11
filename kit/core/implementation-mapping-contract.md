# Implementation-mapping contract

**Status:** frozen vendor-neutral kernel

This contract keeps portable requirements separate from any one product while forcing every actual deployment to identify where each control lives. The mapping is version-specific and evidence-backed; feature names, release notes, or architectural resemblance are discovery inputs, not proof.

## Required classifications

Map every neutral requirement to exactly one primary status:

| Status | Meaning |
|---|---|
| `native` | The pinned product supplies the requirement directly in the tested reference path |
| `configuration` | The product supplies the mechanism only when an explicit, retained setting or policy enables it |
| `extension` | A supported plugin, hook, adapter, or added component implements the requirement inside the product boundary |
| `surrounding-platform` | A separate identity, policy, isolation, evidence, target, or operations system supplies the requirement |
| `unsupported-gap` | No sufficient implementation has been identified for the scoped requirement |

Classification describes control location, not quality. A configured or native mechanism may still be insufficient for the required tier.

## Required row fields

Each mapping row records:

- neutral requirement and linked control trace;
- exact product/runtime version, source identity, package identity, and tested topology;
- one primary status and any necessary supporting statuses;
- implementation component, configuration identity, owner, and conditions;
- official source or observed-test evidence, with date and evidence basis;
- known limit, bypass, and security boundary;
- reference-case use and acceptance test;
- surrounding or manual treatment when incomplete;
- gap owner, consequence, and decision; and
- staleness trigger and next review.

## Decision rules

1. Use the strongest sufficiently evidenced built-in mechanism before adding an extension or surrounding substitute.
2. Conditional capability is `configuration`, not unqualified `native`.
3. An observed installed topology does not prove exact-release conformance; exact-release source tests do not prove a deployed topology.
4. Untested surfaces remain `not_run` evidence status even if a release announces them.
5. No row may hide a load-bearing surrounding dependency behind a product feature name.
6. `unsupported-gap` causes scope reduction, human control, deferral, or rejection when the requirement is acceptance-critical.
7. A new product version, topology, configuration, or requirement invalidates affected rows until reviewed.

## Mapping acceptance

The map passes only when every neutral requirement has one primary classification, all native/configuration/extension claims carry version-specific evidence, every condition and gap is explicit, and a non-builder can reproduce the reference-path conclusion.
