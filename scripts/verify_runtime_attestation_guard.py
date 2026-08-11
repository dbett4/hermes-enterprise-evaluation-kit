#!/usr/bin/env python3
"""Prove the live runner records CLI identity and rejects a release mismatch."""

from __future__ import annotations

import hashlib
import stat
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hermes_runtime import attest_hermes_runtime  # noqa: E402


def make_cli(root: Path, version: str) -> Path:
    path = root / "hermes"
    path.write_text(f"#!/usr/bin/env sh\nprintf '%s\\n' 'Hermes Agent {version}'\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)
    return path


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="hermes-attestation-") as raw:
        root = Path(raw)
        matching = make_cli(root, "0.20.0")
        evidence = attest_hermes_runtime(
            str(matching), accepted_versions=("0.20.0", "v2026.8.3")
        )
        assert evidence["status"] == "captured"
        assert evidence["binary_sha256"] == hashlib.sha256(matching.read_bytes()).hexdigest()
        assert evidence["source_commit_binding"] == "not_proven_by_cli_probe"

        mismatched = make_cli(root, "0.19.0")
        try:
            attest_hermes_runtime(str(mismatched), accepted_versions=("0.20.0", "v2026.8.3"))
        except RuntimeError:
            pass
        else:
            raise AssertionError("mismatched Hermes release did not fail closed")

    print("RUNTIME_ATTESTATION_GUARD_PASS captured_sha256=1 release_mismatch=blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
