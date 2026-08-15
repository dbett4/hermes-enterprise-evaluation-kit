# Hermes Enterprise Evaluation Kit

> **Provenance:** Sanitized public extract published August 2026. Git history is
> publication history, not a full private archive. No client data, credentials, or
> spend-authorization secrets. Independent work — not an official Nous product,
> partnership, endorsement, or customer Hermes Enterprise deployment.

## The problem this answers

Hermes already gives you agent primitives: profiles, goals, tools, approvals,
boards, provider routing. That is not enough for a real organization.

A company still has to answer:

1. **Which jobs are appropriate** for an agent at all?
2. **Which approved setup** may run that job (model, tools, permissions, checks)?
3. **Who is accountable** when the answer needs human judgment?
4. **How do we prove** what ran — without trusting the model’s own narration?

This repository is a working prototype of that surrounding layer, pinned to one
exact Hermes release: **v0.20.0 / tag `v2026.8.3`**.

**One-line pitch:** turn a plain-language job into a policy-bounded Hermes run,
independent checks, and a written receipt — while keeping people in the loop
when judgment is required.

## What it is (and is not)

| It is | It is not |
|---|---|
| An evaluation kit for enterprise-shaped Hermes use | A customer production deployment |
| A version-pinned map of what Hermes v0.20 can and cannot cover | A claim that every Hermes feature is production-ready |
| Synthetic missions with offline, credential-free proof | Live customer data or live spend in the default path |
| Explicit gaps, negative tests, and human-review gates | A green script inventing human approval |
| Independent engineering evidence | Official Nous Enterprise product or partnership |

## The story in one pass

```text
Person describes a job
        ↓
Organization policy narrows what is allowed
        ↓
Kit selects one pre-approved configuration
        ↓
Hermes (or a local stand-in in the demo) runs inside that box
        ↓
Independent checks score the result
        ↓
Person decides when judgment is required
        ↓
JSON receipt records what happened
```

The demo’s important word is **`needs_review`**.

```text
$ bash scripts/demo_mission_s1.sh
=== Hermes Enterprise Evaluation Kit — S1 vendor exception ===
Org pack: packs/organizations/nimbus-synthetic

MISSION_DEMO_PASS ... terminal=needs_review
recommendation=defer-pending-legal oracle_passed=True
```

The local checker passed. The case still needs a person. A green script does
**not** get to pretend legal or policy judgment already happened.

## Three synthetic jobs

These are exercises, not customer work:

1. **Decide** — review a vendor-policy exception and return a *recommendation*,
   not a binding decision.
2. **Coordinate** — prepare an employee-offboarding packet without destructive
   actions.
3. **Act** — make and verify a reversible change in a local staging service;
   production promotion stays with a person.

Public-finance material is an optional pack, not the foundation of the kit.

## How the kit is built

Two layers:

1. **Vendor-neutral core** — qualification, authority, testing, operation, and
   retirement rules that do not depend on undocumented Hermes behavior.
2. **Hermes adapter (pinned)** — for each requirement, where it is handled:
   by Hermes itself, by configuration, by this kit, by surrounding infrastructure,
   or **not at all** (explicit gap).

That produces:

- a **capability map** (what is covered vs open)
- **policy packs** (org rules + workflow rules that do not silently widen permissions)
- **negative tests** (known bad paths must stop safely)
- **receipts** (reconstructable run records, with honest labels when evidence is weak)

### Plain-language glossary

| Term in the repo | What it means |
|---|---|
| Capability map / “318 rows” | Checklist: enterprise need → who handles it → pass, limit, or gap |
| Gap list | Seven things Hermes v0.20 does **not** fully cover for enterprise use |
| Neutral core | Shared operating rules with no Hermes-specific jargon baked in |
| Negative tests | Eight “this must fail safely” cases |
| Receipt | Written record of a run (inputs, config, checks, open human decision) |
| Attested receipt | Receipt tied to real Hermes executable bytes + native session evidence |
| Unattested / operator-recorded | Internally consistent notes someone typed; **not** proof of a live Hermes run |
| `needs_review` | Checker finished; a person still owns the decision |
| Preflight (214 tests) | Focused tests I ran against the pinned Hermes commit — not “all of Hermes” |
| Offline proof | `./scripts/proof.sh` — no API keys, no network, no new paid Hermes call |

## Try it in five minutes

Python 3.10+ and bash. No Hermes install, no model call, no API key, no network
for the default path.

```bash
git clone https://github.com/dbett4/hermes-enterprise-field-kit.git
cd hermes-enterprise-field-kit
pip install -r requirements.txt

# Story first: one synthetic mission end to end
bash scripts/demo_mission_s1.sh

# Then the full offline check suite
./scripts/proof.sh
```

