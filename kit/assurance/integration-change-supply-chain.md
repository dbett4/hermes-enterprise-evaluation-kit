# Integration, change, and supply chain

**Status:** frozen vendor-neutral kernel

## Risk signals — pay extra attention when

Any change to model, provider, prompt, skill, tool, policy, runtime, plugin, dependency, connector, verifier, environment, supplier, or configuration; unsigned/unpinned artifacts; implicit load-order precedence; or external API/schema drift.

## Control rules

- Identify and retain every acceptance-critical component and canonical configuration input.
- Resolve dependencies, precedence, conflicts, compatibility, and gaps explicitly; load order never decides policy conflict.
- Classify each requirement using the version-pinned implementation-mapping contract.
- Treat a material change as a new risk identity with explicit `none`, `haircut`, `probation`, or approved-carryover novation.
- Test integration failure, schema drift, rollback, supersession, and supplier exit.

## Implementation slots — where controls can live

Configuration registry, artifact/dependency process, connector, release/change process, policy service, and supplier-governance process.

## Required evidence — what to keep

Canonical manifest; retained referenced artifacts and source/version identities; capability-location map; change and novation decision; compatibility, conflict, integration, schema, rollback, and reconstruction results; gap and supplier-exception register.

## Metrics and triggers — what to watch

Unknown acceptance-critical components = 0; silent material drift = 0; unreconstructable releases = 0. Track dependency age, failed updates, rollback success, schema incidents, and gap age. Material drift invalidates the configuration identity and returns to Stage 3.

## Tier application — depth by risk

- L1: explicit component inventory, owner, update rule, and rollback path.
- L2: pinned/identified critical inputs, canonical manifest, negative integration tests, reconstruction, and explicit novation.
- L3: stronger provenance/signing where required, independent change approval, supplier concentration/exit testing, and formal policy-distribution controls.

## Exit rule — done when

No candidate advances when an acceptance-critical dependency, conflict, capability location, referenced artifact, change authority, or rollback path is unknown.
