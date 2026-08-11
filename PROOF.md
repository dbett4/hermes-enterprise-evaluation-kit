# Claim-to-command proof map

Run the credential-free proof packet with:

```bash
./scripts/proof.sh
```

The script exits nonzero on the first failed oracle and prints `FIELD_KIT_PROOF_PASS` only after every row below passes.

| Claim | Native proof | Oracle | Boundary |
|---|---|---|---|
| The shipped generalized map contains 318 schema-valid rows against the pinned Hermes release | `python3 scripts/verify_public_mapping.py` | Public schemas validate; map and seven-entry gap ledger match their locked output hashes; counts and release identity reconcile | A few generator inputs remain private, so the public tree verifies the materialized artifacts but cannot regenerate them |
| The control kernel is vendor-neutral | `python3 scripts/check_neutral_core.py` | 22 files, six lifecycle stages, and eight assurance modules contain no vendor-specific terms | Hermes-specific adapters and mappings intentionally live outside the core |
| Eight named fault classes fail closed through the evaluator or real reference pipeline | `python3 scripts/run_negative_tests.py` | 8/8 fixtures reach their exact terminal state with required receipt/oracle facts | Synthetic scenarios; no customer data or production system |
| A future non-demo run must capture native CLI identity and fail on a release mismatch | `python3 scripts/verify_runtime_attestation_guard.py` | Executable SHA-256 and matching native version output are required; a mismatched version fails closed | A CLI version probe does not bind executable bytes to the pinned source commit |
| The committed older operator-recorded artifact is internally consistent and explicitly unattested | `python3 scripts/verify_committed_recorded_receipt.py` | Schema-valid record; stdout, producer artifact, and embedded output are equal; deterministic oracle recomputes; the missing runtime attestation is a named exception | It is not proof that the declared Hermes release, daemon, provider, or model produced the output |
| Passing the deterministic oracle does not impersonate human approval | Same command | Human status is `pending`; review evidence is empty; terminal state is `needs_review` | A real authorized reviewer has not dispositioned the synthetic case |
| The policy-resolved mission shape reproduces without credentials | `bash scripts/demo_mission_s1.sh` | Resolver, producer, deterministic oracle, receipt, and pending disposition complete | Demo producer is local and deterministic; it is not a second live provider run |

## Live artifact limits

- Provider cost remains `NOT_RUN`; the repository makes no cost or ROI claim.
- The older record's model/provider fields are operator-recorded metadata, not native or independent attestation.
- The policy corpus and organization are synthetic.
- No official Nous product, partnership, endorsement, or customer deployment is claimed.
