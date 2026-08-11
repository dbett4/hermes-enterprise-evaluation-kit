#!/usr/bin/env python3
"""Verify the public B05 mapping artifacts without private generator inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "kit/mapping"


def load(name: str) -> dict:
    return json.loads((MAPPING / name).read_text(encoding="utf-8"))


def sha256(name: str) -> str:
    return hashlib.sha256((MAPPING / name).read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    artifacts = [
        ("hermes-v0.20-map.json", "hermes-v0.20-map.schema.json"),
        ("capability-gap-ledger.json", "capability-gap-ledger.schema.json"),
        ("evidence-catalog-v0.20.json", "evidence-catalog-v0.20.schema.json"),
        ("hermes-v0.20-row-decisions.json", "hermes-v0.20-row-decisions.schema.json"),
        ("hermes-v0.20-overrides.json", "hermes-v0.20-overrides.schema.json"),
        ("b05-generation.lock.json", "b05-generation.lock.schema.json"),
    ]
    schemas = {
        schema["$id"]: schema
        for path in MAPPING.glob("*.schema.json")
        if "$id" in (schema := json.loads(path.read_text(encoding="utf-8")))
    }
    for document_name, schema_name in artifacts:
        schema = load(schema_name)
        resolver = RefResolver.from_schema(schema, store=schemas)
        Draft202012Validator(schema, resolver=resolver).validate(load(document_name))

    mapping = load("hermes-v0.20-map.json")
    ledger = load("capability-gap-ledger.json")
    lock = load("b05-generation.lock.json")
    require(len(mapping["rows"]) == 318, "map row count is not 318")
    require(mapping["summary"]["gap_count"] == 7, "map gap count is not seven")
    require(len(ledger["entries"]) == 7, "gap ledger entry count is not seven")
    require(mapping["product_release"]["public_tag"] == "v2026.8.3", "unexpected Hermes tag")
    require(mapping["product_release"]["peeled_release_commit"] == "3c27eb6234bf91b8ceee9e9071591b31e9b148cb", "unexpected Hermes commit")
    require(sha256("hermes-v0.20-map.json") == lock["outputs"]["map"]["sha256"], "map hash differs from lock")
    require(sha256("capability-gap-ledger.json") == lock["outputs"]["ledger"]["sha256"], "ledger hash differs from lock")

    print("PUBLIC_MAPPING_PASS rows=318 gaps=7 release=v2026.8.3 locked_outputs=2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
