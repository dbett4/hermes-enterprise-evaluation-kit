#!/usr/bin/env python3
"""Regenerate committed S3 receipts via local reference_staging_service."""

from __future__ import annotations

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def wait_for_health(base: str, timeout: float = 5.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{base}/health", timeout=1) as resp:
                if json.loads(resp.read()).get("status") == "ok":
                    return
        except Exception:
            time.sleep(0.05)
    raise RuntimeError(f"staging service not healthy at {base}")


def main() -> int:
    fixture = ROOT / "reference-suite/s3-act/fixtures/initial-state.json"
    proc = subprocess.Popen(
        [sys.executable, str(ROOT / "scripts/reference_staging_service.py"), "--port", "0", "--fixture", str(fixture)],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    )
    try:
        assert proc.stdout is not None
        startup = json.loads(proc.stdout.readline().strip())
        base = startup["listen"]
        wait_for_health(base)
        regen = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/run_reference_suite.py"),
                "--scenario",
                "s3-h",
                "--live-staging",
                "--staging-url",
                base,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if regen.returncode != 0:
            print(regen.stdout + regen.stderr)
            return regen.returncode
        regen_a = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/run_reference_suite.py"),
                "--scenario",
                "s3-a",
                "--live-staging",
                "--staging-url",
                base,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        if regen_a.returncode != 0:
            print(regen_a.stdout + regen_a.stderr)
            return regen_a.returncode
        for run_id in ("s3-act-h-20260806-dry-run", "s3-act-a-20260806-dry-run"):
            gp = json.loads((ROOT / "reference-suite/runs" / run_id / "golden-path.json").read_text(encoding="utf-8"))
            observed = gp["effect"]["observed_states"]
            if observed.get("staging_service_invoked") is not True:
                raise SystemExit(f"{run_id}: staging_service_invoked not true after live regen")
            if observed.get("mode") != "local-staging-observed":
                raise SystemExit(f"{run_id}: expected local-staging-observed mode")
        print(regen.stdout)
        return 0
    finally:
        proc.terminate()
        proc.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
