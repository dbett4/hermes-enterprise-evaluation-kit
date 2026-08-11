#!/usr/bin/env python3
"""Hermes CLI runtime helpers for B07 live mission runs."""

from __future__ import annotations

import json
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


def find_hermes_binary(explicit: str | None = None) -> str | None:
    if explicit:
        path = Path(explicit)
        return str(path) if path.is_file() else explicit if shutil.which(explicit) else None
    found = shutil.which("hermes")
    if found:
        return found
    hermes_home = Path(__import__("os").environ.get("HERMES_HOME", Path.home() / ".hermes"))
    candidates = [
        hermes_home / "hermes-agent/venv/bin/hermes",
        hermes_home / "bin/hermes",
        Path.home() / ".local/bin/hermes",
    ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return None


def install_profile_distribution(*, hermes_bin: str, profile_dir: Path, profile_name: str) -> None:
    proc = subprocess.run(
        [hermes_bin, "profile", "install", str(profile_dir), "--name", profile_name, "-y", "--force"],
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


def runtime_reported_from_config(hermes_bin: str, profile_name: str) -> dict[str, str]:
    """Best-effort model/provider readback via hermes config get."""
    model = "unknown"
    provider = "unknown"
    for key in ("model.default", "provider.default"):
        proc = subprocess.run(
            [hermes_bin, "-p", profile_name, "config", "get", key],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            if key.endswith("model.default"):
                model = proc.stdout.strip()
            else:
                provider = proc.stdout.strip()
    return {"model": model, "provider": provider}
