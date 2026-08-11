# SPEC — Enterprise Agent Deployment Field Kit for Hermes

**As of:** 2026-08-04 · Amended by the 2026-08-04 generalized-enterprise directive, which supersedes the earlier finance-centered reference choice while preserving it as optional workflow-pack history.

## 1. Problem statement and destination

Hermes now exposes substantial individual, team, and cloud-facing primitives, but its documented v0.20 surfaces do not by themselves supply the organization-grade method this project addresses: workflow qualification, policy resolution, proportionate authority, acceptance proof, evidence custody, and owned handoff. This project builds the **Enterprise Agent Deployment Field Kit for Hermes** — generalized horizontal infrastructure consisting of a portable control kernel, version-pinned Hermes adapter, composable packs, and a synthetic decide/coordinate/act validation suite. Exact-tag capability evidence never substitutes for proof that a production deployment conforms to the same pin. (T02, T03, T15-amendment, B18.)

**Naming discipline:** *Hermes for organizations* is a descriptive phrase for the problem space. The author's asset is the **Enterprise Agent Deployment Field Kit for Hermes**; it is independent work, not an official Nous product, partnership, or endorsement. Product doctrine: `kit/DOCTRINE.md`.

Destination artifact: a public repo release containing the kit, completed synthetic reference-suite evidence, the desk-probe results, and one flagship explainer. Optional workflow packs may demonstrate specific domains later, but no domain is required for the generalized v0.1. Success is the Field Kit v0.1 passing its own desk test and validation set. (B18.)

## 2. Decisions and provenance

| Decision | Ticket |
|---|---|
| The construct is doctrine-derived; the kit must contain intake procedure, ordered process, per-stage decision rules, proportionality, acceptance tests, traceability, Hermes capability map, tacit-knowledge-free examples | T01 |
| Primary user/buyer: an enterprise-delivery / forward-deployed-engineering leader (a design persona; commercial sponsorship is a hypothesis) | T02, T17 |
| Spine JTBD: qualify → design controls → implement on native primitives → prove acceptance → hand over with evidence | T03 |
| Architecture: six-stage FDE lifecycle spine (Qualify; Map; Configure & Integrate; Assure & Authorize; Operate & Adopt; Review→continue/transfer/retire) + 8 cross-cutting assurance modules applied by proportionality | T04, T17-C11 |
| Three layers: vendor-neutral core / version-pinned Hermes deployment mapping (5 statuses: native, configuration, extension, surrounding-platform, unsupported gap) / private deployment memo. One validated snapshot; never evergreen | T05 |
| Deliverable: integrated Field Kit v0.1 + one flagship explainer; publishing arc demoted to derivatives | T06 |
| Reference validation: synthetic decide/coordinate/act suite; public-sector finance demoted to an optional workflow pack and removed from the v0.1 critical path | 2026-08-04 directive, B18 (supersedes T07/T08 for active scope) |
| Evidence: claim-evidence ledger (24-claim seed, committed), 12-item minimum validation set, "production-pattern evidence" labeling | T09 |
| IP bar: the desk test (frozen kit, ≤5 clarifications, gate-complete packet, published rubric; public rubric fully determines pass/fail) | T10, T17 |
| Partition: publish everything needed to pass the desk test; commercial calibration remains private | T11 |
| Failure register: 18 modes committed; Automatic rows enforce without renegotiation, Judgment rows are owner-steered | T13, T17 |
| Claim ladder: "Field Kit preview" → "Enterprise Agent Deployment Field Kit v0.1" (post desk-test + generalized validation set) → "proven reusable framework" (only after external field trial: foreign workflow/stack, predeclared baseline, ≥25% improvement, zero critical regression) | T09 amendment, T17-C09, B18 |
| Hermes pin: v0.20.0 / tag v2026.8.3; B04 preflight verdict `PASS_WITH_LIMITS`, so fallback v0.19/2026.7.20 is not triggered. Exact-tag evidence and production-topology evidence remain separate claim classes | T17-C05, B04 |
| Desk probe: employee offboarding at a fictional B2B SaaS company; fresh context-isolated operator + cross-family evaluator; sealed answer key; expected outcome is a bounded coordination agent | T17-C01/C02 |
| Portability probe: employee offboarding remains a held-out coordinate-archetype desk probe, not a product vertical | T17-C01/C02, B18 |
| Checker contract: independence = separate process/session/context, immutable producer output, no hidden reasoning, deterministic oracles; same-model = "role-separated checking" | T17-C08 |
| Suite rule: synthetic, inspectable inputs; declared workflow oracles; zero unexplained oracle failures or undispositioned material discrepancies; 8 committed cross-cutting negative cases | B18 (finance-specific T17-C07 retained only inside the optional pack) |
| Schema: Markdown records + JSON sidecars; claim-ledger minimum fields fixed | T17-C10 |

