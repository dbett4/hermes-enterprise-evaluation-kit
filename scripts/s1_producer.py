#!/usr/bin/env python3
"""Derive S1 vendor-policy recommendation from questionnaire inputs only."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def produce_s1_vendor_exception(
    s1_dir: Path | None = None,
    *,
    questionnaire: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build producer output from questionnaire answers — never reads expected-oracle.json."""
    if questionnaire is None:
        if s1_dir is None:
            raise ValueError("s1_dir or questionnaire required")
        questionnaire = load_json(s1_dir / "questionnaire.json")
    by_id = {item["id"]: item for item in questionnaire["questions"]}

    conditions: list[str] = []
    recommendation = "approve"

    if by_id["Q1"]["answer"]:
        conditions.append("Reduce requested retention to 12 months or obtain executive waiver record")
        recommendation = "defer-pending-legal"

    if not by_id["Q4"]["answer"]:
        conditions.append("Obtain Legal-approved contractual addendum with explicit expiry")
        recommendation = "defer-pending-legal"

    if by_id["Q1"]["answer"]:
        conditions.append(
            "Separate deletion schedule for raw logs (12 months) vs aggregates (max 12 months unless waived)"
        )

    citations: list[str] = []
    seen: set[str] = set()
    for item in questionnaire["questions"]:
        ref = item["evidence_ref"]
        if ref not in seen:
            seen.add(ref)
            citations.append(ref)

    for source in questionnaire.get("citation_sources", []):
        if source.get("apply_when_recommendation") not in (None, recommendation):
            continue
        doc = source["document"]
        for anchor in source.get("anchors", []):
            ref = f"{doc}#{anchor}"
            if ref not in seen:
                seen.add(ref)
                citations.append(ref)

    return {
        "recommendation": recommendation,
        "conditions": conditions,
        "citations": citations,
        "external_action": False,
    }
