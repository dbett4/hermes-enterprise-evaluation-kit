#!/usr/bin/env python3
"""Hermes CLI runtime helpers for B07 live mission runs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class HermesInvocation:
    binary: str
    profile_name: str
    stdout: str
    stderr: str
    returncode: int
    latency_ms: int


def attest_hermes_runtime(
    hermes_bin: str,
    *,
    accepted_versions: tuple[str, ...],
) -> dict[str, Any]:
    """Capture native CLI identity before a run and fail on release mismatch.

    This attests the executable bytes and its own version output. It does not
    prove how those bytes were built or independently bind them to a source
    commit; callers must state that boundary.
    """
    resolved = Path(hermes_bin).expanduser().resolve()
    if not resolved.is_file():
        raise RuntimeError(f"Hermes executable is not a file: {resolved}")
    if not os.access(resolved, os.X_OK):
        raise RuntimeError(f"Hermes executable is not executable: {resolved}")

    attempts: list[dict[str, Any]] = []
    for version_args in ([hermes_bin, "--version"], [hermes_bin, "version"]):
        proc = subprocess.run(version_args, capture_output=True, text=True, check=False)
        output = (proc.stdout or proc.stderr).strip()
        attempt = {
            "argv": ["hermes", *version_args[1:]],
            "returncode": proc.returncode,
            "output": output[:500],
        }
        attempts.append(attempt)
        if (
            proc.returncode == 0
            and output
            and any(version in output for version in accepted_versions)
        ):
            return {
                "status": "captured",
                "binary_path": str(resolved),
                "binary_sha256": hashlib.sha256(resolved.read_bytes()).hexdigest(),
                "version_probe": attempt,
                "source_commit_binding": "not_proven_by_cli_probe",
            }

    raise RuntimeError(
        "Hermes runtime version did not match the pinned release: "
        + json.dumps(attempts, sort_keys=True)
    )


def find_hermes_binary(explicit: str | None = None) -> str | None:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.is_file() and os.access(path, os.X_OK):
            return str(path)
        return shutil.which(explicit)
    found = shutil.which("hermes")
    if found:
        return found
    hermes_home = Path(os.environ.get("HERMES_HOME", Path.home() / ".hermes"))
    candidates = [
        hermes_home / "hermes-agent/venv/bin/hermes",
        hermes_home / "bin/hermes",
        Path.home() / ".local/bin/hermes",
    ]
    for candidate in candidates:
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def install_profile_distribution(*, hermes_bin: str, profile_dir: Path, profile_name: str) -> None:
    proc = subprocess.run(
        [
            hermes_bin,
            "profile",
            "install",
            str(profile_dir),
            "--name",
            profile_name,
            "-y",
            "--force",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"hermes profile install failed ({proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}"
        )


def run_hermes_oneshot(*, hermes_bin: str, profile_name: str, prompt: str) -> HermesInvocation:
    start = time.perf_counter()
    proc = subprocess.run(
        [hermes_bin, "-p", profile_name, "-z", prompt],
        capture_output=True,
        text=True,
        check=False,
    )
    latency_ms = int((time.perf_counter() - start) * 1000)
    return HermesInvocation(
        binary=hermes_bin,
        profile_name=profile_name,
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
        latency_ms=latency_ms,
    )


def parse_producer_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if not text:
        raise ValueError("empty hermes response")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("hermes response contained no JSON object") from None
        return json.loads(match.group(0))


def _config_get(hermes_bin: str, profile_name: str, key: str) -> str | None:
    proc = subprocess.run(
        [hermes_bin, "-p", profile_name, "config", "get", key],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return None


def runtime_reported_from_config(hermes_bin: str, profile_name: str) -> dict[str, str]:
    """Best-effort model/provider readback via hermes config get."""
    model = _config_get(hermes_bin, profile_name, "model.default") or "unknown"
    provider = _config_get(hermes_bin, profile_name, "model.provider")
    if not provider:
        provider = _config_get(hermes_bin, profile_name, "provider.default")
    if not provider:
        provider = "unknown"
    return {"model": model, "provider": provider}
