#!/usr/bin/env python3
"""Assemble B09 evidence packets from accepted reference-suite runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RUNS_DIR = ROOT / "reference-suite/runs"
PACKETS_DIR = ROOT / "reference-suite/evidence-packets"

ACCEPTED_RUNS = (
    ("s1-decide-20260806-dry-run", "S1"),
    ("s3-act-h-20260806-dry-run", "S3"),
    ("s3-act-a-20260806-dry-run", "S3"),
)

RUN_ARTIFACTS: dict[str, list[str]] = {
    "s1-decide-20260806-dry-run": [
        "reference-suite/s1-decide/expected-oracle.json",
        "reference-suite/s1-decide/questionnaire.json",
        "reference-suite/s1-decide/vendor-policy-corpus/org-policy-v3.2.md",
        "reference-suite/s1-decide/vendor-policy-corpus/exception-request-cloudsync.md",
        "reference-suite/config-bundles/bundle-s1-decide.json",
    ],
    "s3-act-h-20260806-dry-run": [
        "reference-suite/s3-act/fixtures/initial-state.json",
        "reference-suite/s3-act/fixtures/target-state.json",
        "reference-suite/s3-act/fixtures/rollback-state.json",
        "reference-suite/config-bundles/bundle-s3-act-h.json",
    ],
    "s3-act-a-20260806-dry-run": [
        "reference-suite/s3-act/fixtures/initial-state.json",
        "reference-suite/s3-act/fixtures/target-state.json",
        "reference-suite/s3-act/fixtures/rollback-state.json",
        "reference-suite/config-bundles/bundle-s3-act-a.json",
        "reference-suite/runs/s3-act-h-20260806-dry-run/golden-path.json",
    ],
}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def expected_outcomes(receipt: dict[str, Any]) -> dict[str, Any]:
    run_id = receipt["run_id"]
    if run_id.startswith("s1-"):
        return {
            "type": "decide-recommendation",
            "recommendation": receipt["execution"]["producer_output"]["recommendation"],
            "external_action": receipt["execution"]["producer_output"].get("external_action", False),
            "checker_verdict": receipt["checker"]["verdict"],
            "terminal_status": receipt["terminal_status"],
        }
    states = receipt["effect"]["observed_states"]
    return {
        "type": "act-rate-limit",
        "pre_rpm": states["prestate"]["rate_limit"]["requests_per_minute"],
        "post_rpm": states["poststate"]["rate_limit"]["requests_per_minute"],
        "rollback_rpm": states["rollback"]["rate_limit"]["requests_per_minute"],
        "checker_verdict": receipt["checker"]["verdict"],
        "terminal_status": receipt["terminal_status"],
    }


def assemble_packet(run_id: str, suite_member: str) -> Path:
    receipt_path = RUNS_DIR / run_id / "golden-path.json"
    if not receipt_path.is_file():
        raise FileNotFoundError(f"missing accepted run receipt: {receipt_path}")
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("terminal_status") != "accepted":
        raise ValueError(f"run {run_id} is not accepted")

    out_dir = PACKETS_DIR / run_id
    if out_dir.exists():
        shutil.rmtree(out_dir)
    artifacts_dir = out_dir / "artifacts"
    artifacts_dir.mkdir(parents=True)

    artifacts: list[dict[str, Any]] = []
    lineage: list[dict[str, str]] = []

    receipt_rel = "artifacts/golden-path.json"
    receipt_bytes = receipt_path.read_bytes()
    (artifacts_dir / "golden-path.json").write_bytes(receipt_bytes)
    artifacts.append(
        {
            "artifact_id": f"{run_id}-golden-path",
            "role": "receipt",
            "path": receipt_rel,
            "sha256": sha256_bytes(receipt_bytes),
            "content_type": "application/json",
        }
    )

    for rel in RUN_ARTIFACTS.get(run_id, []):
        src = ROOT / rel
        if not src.is_file():
            raise FileNotFoundError(rel)
        dest_name = rel.replace("/", "__")
        dest_rel = f"artifacts/{dest_name}"
        data = src.read_bytes()
        (artifacts_dir / dest_name).write_bytes(data)
        aid = f"{run_id}-{dest_name}"
        artifacts.append(
            {
                "artifact_id": aid,
                "role": "supporting",
                "source_repo_path": rel,
                "path": dest_rel,
                "sha256": sha256_bytes(data),
                "content_type": "application/json" if rel.endswith(".json") else "text/markdown",
            }
        )
        lineage.append({"from": aid, "to": f"{run_id}-golden-path", "relation": "supports"})

    manifest = {
        "schema_version": "0.1",
        "packet_id": f"packet-{run_id}",
        "assembled_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "run_id": run_id,
        "suite_member": suite_member,
        "record_posture": {
            "store": "mutable-kit-artifact",
            "immutable_audit_claim": False,
            "reconstruction_class": "non-producer",
        },
        "artifacts": artifacts,
        "lineage": lineage,
        "expected_outcomes": expected_outcomes(receipt),
        "secrets_policy": "no-secrets-synthetic-only",
    }
    manifest_path = out_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return out_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="Assemble one run packet")
    args = parser.parse_args()
    targets = [(args.run_id, "S1" if args.run_id.startswith("s1") else "S3")] if args.run_id else list(ACCEPTED_RUNS)
    written = []
    for run_id, member in targets:
        path = assemble_packet(run_id, member)
        written.append(str(path.relative_to(ROOT)))
    print(json.dumps({"packets": written}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