## 3. Non-goals and scope boundaries

Out of scope for v0.1 (T06 cuts): the six-piece publishing arc; per-module essays; partner commercial system (pricing/SOWs/staffing/support — secondary requirement); readiness scanner; comprehensive security questionnaire; productionizing domain packs; evergreen Hermes compatibility; full regulatory mappings; hermes-agent core-repo contributions (standing ground rule); any claim of enterprise SSO/tenant-isolation/adoption/ROI proof.

## 4. Current-state assumptions and external constraints

- Production deployments of hermes-agent v0.20.0 typically run inside a composite stack (Hermes plus separate governance/evidence controls). Production-pattern claims cite their own topology honestly and never borrow exact-tag conformance from the clean B04 test checkout. v0.20 includes a first-party team platform surface; surrounding controls remain separately attributed.
- Nous has announced Hermes Cloud organization provisioning, access controls, and unified billing through Portal. The public detail inspected does not establish that Cloud supplies this kit's implementation, evidence-custody, or lifecycle method; internal capabilities remain unknowable.
- Optional measured-cost runs require separate provider auth/spend authority and remain `NOT_RUN` in this slice. Portal is the preferred Nous-integrated candidate, not a generalized release dependency; only synthetic or otherwise explicitly approved non-client-data lanes may use any provider if later authorized.
- Publication gates: any production-pattern wording requires its own sanitized receipt series, and every release receives a secrets/privacy/source-license scrub.

## 5. Implementation design

### 5.0 Product doctrine and experience contract

- **Product promise:** give Hermes the mission; let organizational policy resolve model, provider, effort, tools, authority, and proof. This is a design target and kit control, not a claim that v0.20 already performs general task-aware selection.
- **Progressive disclosure:** the user sees mission, outcome, material approvals, status, and proof; the organization admin sets the operating envelope; the expert can inspect and override exact runtime choices within that envelope.
- **Policy resolution:** every run resolves to a named, preapproved configuration bundle before execution. An override is explicit, authorized, and receipted. Unsupported combinations stop for an admin/expert decision.
- **Architecture:** Hermes is the front door and reference execution path from day one. A portable authority/evidence/lifecycle kernel sits underneath. Every kernel concept requires a neutral definition, an explicit Hermes mapping, and a documented surrounding/manual fallback where Hermes lacks the control.
- **Composition:** versioned organization, capability, and workflow packs customize the system through an approved Assembly Blueprint. Packs may narrow authority but cannot silently expand the organization envelope or redefine core evidence semantics.
- **Reconciled Autonomy:** authority advances only when authorized intent, observed effect, and a separately classified disposition reconcile. Role-separated, model-independent, deterministic, and human verification are distinct claims. Promotion is only a recommendation until a policy owner ratifies it.
- **Evidence posture:** v0.1 Markdown/JSON records are append-oriented lifecycle artifacts, not immutable audit. A hash is provenance, not custody or enforcement; immutable claims require an independently controlled evidence store and verified retention/change controls.

Full doctrine: `kit/DOCTRINE.md`. Product architecture and pack contract: `kit/architecture.md` and `packs/README.md`. Exact capability boundaries: `kit/preflight/v0.20-preflight-report.md`.

