# How runtime support is classified

**Status:** frozen vendor-neutral kernel

The release map keeps the reusable requirements separate from any one product and says
where each one is actually implemented. It is tied to a version and a specific test or
official source. A feature name, release note, or similar-looking architecture is a lead
to investigate, not a passing result.

## Status values

Map every neutral requirement to exactly one primary status:

| Status | Meaning |
|---|---|
| `native` | The pinned product supplies the requirement directly in the tested reference path |
| `configuration` | The product supplies the mechanism only when an explicit, retained setting or policy enables it |
| `extension` | A supported plugin, hook, adapter, or added component implements the requirement inside the product boundary |
| `surrounding-platform` | A separate identity, policy, isolation, evidence, target, or operations system supplies the requirement |
| `unsupported-gap` | No sufficient implementation has been identified for the scoped requirement |

Classification describes control location, not quality. A configured or native mechanism may still be insufficient for the required tier.

## What each row records

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

## Rules

1. Use the strongest sufficiently evidenced built-in mechanism before adding an extension or surrounding substitute.
2. Conditional capability is `configuration`, not unqualified `native`.
3. An observed installed topology does not prove exact-release conformance; exact-release source tests do not prove a deployed topology.
4. Untested surfaces remain `not_run` evidence status even if a release announces them.
5. No row may hide a load-bearing surrounding dependency behind a product feature name.
6. `unsupported-gap` causes scope reduction, human control, deferral, or rejection when the requirement is acceptance-critical.
7. A new product version, topology, configuration, or requirement invalidates affected rows until reviewed.

## A complete map

The map is complete only when every requirement has one primary status, each
`native`/`configuration`/`extension` row points to version-specific support, all limits
and gaps are visible, and someone other than the builder can reproduce the conclusion.
