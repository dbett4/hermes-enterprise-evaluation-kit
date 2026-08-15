# Reference exercises

This directory tests the design against three different kinds of work: making a
recommendation, coordinating a handoff, and changing a system. The organization and
all inputs are fictional so the examples do not depend on client data or imply a real
customer relationship.

## The three jobs

| ID | Job | Scenario | What I check |
|---|---|---|---|
| **S1** | Decide | Review a vendor-policy exception and recommend what to do; do not make the external decision | Source citations, policy rules, a separate checker, and human review |
| **S2** | Coordinate | Prepare an employee-offboarding packet across fictional systems; do not disable accounts or perform another destructive action | Multi-owner handoff, clarification limits, and a deliberate `not_ready_to_authorize` outcome |
| **S3** | Act | Apply one operator-approved change to the [Hermes Enterprise Deployment Lab](https://github.com/dbett4/hermes-enterprise-deployment-lab), survive a post-commit failure, and resume; do not promote to production | Narrow tool surface, approval separation, target readback, exactly-once recovery, and the staging/production stop line |

The committed S1 and S3 examples include dry runs with reconstruction records. The
older S1 directory `runs/s1-decide-20260811-025135` is labeled
`operator-recorded-unattested`. Its output is internally consistent, but the run did
not save native CLI identity, so it does not show that the declared Hermes release,
provider, or model produced the result. S2's fixtures and expected checks are public;
its earlier desk-probe record is not included in this preview.

The newer S1 directory `runs/s1-decide-20260812-owner-chat-authorized` is a live
one-shot with a captured executable digest, native CLI session ID, frozen model output,
and recomputed oracle pass. It remains `needs_review`: no external action or human
disposition occurred, the recorded $0.406986 is an estimate rather than an actual
billed amount, and its two execution-time exceptions remain in the receipt.

## Rules shared by the exercises

Each executed job must:

- start from an authorized mission and an approved fictional organization policy;
- choose exactly one configuration from the approved catalog;
- freeze the produced output before a checker evaluates it;
- label deterministic, separate-session, different-model, and human review accurately;
- read important results from the output or target system instead of trusting the
  producer's summary;
- record exceptions and a final state;
- save the selected model, provider, effort, and any fallback in the run record; and
- avoid claims about immutable audit, enterprise IAM, production readiness, or adaptive
  routing that these exercises do not establish.

S1 needs a clean accepted run that someone other than the producer can reconstruct.
S3 needs both its first human-released change and the later preauthorized staging run;
the pair is the result, not just the more autonomous run. S2 remains a context-isolated
desk exercise.

## The S3 Act target

Act is the archetype where a wrong answer changes something, so its target is a real
system with real controls rather than a prop this repository wrote for itself. That
system is the sister repository, cloned side by side:

```bash
git clone https://github.com/dbett4/hermes-enterprise-deployment-lab
cd hermes-enterprise-deployment-lab
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt \
                      -r workflow-runner/requirements.txt \
                      -r enterprise-mcp/requirements.txt
```

Then, from this repository:

```bash
bash scripts/demo_mission_s3.sh
```

`scripts/deployment_lab_backend.py` resolves the lab (`HERMES_DEPLOYMENT_LAB`, or a
sibling directory), boots its `enterprise-api` on a loopback port, and runs
`scripts/deployment_lab_act_client.py` — an MCP client that calls the lab's own
`propose_incident_plan` and `apply_incident_plan` tools over stdio. The approval
separation, the approval-scoped idempotency key, the injected post-commit 500, and the
replayed resume are all the lab's mechanics. This kit selects the configuration, runs
the mission, and checks the result.

The run is written to `runs/s3-act-h-deployment-lab/` — a separate run id, so a local
Act run never overwrites the committed dry-run exemplars. The receipt records the lab
root, its commit, and the tools called under
`run_mode.deployment_lab`, and the oracle
`s3-approval-idempotency-oracle-h` fails the run if the mutating tool is visible under
the read/plan allowlist, an unapproved request changes the store, a capability reaches
the requester, the fault is not surfaced, resume does not replay, or the store ends with
anything other than exactly one record.

| Backend | Flag | What it is |
|---|---|---|
| Deployment lab | `--staging-backend deployment-lab` (default when resolvable) | Real MCP tools, real approval/idempotency/resume |
| Toy service | `--staging-backend reference-service` | **Fallback.** `scripts/reference_staging_service.py`: change plus exact rollback, no approval separation, no idempotency, no resume |
| Fixtures | `--staging-backend fixture` | Committed prestate/poststate/rollback files; nothing is invoked |

If the lab is absent, `./scripts/proof.sh` prints `FIELD_KIT_PROOF_ACT_SKIPPED` and does
not run the Act mission. It never silently substitutes the toy target.

The suite passes only when each workflow's programmed checks pass, every important
difference is explained, and no blocking `unknown` remains. A domain-specific
zero-difference rule belongs in that workflow's pack rather than in the reusable core.