### 5.1 Kit structure (public repo)
1. **Lifecycle guide** — the six-stage spine; each stage: entry conditions, required questions, decision rules, outputs, accountable owner, exception handling, exit gate.
2. **Scoping/decision instrument** — connected intake emitting: agent/no-agent decision, outcome baseline, workflow/action map, reversibility classification, risk tier, control plan, deployment boundary, acceptance plan, operating owner, unresolved-risk register.
3. **Gate artifacts** — blank form + completed example + acceptance criteria per required artifact; proportionality rules select modules by risk tier; waiver process included; the method must be able to conclude "do not agentize."
4. **Hermes deployment mapping** — five-status map pinned to the preflighted release (exact tag, commit SHA, package version, release date, topology); native primitives before extensions; conditional capabilities and untested release surfaces labeled; capability-gap ledger. No A2A, signing, verification-evidence, or Cloud claim is inherited from release notes without its own scoped proof.
5. **Reference suite** — synthetic decide, coordinate, and act archetypes (§5.2) with full evidence contracts.
6. **Desk-probe case** — the held-out offboarding coordinate archetype and defect log.
7. **Claim-evidence ledger + coverage matrix + composite architecture diagram.**
8. **Version/compatibility statement** — single-snapshot posture, stale-release banner rule.

### 5.2 Generalized reference suite

The active foundation spans three horizontal action archetypes against synthetic data: **S1 Decide** (vendor-policy exception assessment), **S2 Coordinate** (held-out employee-offboarding desk probe), and **S3 Act** (reversible staging rate-limit change with target readback and rollback). No one scenario is a product vertical or proof of universal generality. The detailed contract is `reference-suite/README.md`.

S1 requires one clean accepted run. S3 requires an accepted first-occurrence H seed, policy-owner ratification of the observed bounded rule, and a subsequent accepted A run. Both use workflow-specific deterministic oracles, fixed producer output, a separately controlled checker, human/policy dispositions, negative cases, and non-producer reconstruction from the evidence packet. S2 uses the T10/C02 context-isolated desk-test protocol. The checker claim states its exact independence class: separate process/session/context establishes role separation only; model independence, deterministic verification, and human independence require their own evidence.

The golden path resolves a predeclared policy bundle before execution and records the actual model, provider, effort, tool/policy manifest, runtime-reported values, independently observed values, latency, verifier evidence, and disposition. It does not imply general adaptive routing. Cost fields remain `NOT_RUN` until B10 executes under separate provider authority.

Public-sector finance is an optional workflow pack. Its prior jurisdiction, source, relationship, and domain-judgment gates reactivate only if that pack is explicitly resumed; they do not block the generalized product.

### 5.3 Data contracts
Markdown decision records and buyer packets; JSON sidecars for run/input/version manifests, claim ledger, run ledger, evidence relationships. Claim-ledger fields: claim ID, exact wording, scope, evidence class, artifact/evidence IDs, status, permitted wording, prohibited wording, validation date, applicable versions, owner. Stable IDs and deterministic links aid reconstruction but do not make the records immutable. Configuration identity hashes require canonical serialization plus retained referenced artifacts. Exact filenames/serialization are build-ticket detail.

### 5.4 Verification program
- **Kit:** the desk test (T10) with C02 protocol; two revision cycles maximum before the asset-stop tripwire.
- **Reference suite:** workflow-specific deterministic oracles; checker verdict; artifact/effect reconstruction by a non-producer; negative-case outcomes as committed.
- **Claims:** no public sentence without a ledger row; the 12-item validation set gates the v0.1 label.
- **Rollback/exception:** each stage's exit gate defines rejection and waiver; the failure register's Automatic rows are self-executing.

### 5.5 Approval gates (owner-only)
Final license text; final publication scrub and release; and any provider spend. Jurisdiction relationship clearance and domain-owner judgments are optional-pack gates only; they do not block the generalized build.

## 6. Implementation-time decisions (named, not hidden)
Exact filenames/serialization; license text; fault-fixture values; probe answer-key contents. Any future domain pack adds its own named domain-owner decisions without changing core semantics.

## 7. Ticket derivation
Build tickets B01–B18 structure the work, each citing its spec section with acceptance criteria and blocking edges. B04 completed the focused exact-release preflight; B01 established the Hermes-shaped doctrine and skeleton; B18 completed the generalized architecture and suite rebase after its active dependencies and guard were corrected. B17 authority-architecture v4 is ratified and design-complete. B02 has frozen its vendor-neutral lifecycle, authority, proportionality, exception, assurance, traceability, mapping-contract, and example rules; B03/B05 connect the artifacts and complete the pinned mapping. B07 executes the native-Hermes suite after B03/B05. B06 is superseded and retained only as optional-pack history. B10 remains optional and separately gated on provider auth/spend.
