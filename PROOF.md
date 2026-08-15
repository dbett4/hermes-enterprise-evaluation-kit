# What you can verify

This page is the **command-level claim table**. For the human story — problem,
flow, and what the kit is for — start with [README.md](README.md).

## Offline path (default)

```bash
./scripts/proof.sh
```

No Hermes call. No API keys. No network. The script prints
`FIELD_KIT_PROOF_OFFLINE` up front and `FIELD_KIT_PROOF_PASS` only after every
offline check succeeds.

In plain English, a pass means: the capability map is intact, known-bad paths
still fail closed, the shared core stayed vendor-neutral, receipt guards still
work, weak older evidence is still labeled weak, the committed live receipt still
hashes, and the local demo still ends in human review.

Map snapshot alone:

```bash
python3 scripts/verify_public_mapping.py
```

| Plain-language check | Command | Passing result | What it does not prove |
|---|---|---|---|
| Capability map for the pinned Hermes release is intact | `python3 scripts/verify_public_mapping.py` | Schemas pass; map, seven-item gap list, hashes, counts, release ID, and shipped public inputs agree | Private build inputs are digest-only; this checks the published snapshot rather than rebuilding every private input |
| Scoring / evaluator contracts stay deterministic | `pytest -q tests/test_evaluator.py` | Fingerprints stable; fixtures and completed example evaluate deterministically | Does not replace the full B03 artifact generator |
| Profile config still exposes provider readback correctly | `pytest -q tests/test_hermes_runtime.py` | `model.provider` with `provider.default` fallback matches the shipped profile config | Optional `HERMES_BIN` integration test is skipped unless supplied |
| Shared operating rules are not hard-wired to Hermes | `python3 scripts/check_neutral_core.py` | 22 files, six lifecycle stages, and eight review areas contain no vendor-specific terms | Hermes-specific code and mapping deliberately live elsewhere |
| Eight known failure modes stop safely | `python3 scripts/run_negative_tests.py` | All 8 fixtures reach the expected final state and produce the required run facts | The cases are synthetic; they do not use customer data or production systems |
| Live runner must identify the CLI and reject the wrong release | `python3 scripts/verify_runtime_attestation_guard.py` | A matching native version and executable SHA-256 are required; a mismatch stops the run | A version result does not tie the executable bytes to a particular source commit |
| Older weak S1 record is consistent and clearly unattested | `python3 scripts/verify_committed_recorded_receipt.py` | The record validates; its copies of stdout and output agree; the checker recomputes; missing runtime identity is recorded as an exception | It does not show that the declared Hermes release, daemon, provider, or model produced the output |
| Committed live one-shot still binds output to native Hermes evidence | `python3 scripts/verify_committed_attested_receipt.py` | Schema, executable/output hashes, native session ID, frozen output, runtime provider/model readback, usage estimate, and deterministic oracle agree | Human disposition is pending; $0.406986 is an estimate, not an actual-charge claim; the wrapper-bypass and provider-policy exceptions remain visible |
| A passing checker does not stand in for a person | Same command | Human review is `pending`, no review record exists, and the final state is `needs_review` | No authorized reviewer has decided the synthetic case |
| Mission story works without credentials | `bash scripts/demo_mission_s1.sh` | Policy selection, local producer, deterministic checker, run record, and pending decision all complete | The producer is deterministic local code, not a live model run |

## Live proof (guarded, spends money)

```bash
LIVE_PROOF_AUTHORIZED=yes \
  SPEND_AUTHORIZATION_FILE=spend-authorization/<file> \
  SPEND_CAP_USD=1.00 \
  HERMES_BIN=/path/to/hermes \
  ./scripts/live_proof.sh
```

This path is intentionally excluded from `./scripts/proof.sh`.

## Limits that apply to every result

- Live inference occurred once. Hermes recorded a $0.406986 estimate; no
  provider-reported actual billed USD was captured. This repository makes no
  exact-charge or ROI claim.
- Provider and model names in the older record are operator-entered metadata.
- The organization and policy documents are fictional.
- This project is not an official Nous product, partnership, endorsement, or customer
  deployment.
- The committed live one-shot ties output to the pinned Hermes executable bytes and a
  native CLI session, but remains `needs_review` with two recorded exceptions. The
  older S1 record remains `operator-recorded-unattested`.
