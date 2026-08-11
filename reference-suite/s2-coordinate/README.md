# S2 Coordinate — employee offboarding (synthetic)

Fictional mid-sized B2B SaaS **Nimbus Analytics, Inc.** Employee-offboarding packet across HRIS, IdP, MDM, ticketing, payroll, and twelve SaaS integrations. The archetype tests **bounded coordination** — assemble owners, gates, and a handoff packet without executing destructive effects.

This directory supplies fixtures and the public oracle surface. The **context-isolated desk probe** (B13) uses a frozen kit bundle plus a sealed answer key held outside the repo.

## Fixtures

| File | Role |
|---|---|
| `fixtures/fictional-org.json` | Company profile and escalation contacts |
| `fixtures/systems-inventory.json` | HRIS/IdP/MDM/ticketing/payroll + 12 SaaS apps |
| `fixtures/employee-case.json` | Termination scenario (legal hold, privileged access, after-hours) |
| `expected-oracle.json` | Public rubric-facing expected gate outcomes (no sealed answers) |

## Probe protocol

The sealed desk-probe record is held outside this public preview. Operator budget: **≤5 clarifications** answered from the sealed key only.
