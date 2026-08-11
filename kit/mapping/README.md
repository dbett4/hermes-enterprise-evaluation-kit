# Hermes release map

This directory ties each requirement in the Field Kit to the exact Hermes release I
tested. A row says whether the behavior comes from Hermes itself, configuration, this
kit, surrounding infrastructure, or an unresolved gap.

`scripts/generate_b05_mapping.py` builds the map. The lock file records input digests so
changes to the generated output are visible. A few build inputs are private, which means
the public repository can validate the shipped map and its shape but cannot reproduce
every source input byte for byte.

The generator was built in three parts:

| Part | Responsibility | Status |
|---|---|---|
| B1 | Row decisions, overrides, and source tracking | Merged; later rendering work belongs to B3 |
| B2 | Map, seven-item gap list, and lock materialization | Merged at `e881571` |
| B3 | Link index, summaries, and output hash chain | In progress in memory; no schema or materialized-output change yet |

Useful commands:

```bash
# Validate the pending 318-row manifest
python3 scripts/generate_b05_mapping.py --foundation-check

# Compile B1 through B3 and print the row, gap, link, and hash summary
python3 scripts/generate_b05_mapping.py --check

# Write the map, gap list, and lock only when their hashes match the expected result
python3 scripts/generate_b05_mapping.py --materialize
```

The manifest, overrides, schemas, and lock determine the generated result. Do not infer
runtime behavior beyond what a row and its test source actually show.
