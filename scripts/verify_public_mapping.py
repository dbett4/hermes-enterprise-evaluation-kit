#!/usr/bin/env python3
"""Verify the public B05 mapping snapshot without private generator inputs."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "kit/mapping"
MANIFEST_PATH = MAPPING / "public-integrity.manifest.json"

PUBLIC_INPUT_PATHS = (
    "kit/mapping/neutral-requirements.json",
    "kit/mapping/evidence-catalog-v0.20.json",
    "kit/mapping/hermes-v0.20-row-decisions.json",
    "kit/mapping/hermes-v0.20-overrides.json",
    "kit/core/implementation-mapping-contract.md",
    "kit/core/control-traceability.md",
    "kit/preflight/v0.20-preflight-report.md",
)

PRIVATE_DIGEST_ONLY_PATHS = (
    "research/authority-access-architecture-draft.md",
    "build-tickets/B03-scoping-instrument-and-gates.md",
    "build-tickets/B05-deployment-mapping.md",
)


def load(name: str) -> dict:
    return json.loads((MAPPING / name).read_text(encoding="utf-8"))


def sha256_path(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify_manifest() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    require(manifest["manifest_id"] == "hermes-v0.20-public-integrity", "unexpected manifest id")
    require(
        manifest["verification_scope"] == "public_snapshot_only", "unexpected verification scope"
    )
    require(manifest["row_count"] == 318, "manifest row count is not 318")
    require(manifest["gap_count"] == 7, "manifest gap count is not seven")
    require(
        manifest["hermes_release"]["public_tag"] == "v2026.8.3",
        "unexpected Hermes public tag",
    )
    require(
        manifest["hermes_release"]["peeled_release_commit"]
        == "3c27eb6234bf91b8ceee9e9071591b31e9b148cb",
        "unexpected Hermes peeled release commit",
    )

    require(
        tuple(manifest["public_input_paths"]) == PUBLIC_INPUT_PATHS,
        "manifest public input path list mismatch",
    )
    for rel in PUBLIC_INPUT_PATHS:
        require((ROOT / rel).is_file(), f"missing shipped public input: {rel}")

    lock = load("b05-generation.lock.json")
    for rel in PRIVATE_DIGEST_ONLY_PATHS:
        require(rel in lock["inputs"], f"lock missing private provenance digest: {rel}")
        require(
            lock["inputs"][rel] == manifest["private_extraction_provenance"][rel],
            f"private provenance digest mismatch for {rel}",
        )
        require(
            not (ROOT / rel).exists(),
            f"private provenance path must not ship in public tree: {rel}",
        )

    return manifest


def main() -> int:
    verify_manifest()

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
    require(
        mapping["product_release"]["peeled_release_commit"]
        == "3c27eb6234bf91b8ceee9e9071591b31e9b148cb",
        "unexpected Hermes commit",
    )
    require(
        sha256_path("kit/mapping/hermes-v0.20-map.json") == lock["outputs"]["map"]["sha256"],
        "map hash differs from lock",
    )
    require(
        sha256_path("kit/mapping/capability-gap-ledger.json")
        == lock["outputs"]["ledger"]["sha256"],
        "ledger hash differs from lock",
    )

    print(
        "PUBLIC_MAPPING_PASS rows=318 gaps=7 release=v2026.8.3 "
        "public_inputs=7 private_provenance=3 locked_outputs=2"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
