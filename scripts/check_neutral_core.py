#!/usr/bin/env python3
"""Validate the frozen B02 vendor-neutral control kernel."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STAGE_FILES = (
    "kit/lifecycle/01-qualify.md",
    "kit/lifecycle/02-map.md",
    "kit/lifecycle/03-configure-integrate.md",
    "kit/lifecycle/04-assure-authorize.md",
    "kit/lifecycle/05-operate-adopt.md",
    "kit/lifecycle/06-review-transfer-retire.md",
)

ASSURANCE_FILES = (
    "kit/assurance/authority-human-oversight.md",
    "kit/assurance/quality-verification.md",
    "kit/assurance/evidence-traceability.md",
    "kit/assurance/identity-security-data-legal.md",
    "kit/assurance/integration-change-supply-chain.md",
    "kit/assurance/reliability-continuity.md",
    "kit/assurance/economics-value.md",
    "kit/assurance/adoption-ownership.md",
)

CORE_FILES = (
    "kit/core/README.md",
    "kit/core/proportionality.md",
    "kit/core/waivers-and-exceptions.md",
    "kit/core/control-traceability.md",
    "kit/core/implementation-mapping-contract.md",
    "kit/core/examples-and-counterexamples.md",
)

NEUTRAL_FILES = (
    "kit/lifecycle/README.md",
    *STAGE_FILES,
    "kit/assurance/README.md",
    *ASSURANCE_FILES,
    *CORE_FILES,
)

VENDOR_PATTERNS = (
    r"\bHermes\b",
    r"\bNous\b",
    r"\bPortal\b",
    r"\bOpenRouter\b",
    r"\bKanban\b",
    r"\bIron Proxy\b",
    r"\bmanaged scope\b",
    r"\bprofile distributions?\b",
    r"\bcompletion contracts?\b",
    r"\bv0\.20\b",
)

STAGE_HEADINGS = (
    "Entry conditions",
    "Required questions",
    "Decision rules",
    "Outputs",
    "Accountable owner",
    "Exceptions and escalation",
    "Exit gate and acceptance tests",
)

ASSURANCE_HEADINGS = (
    "Risk signals",
    "Control rules",
    "Implementation slots",
    "Required evidence",
    "Metrics and triggers",
    "Tier application",
    "Exit rule",
)

MODULE_NAMES = (
    "Authority & human oversight",
    "Quality & verification",
    "Evidence & traceability",
    "Identity, security, data & legal",
    "Integration, change & supply chain",
    "Reliability & continuity",
    "Economics & value",
    "Adoption & ownership",
)


def read(root: Path, relative: str) -> str:
    path = root / relative
    if not path.is_file():
        raise AssertionError(f"missing required file: {relative}")
    return path.read_text(encoding="utf-8")


def check(root: Path = ROOT) -> list[str]:
    failures: list[str] = []

    for relative in NEUTRAL_FILES:
        text = read(root, relative)
        for pattern in VENDOR_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                failures.append(f"{relative}: vendor-specific term matches {pattern!r}")
        for stale in ("preview stub", "Placeholder:", "rules not frozen"):
            if stale.casefold() in text.casefold():
                failures.append(f"{relative}: stale scaffold marker remains: {stale!r}")

    lifecycle = read(root, "kit/lifecycle/README.md")
    for stage in range(1, 7):
        if f"{stage}." not in lifecycle:
            failures.append(f"lifecycle README missing ordered stage {stage}")
    for phrase in (
        "do_not_agentize",
        "not_ready_to_authorize",
        "Ordered procedure and dependencies",
        "Every stage applies all eight assurance modules",
    ):
        if phrase not in lifecycle:
            failures.append(f"lifecycle README missing required contract: {phrase!r}")

    for relative in STAGE_FILES:
        text = read(root, relative)
        if "**Status:** frozen vendor-neutral kernel" not in text:
            failures.append(f"{relative}: stage is not frozen")
        for heading in STAGE_HEADINGS:
            if f"## {heading}" not in text:
                failures.append(f"{relative}: missing heading {heading!r}")
        if "Negative test:" not in text:
            failures.append(f"{relative}: missing explicit negative test")

    for relative in ASSURANCE_FILES:
        text = read(root, relative)
        if "**Status:** frozen vendor-neutral kernel" not in text:
            failures.append(f"{relative}: assurance module is not frozen")
        for heading in ASSURANCE_HEADINGS:
            if f"## {heading}" not in text:
                failures.append(f"{relative}: missing heading {heading!r}")

    core_readme = read(root, "kit/core/README.md")
    for phrase in (
        "Suitability and intake procedure",
        "Ordered process and cross-stage dependencies",
        "Per-stage questions",
        "Risk-tiered applicability",
        "Acceptance, negative-test",
        "Control traceability",
        "Version-pinned capability",
        "Examples and counterexamples",
    ):
        if phrase not in core_readme:
            failures.append(f"core README missing T01 framework element: {phrase!r}")

    proportionality = read(root, "kit/core/proportionality.md")
    for tier in ("T0", "T1", "T2", "T3", "T4"):
        if tier not in proportionality:
            failures.append(f"proportionality procedure missing tier {tier}")
    for depth in ("L0", "L1", "L2", "L3"):
        if depth not in proportionality:
            failures.append(f"proportionality procedure missing depth {depth}")
    for name in MODULE_NAMES:
        short_name = name.split(" & ", 1)[0].split(",", 1)[0]
        if short_name not in proportionality:
            failures.append(f"proportionality base profile missing module {name!r}")

    traceability = read(root, "kit/core/control-traceability.md")
    for name in MODULE_NAMES:
        if f"| {name} |" not in traceability:
            failures.append(f"control traceability missing module row: {name}")
    for phrase in ("risk → control rule → implementation slot → evidence → metric", "known bypass"):
        if phrase not in traceability:
            failures.append(f"control traceability missing requirement: {phrase!r}")

    waivers = read(root, "kit/core/waivers-and-exceptions.md")
    for heading in ("Non-waivable conditions", "Required waiver record", "Procedure", "Gate behavior"):
        if f"## {heading}" not in waivers:
            failures.append(f"waiver procedure missing section: {heading}")
    for phrase in ("cannot approve its own material waiver", "unknown acceptance-critical evidence"):
        if phrase not in waivers:
            failures.append(f"waiver procedure missing hard rule: {phrase!r}")

    mapping = read(root, "kit/core/implementation-mapping-contract.md")
    for status in ("`native`", "`configuration`", "`extension`", "`surrounding-platform`", "`unsupported-gap`"):
        if status not in mapping:
            failures.append(f"implementation mapping missing status {status}")

    examples = read(root, "kit/core/examples-and-counterexamples.md")
    for phrase in ("do_not_agentize", "not_ready_to_authorize", "conventional automation", "first occurrence"):
        if phrase not in examples:
            failures.append(f"examples/counterexamples missing outcome: {phrase!r}")

    return failures


def main() -> int:
    failures = check(ROOT)
    if failures:
        print("NEUTRAL_CORE_FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("NEUTRAL_CORE_PASS")
    print(f"checked_files={len(NEUTRAL_FILES)}")
    print("stages=6")
    print("assurance_modules=8")
    print("vendor_specific_terms=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
