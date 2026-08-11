"""B03 enforcement patch oracles — derived from external prior-art review (2026-08-06).

Validates negative fixtures and terminal-state vocabulary without requiring
intake-schema v3. Wired into tests; evaluator integration is a follow-on lane.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
FIXTURE = ROOT / "fixtures" / "enforcement-negative-denied-sibling-search.json"

TERMINAL_STATES = frozenset({"denied_by_policy", "boundary_unavailable", "approved_pending_human"})


def load_denied_sibling_fixture() -> dict[str, Any]:
    return json.loads(FIXTURE.read_text())


def evaluate_search_result(result_envelope: dict[str, Any], fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return pass/fail for denied-sibling search invariant."""
    fixture = fixture or load_denied_sibling_fixture()
    oracle = fixture["oracle"]
    text = json.dumps(result_envelope, sort_keys=True).casefold()
    leaks = [token for token in oracle["must_not_contain"] if token.casefold() in text]
    return {
        "fixture_id": fixture["fixture_id"],
        "passed": not leaks,
        "leaks": leaks,
        "terminal_state_vocabulary": sorted(TERMINAL_STATES),
    }


def classify_terminal_state(*, policy_denied: bool, boundary_down: bool, human_pending: bool) -> str:
    if human_pending:
        return "approved_pending_human"
    if boundary_down and not policy_denied:
        return "boundary_unavailable"
    return "denied_by_policy"