`proof.sh` stops on first failure and prints `FIELD_KIT_PROOF_PASS` only when
everything offline succeeds. Details live in [PROOF.md](PROOF.md).

Useful pieces:

```bash
# Eight failure cases must stop safely
python3 scripts/run_negative_tests.py

# Shared core must stay vendor-neutral
python3 scripts/check_neutral_core.py

# Published capability map only
python3 scripts/verify_public_mapping.py
```

## What the offline check actually proves

When `./scripts/proof.sh` passes, you have re-checked that:

1. The published capability map is intact and schema-valid.
2. The eight known-bad paths still fail closed the way they should.
3. The shared operating core has not drifted into Hermes-only assumptions.
4. Receipt-verification guards still catch missing or mismatched runtime identity.
5. The older, weaker S1 record is still clearly labeled **unattested**.
6. The committed live one-shot receipt still verifies against its hashes and oracle.
7. The local S1 demo still completes and ends in **human review**, not fake approval.

It does **not** spend money, call a model, or run a new live Hermes mission.

## Live path (optional, spends money, gated)

Default demos stay offline on purpose.

A real Hermes CLI run is only allowed after spend controls are present (owner
authorization + matching portal cap). The runner rejects the wrong CLI version
and records executable identity, session evidence, and input/output digests.
See [`spend-authorization/`](spend-authorization/README.md).

**What is committed today**

| Record | Label | Meaning |
|---|---|---|
| [Live one-shot S1](reference-suite/runs/s1-decide-20260812-owner-chat-authorized/) | Native-runtime attested, still `needs_review` | Output is bound to Hermes v0.20.0 bytes and a native session. No external action. No human disposition yet. Cost figure is an **estimate** (~$0.41), not a billed invoice. Two execution-time exceptions stay visible in the receipt. |
| [Older S1](reference-suite/runs/s1-decide-20260811-025135/) | `operator-recorded-unattested` | Consistent notes; **not** treated as proof of a live Hermes run. |
| Other reference records | Dry runs | Local deterministic producers only. |

Verify the committed live receipt offline:

```bash
python3 scripts/verify_committed_attested_receipt.py
```

## What Hermes v0.20 covers — with limits

I ran a **214-test preflight** against the exact peeled commit
`3c27eb6234bf91b8ceee9e9071591b31e9b148cb` (tag `v2026.8.3`). That number is
pinned to that commit’s focused test list; it is not a claim about every Hermes
feature forever.

The preflight ended **`PASS_WITH_LIMITS`**. Examples of limits that matter:

- Managed scope is **not** an OS sandbox.
- Kanban is **not** an immutable audit log.
- Provider fallback is **not** intelligent model selection.
- Goals are still judged in part by the model — so this kit adds independent checks.

The map has **318 schema-valid rows** and a **seven-item gap list**. Those are
the engineering ledger behind the story above, not the story itself.

## Where to look next

| Path | Why |
|---|---|
| [`reference-suite/`](reference-suite/README.md) | The three synthetic jobs and committed run records |
| [`packs/`](packs/README.md) | How org policy and workflow rules combine |
| [`kit/mapping/`](kit/mapping/README.md) | Capability map and gap list |
| [`kit/preflight/`](kit/preflight/v0.20-preflight-report.md) | What was actually tested on Hermes v0.20 |
| [`kit/`](kit/README.md) | Longer deployment method |
| [`PROOF.md`](PROOF.md) | Command → pass condition → non-claim for every check |
| [`SUMMARY.md`](SUMMARY.md) | Short project status |
| [`scripts/`](scripts/) | Resolver, runner, checkers, guards |

## Sister project

If this kit answers **“can we govern Hermes for enterprise-shaped work?”**, the
related lab answers a different question:

**[Hermes Enterprise Deployment Lab](https://github.com/dbett4/hermes-enterprise-deployment-lab)** —
when an agent can touch an internal system, can we scope tools, require a separate
operator approval, and survive post-commit failure without double-writing?

Same family. Different question. Neither is a customer Hermes Enterprise deploy.

## Limits (read these)

- Synthetic cases and fictional org/policy docs only.
- Not a customer deployment, production identity integration, or immutable audit system.
- Default path is offline; live inference is gated and rare.
- One live one-shot has native attestation and still ends `needs_review`.
- Hermes cost figure is a catalog **estimate**, not provider-reported actual spend.
- Run records in-repo are ordinary files, not WORM/custody storage.
- Some private build inputs exist only as digests; you can verify the shipped map,
  not reconstruct every private generator input.
- Demo runs write ignored local directories; committed examples are the reviewed copies.

## Author

MIT licensed. Built by [Dave Bettner](https://davebettner.com).
