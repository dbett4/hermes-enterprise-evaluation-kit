# Requirement-to-runtime mapping

Maps each enterprise requirement in the kit to what the pinned Hermes release actually provides — native support, kit-supplied control, or an honest gap. Generated deterministically by `scripts/generate_b05_mapping.py`; the lock file pins input digests so a regenerated map can be diffed against the shipped one. Some pinned generator inputs remain private (see the root README's transparency note), so public regeneration is a verification of shape, not a byte-for-byte rebuild.

`scripts/generate_b05_mapping.py` is the frozen compiler:

| Phase | Responsibility | State |
|-------|----------------|-------|
| **B1** | Row decisions + override merge + provenance | **merged** — defers `render-links`, `summaries`, `output-hashes` to B3 |
| **B2** | Map + capability-gap ledger + post-lock materialization | **merged** @ `e881571` |
| **B3** | Render-link index, module summaries, output-hash chain | **in progress** — in-memory only; no schema/materialize change yet |

`--foundation-check` verifies pending production manifest (318 rows, adjudication pending fields).
`--check` runs B1→B2→B3 compile against adjudicated overrides and prints row/gap/link/chain summary.
`--materialize` writes map, ledger, and lock only when compiled hashes match the production oracle (no-op if already ahead).

The manifest, overrides, generation lock, map schema, and gap-ledger schema are governing contracts. B03 integration remains `absent` in the map until instrument v3 wiring lands. No operational claim may be inferred beyond what the lock outputs record.
