# What you can verify

Run all credential-free checks with:

```bash
./scripts/proof.sh
```

The script prints `FIELD_KIT_PROOF_OFFLINE` before running and `FIELD_KIT_PROOF_PASS` only after
every offline check succeeds. It does not call Hermes, use API keys, or need network access.

For the published map snapshot alone:

```bash
python3 scripts/verify_public_mapping.py
```

| What I am checking | Command | Passing result | What it does not prove |
|---|---|---|---|
| The public map has 318 valid rows for the pinned Hermes release | `python3 scripts/verify_public_mapping.py` | Schemas pass; map, seven-item gap list, hashes, counts, release ID, and shipped public inputs agree | Private build inputs are digest-only; this checks the published snapshot rather than rebuilding every private input |
| Instrument evaluator contracts and determinism | `pytest -q tests/test_evaluator.py` | Fingerprints stable; fixtures and completed example evaluate deterministically | Does not replace the full B03 artifact generator |
| Hermes runtime provider readback | `pytest -q tests/test_hermes_runtime.py` | `model.provider` with `provider.default` fallback matches the shipped profile config | Optional `HERMES_BIN` integration test is skipped unless supplied |
| The reusable core is not coupled to Hermes | `python3 scripts/check_neutral_core.py` | 22 files, six lifecycle stages, and eight review areas contain no vendor-specific terms | Hermes-specific code and mapping deliberately live elsewhere |
| Eight known failure modes stop safely | `python3 scripts/run_negative_tests.py` | All 8 fixtures reach the expected final state and produce the required run facts | The cases are synthetic; they do not use customer data or production systems |
| A future live runner must identify the CLI and reject the wrong release | `python3 scripts/verify_runtime_attestation_guard.py` | A matching native version and executable SHA-256 are required; a mismatch stops the run | A version result does not tie the executable bytes to a particular source commit |
| The older operator-recorded run is internally consistent and clearly marked unattested | `python3 scripts/verify_committed_recorded_receipt.py` | The record validates; its copies of stdout and output agree; the checker recomputes; missing runtime identity is recorded as an exception | It does not show that the declared Hermes release, daemon, provider, or model produced the output |
| A passing checker does not stand in for a person | Same command | Human review is `pending`, no review record exists, and the final state is `needs_review` | No authorized reviewer has decided the synthetic case |
| The mission flow works without credentials | `bash scripts/demo_mission_s1.sh` | Policy selection, local producer, deterministic checker, run record, and pending decision all complete | The producer is deterministic local code, not a live model run |

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

- Provider cost is `NOT_RUN`; this repository makes no cost or ROI claim.
- Provider and model names in the older record are operator-entered metadata.
- The organization and policy documents are fictional.
- This project is not an official Nous product, partnership, endorsement, or customer
  deployment.
- There is still no committed live receipt tying model output to the pinned Hermes
  executable; the older S1 record remains `operator-recorded-unattested`.
