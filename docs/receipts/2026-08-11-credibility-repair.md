# Credibility repair receipt — 2026-08-11

## Scope

Repository: `hermes-enterprise-field-kit`
Date: 2026-08-11 (UTC)
Operator: Cursor agent (implementation) and Hermes (independent execution)
Commit: included in the verified publication packet

## Reproduced failures (pre-repair)

| Check | Expected failure | Root cause |
|---|---|---|
| `python3 scripts/generate_b05_mapping.py --check` | `B1_PROVENANCE` / missing frozen input | Lock required private `build-tickets/` and `research/` paths absent from public tree; stale `implementation-mapping-contract.md` digest in lock |
| `./scripts/proof.sh` | Same mapping path or downstream | Public integrity story depended on private regeneration semantics |
| `runtime_reported_from_config` | Wrong provider on v0.20 profiles | Read only `provider.default`, not `model.provider` from nested `config.yaml` |
| Profile distribution | Misleading `OPENROUTER_API_KEY` requirement | Shipped profile uses `model.provider: nous` |

## Changes made

### 1. B03 evaluator (`kit/instrument/evaluator.py`)

- Removed unreachable `raise ValueError("unknown risk operator")` after `return` in `_risk_detail.hit`.
- Removed duplicate `reasons = [...]` assignment before the non-empty fired return.
- Reformatted module header, `_risk_detail`, `evaluate`, `_validate_result`, and `__main__` to four-space PEP 8.
- Preserved `DECISION_FINGERPRINT`, `RISK_FINGERPRINT`, and evaluation semantics.

### 2. Lint / test gate

- Added `pyproject.toml` with Ruff configuration.
- Added `tests/test_evaluator.py` (fingerprints, fixture, determinism, invalid intake).
- Added `tests/test_hermes_runtime.py` (provider resolution + optional `HERMES_BIN` integration).
- Extended `requirements.txt` with `ruff` and `pytest`.
- `./scripts/proof.sh` now runs Ruff and pytest before repository guards.

### 3. Public mapping integrity

- Added `kit/mapping/public-integrity.manifest.json` documenting public inputs, private digest-only provenance, and verification scope.
- Expanded `scripts/verify_public_mapping.py` to validate manifest, shipped public inputs, private digest record, schemas, 318 rows, seven gaps, and locked output hashes.
- Updated `scripts/generate_b05_mapping.py` to separate `PUBLIC_INPUT_PATHS` from `PRIVATE_PROVENANCE_DIGESTS`; public inputs are read from disk, private inputs are digest-only and must not exist in the public tree.
- Rewrote `kit/mapping/README.md` so the public command is `verify_public_mapping.py`; maintainer `--check` is labeled explicitly.

### 4. Hermes runtime provider resolution

- `scripts/hermes_runtime.py` now reads `model.provider` first, then falls back to `provider.default`.

### 5. Profile distribution alignment

- `packs/profiles/profile-decide-vendor-policy/distribution.yaml` documents Nous OAuth (`hermes auth add nous --type oauth`) instead of `OPENROUTER_API_KEY`.
- Profile README updated accordingly.

### 6. Proof scripts

- `scripts/proof.sh` banners state credential-free / offline scope; runs lint and unit tests.
- Added guarded `scripts/live_proof.sh` requiring `LIVE_PROOF_AUTHORIZED=yes`, spend authorization, cap, and `HERMES_BIN` (does not run during this repair).

### 7. README / PROOF

- Top-third provenance note (sanitized public extract, August 2026).
- “Verify in 5 minutes” path via `./scripts/proof.sh`.
- 214-test preflight pinned to peeled commit `3c27eb6` / tag `v2026.8.3`.
- Live attestation limitation remains visible.

## Verification commands (run locally)

```bash
cd /srv/hermes/work/dbett4-portfolio/hermes-enterprise-field-kit
pip install -r requirements.txt
./scripts/proof.sh
python3 scripts/verify_public_mapping.py
python3 scripts/generate_b05_mapping.py --check
python3 -m pytest -q tests/
python3 -m ruff format --check scripts/hermes_runtime.py scripts/verify_public_mapping.py tests/
python3 -m ruff check kit/instrument/evaluator.py scripts/hermes_runtime.py scripts/verify_public_mapping.py tests/
```

Optional live path (spends money; not run for this receipt):

```bash
chmod +x scripts/live_proof.sh
LIVE_PROOF_AUTHORIZED=yes \
  SPEND_AUTHORIZATION_FILE=spend-authorization/<file> \
  SPEND_CAP_USD=1.00 \
  HERMES_BIN=/path/to/hermes \
  ./scripts/live_proof.sh
```

## Verification results (independent local execution)

The initial worker did not execute the gates. Hermes independently installed the public
requirements into an ignored `.venv`, fixed the resulting scoped lint defects, and ran
the actual commands on 2026-08-11:

```text
./scripts/proof.sh
7 passed, 1 skipped
PUBLIC_MAPPING_PASS rows=318 gaps=7 release=v2026.8.3 public_inputs=7 private_provenance=3 locked_outputs=2
RUNTIME_ATTESTATION_GUARD_PASS captured_sha256=1 release_mismatch=blocked
NEUTRAL_CORE_PASS
B08 negative tests: 8/8 passed
RECORDED_RECEIPT_PASS ... runtime_attestation=missing ... cost=NOT_RUN
MISSION_DEMO_PASS ... terminal=needs_review ... oracle_passed=True
FIELD_KIT_PROOF_PASS mapping_rows=318 negative_tests=8 recorded_receipt=pass runtime_attestation=missing demo=pass lint=pass unit_tests=pass

python3 scripts/generate_b05_mapping.py --check
B05_CHECK_PASS rows=318 gaps=7 links=326 chain=3e99a18c09f55a76

HERMES_BIN=/srv/hermes/.local/bin/hermes HERMES_PROFILE=default pytest -q tests/test_hermes_runtime.py
4 passed
```

The generator source hash in `b05-generation.lock.json` was updated to the exact repaired
generator bytes after the first real `--check` correctly rejected the stale hash.

The proof script performs no install or network operation; dependency installation is a
separate prerequisite. The lint gate is intentionally scoped to the evaluator,
runtime/mapping verifier, and new tests hardened by this repair rather than pretending
the repository's legacy generators are globally Ruff-clean.

No live model call was made. Hermes Agent v0.20.0 / 2026.8.3 and Nous OAuth are available,
but no owner-created `spend-authorization/*.authorization` file exists. The repository's
separation control expressly forbids an agent from creating or transcribing that file,
so the live-attestation gap remains truthful.

## Intentional non-changes

- No git commit or push.
- No private `build-tickets/` or `research/` files fabricated.
- No live Hermes invocation or provider spend during repair.
- `b05-generation.lock.json` output hashes and adjudicated artifacts unchanged.

## Achieved post-repair outcomes

- `./scripts/proof.sh` → `FIELD_KIT_PROOF_PASS`
- `python3 scripts/verify_public_mapping.py` → `PUBLIC_MAPPING_PASS rows=318 gaps=7 ...`
- `python3 scripts/generate_b05_mapping.py --check` → `B05_CHECK_PASS rows=318 ...` without private input files on disk
