# Hermes release map

This directory ties each requirement in the Evaluation Kit to the exact Hermes release I
tested. A row says whether the behavior comes from Hermes itself, configuration, this
kit, surrounding infrastructure, or an unresolved gap.

The shipped **318-row map** and **seven-item gap list** are public artifacts. A few
private build inputs exist only as digests in `b05-generation.lock.json`; this public
tree does not include those files and does not claim full private regeneration.

## Public integrity check (use this in a public clone)

```bash
python3 scripts/verify_public_mapping.py
```

That command validates schemas, the 318 adjudicated rows, seven gaps, locked output
hashes, all shipped public inputs, and the private-extraction digest record. It is the
single command that proves the current public snapshot.

See `public-integrity.manifest.json` for the public input list and private provenance
boundary.

## Private generator (maintainer only)

`scripts/generate_b05_mapping.py` compiles the map when private extraction inputs are
present on disk. In this public repository it still validates adjudication and can run
`--check` against the shipped snapshot, but it cannot recreate private build-ticket or
research inputs that are absent here.

```bash
# Maintainer compile check against the shipped snapshot
python3 scripts/generate_b05_mapping.py --check
```

Do **not** treat `--materialize` as a public reproducibility command. It is for
maintainers when private inputs and expected output hashes are available.

The manifest, overrides, schemas, and lock determine the generated result. Do not infer
runtime behavior beyond what a row and its test source actually show.
