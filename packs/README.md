# Packs

Packs customize a deployment without copying and editing the reusable core. The
fictional Nimbus organization pack is implemented; capability packs remain future work.

| Directory | What belongs there | Hard limit |
|---|---|---|
| `organizations/` | Provider, data, permission, budget, identity, retention, and approved-configuration rules | Cannot grant more permission than the policy owner approved |
| `capabilities/` | Connectors, checkers, storage adapters, recovery behavior, permissions, failure modes, and tests | Cannot redefine lifecycle or authority rules |
| `workflows/` | Job language, inputs, outputs, actions, programmed checks, exceptions, examples, and failure fixtures | Cannot weaken organization policy or hide runtime choices |

Each pack names its version, owner, review date, compatible core schema, and compatible
Hermes adapter. A resolved blueprint stores the selected versions and a stable manifest
hash.

Before Hermes starts, validation rejects a blueprint unless:

1. Every dependency and conflict is declared, the graph has no cycles, and organization
   policy wins conflicts explicitly rather than through load order.
2. Every action declares the permission used, where it is enforced, known bypasses,
   how it stops, and how the target state is read back.
3. Every important output has a compatible checker, review requirement, and final state.
4. Every referenced file and version exists and matches the resolved manifest.

The versions and hash identify what was selected. They do not prove signing, custody,
enforcement, or trust.

Public-sector finance may become a workflow pack later. It is not part of the preview's
main path. No capability pack ships yet; the directory is documented to show the
intended extension point.
