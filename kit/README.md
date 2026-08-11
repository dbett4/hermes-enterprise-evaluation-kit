# The deployment method

This directory contains the longer version of the method behind the runnable examples.
Most readers should start with the [root README](../README.md) and come here only when
they want to inspect a design decision.

- [Product principles](DOCTRINE.md) explains the choices I made about configuration,
  authority, and user experience.
- [Architecture](architecture.md) shows how organization policy, reusable packs, and
  the Hermes adapter fit together.
- [Core](core/README.md) contains the runtime-neutral operating rules.
- [Lifecycle](lifecycle/README.md) walks through qualification, design, build, testing,
  operation, and retirement.
- [Assurance](assurance/README.md) is the cross-check list used at each lifecycle stage.
- [Intake](instrument/README.md) contains the schema and deterministic decision rules.
- [Gates](gates/README.md) contains the decision forms and acceptance checks.
- [Mapping](mapping/README.md) connects each requirement to the pinned Hermes release.
- [Preflight](preflight/v0.20-preflight-report.md) records the exact-release tests.
- [Golden path](golden-path.md) describes the mission runner and JSON run format.

This is still a preview. The status notes in individual documents say which parts are
implemented, stable design, or future work.
