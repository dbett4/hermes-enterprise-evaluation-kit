#!/usr/bin/env python3
"""Organization-pack policy resolver for B07 mission runs."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ORG_PACK = ROOT / "packs/organizations/nimbus-synthetic"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def manifest_hash_for_bundle(bundle: dict[str, Any]) -> str:
    payload = copy.deepcopy(bundle)
    payload["manifest"] = {"canonicalization": "json-canonical-v1", "sha256": ""}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


def load_org_pack(org_pack_dir: Path | None = None) -> dict[str, Any]:
    base = org_pack_dir or DEFAULT_ORG_PACK
    return {
        "pack": load_json(base / "pack.json"),
        "envelope": load_json(base / "envelope.json"),
        "catalog": load_json(base / "bundle-catalog.json"),
        "blueprint": load_json(base / "blueprint.json"),
        "base": base,
    }


def load_bundle_from_catalog(catalog: dict[str, Any], bundle_id: str) -> dict[str, Any]:
    entry = next((b for b in catalog["bundles"] if b["bundle_id"] == bundle_id), None)
    if entry is None:
        raise ValueError(f"bundle not in catalog: {bundle_id}")
    path = ROOT / entry["path"]
    bundle = load_json(path)
    expected = manifest_hash_for_bundle(bundle)
    if bundle["manifest"]["sha256"] != expected:
        raise ValueError(f"bundle manifest hash mismatch for {bundle_id}")
    return bundle


def resolve_bundle(mission: dict[str, Any], org_pack: dict[str, Any] | None = None) -> dict[str, Any]:
    pack = org_pack or load_org_pack()
    catalog = pack["catalog"]
    envelope = pack["envelope"]
    task = mission["task_class"]
    action = mission["action_class"]
    authority = mission.get("authority_mode", "H")
    data_zone = mission.get("data_zone")

    if data_zone and data_zone not in envelope["allowed_data_zones"]:
        raise ValueError(f"data_zone {data_zone!r} not allowed by envelope {envelope['envelope_id']}")

    matches = [
        b
        for b in catalog["bundles"]
        if task in b["task_classes"]
        and action in b["action_classes"]
        and authority in b["authority_modes"]
    ]
    if len(matches) != 1:
        raise ValueError(f"resolver needs_policy_decision: {len(matches)} bundles for {mission}")
    return load_bundle_from_catalog(catalog, matches[0]["bundle_id"])


def resolve_profile_path(bundle: dict[str, Any]) -> Path:
    ref = bundle["hermes_profile"]["distribution_ref"]
    short = ref.rsplit("/", 1)[-1]
    registry = load_json(ROOT / "packs/profiles/REGISTRY.json")
    rel = registry.get(short)
    if not rel:
        raise ValueError(f"no local profile registry entry for {ref}")
    path = ROOT / rel
    if not (path / "manifest.json").is_file():
        raise ValueError(f"profile manifest missing: {path}")
    return path
