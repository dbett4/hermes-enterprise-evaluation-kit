#!/usr/bin/env python3
"""Resolve, boot, and drive the Hermes Enterprise Deployment Lab for S3 Act.

The Act archetype needs a target system whose approval separation, idempotency,
and post-commit recovery are real rather than re-implemented here. That system
is the sister repository:

    https://github.com/dbett4/hermes-enterprise-deployment-lab

It is a documented side-by-side clone, not a PyPI package: the lab ships an
application (FastAPI service, MCP server, workflow runner) with pinned
dependencies of its own, so this kit resolves it on disk and runs it under its
own interpreter instead of importing it into this environment.

Resolution order for the lab checkout:

    1. ``HERMES_DEPLOYMENT_LAB`` environment variable
    2. ``../hermes-enterprise-deployment-lab`` next to this repository

Interpreter: ``<lab>/.venv/bin/python`` when present, otherwise
``HERMES_DEPLOYMENT_LAB_PYTHON``, otherwise this interpreter (which then has to
provide ``fastmcp``, ``httpx``, ``fastapi`` and ``uvicorn`` itself).

Everything stays on loopback. No network egress, no credentials, no model call.
The lab's fixture tokens are non-secret test data published in its
``.env.example``.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "scripts/deployment_lab_act_client.py"
DEFAULT_SIBLING = ROOT.parent / "hermes-enterprise-deployment-lab"
READ_TOKEN = "lab-read-token"
WRITE_TOKEN = "lab-write-token"


class DeploymentLabUnavailable(RuntimeError):
    """The lab checkout or its dependencies are not present on this machine."""


def resolve_lab_root(explicit: str | Path | None = None) -> Path:
    candidates = []
    if explicit:
        candidates.append(Path(explicit))
    env_root = os.environ.get("HERMES_DEPLOYMENT_LAB")
    if env_root:
        candidates.append(Path(env_root))
    candidates.append(DEFAULT_SIBLING)
    for candidate in candidates:
        root = candidate.expanduser()
        if (root / "enterprise-mcp/enterprise_mcp/server.py").is_file():
            return root.resolve()
    raise DeploymentLabUnavailable(
        "hermes-enterprise-deployment-lab not found. Clone it beside this repository "
        "or set HERMES_DEPLOYMENT_LAB=/path/to/hermes-enterprise-deployment-lab."
    )


def resolve_lab_python(lab_root: Path) -> Path:
    venv_python = lab_root / ".venv/bin/python"
    if venv_python.is_file():
        return venv_python
    override = os.environ.get("HERMES_DEPLOYMENT_LAB_PYTHON")
    if override:
        python = Path(override).expanduser()
        if python.is_file():
            return python
        raise DeploymentLabUnavailable(f"HERMES_DEPLOYMENT_LAB_PYTHON is not a file: {python}")
    return Path(sys.executable)


def check_lab_dependencies(lab_python: Path) -> None:
    probe = subprocess.run(
        [str(lab_python), "-c", "import fastmcp, httpx, fastapi, uvicorn"],
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode != 0:
        raise DeploymentLabUnavailable(
            f"{lab_python} cannot import the lab's runtime dependencies "
            f"(fastmcp, httpx, fastapi, uvicorn): {probe.stderr.strip()}"
        )


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_health(api_url: str, timeout: float = 60.0) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{api_url}/healthz", timeout=2) as response:
                if response.status == 200:
                    return
        except (urllib.error.URLError, OSError):
            time.sleep(0.25)
    raise DeploymentLabUnavailable(f"enterprise-api never became healthy at {api_url}")


def run_act_mission(
    *,
    lab_root: Path | None = None,
    workdir: Path | None = None,
    run_id: str = "evaluation-kit-s3-act",
) -> dict[str, Any]:
    """Boot the lab's enterprise-api and drive its MCP tools through the Act arc."""
    root = resolve_lab_root(lab_root)
    lab_python = resolve_lab_python(root)
    check_lab_dependencies(lab_python)

    work = Path(workdir) if workdir else ROOT / ".deployment-lab-act"
    work.mkdir(parents=True, exist_ok=True)
    api_log = work / "enterprise-api.log"
    audit_path = work / "act-audit.jsonl"
    approval_path = work / "act-approvals.json"
    # The lab's approval store is durable and remembers applied incident/action
    # pairs. This mission always starts from an empty target system, so it must
    # also start from an empty approval store, or a prior run's terminal record
    # refuses this run's grant before the fault can even be injected.
    for stale in (audit_path, approval_path):
        stale.unlink(missing_ok=True)
    port = free_port()
    api_url = f"http://127.0.0.1:{port}"

    api_env = os.environ.copy()
    api_env.update(
        {
            "PYTHONPATH": str(root / "enterprise-api"),
            "ENTERPRISE_API_TOKEN": READ_TOKEN,
            "ENTERPRISE_API_WRITE_TOKEN": WRITE_TOKEN,
        }
    )
    api_env.pop("ACTION_STORE_PATH", None)  # in-memory store: no file to reconcile
    with api_log.open("w", encoding="utf-8") as log:
        api = subprocess.Popen(
            [
                str(lab_python),
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ],
            cwd=str(root / "enterprise-api"),
            env=api_env,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
    try:
        wait_for_health(api_url)
        completed = subprocess.run(
            [
                str(lab_python),
                str(CLIENT),
                "--lab-root",
                str(root),
                "--api-url",
                api_url,
                "--read-token",
                READ_TOKEN,
                "--write-token",
                WRITE_TOKEN,
                "--audit-log",
                str(audit_path),
                "--approval-store",
                str(approval_path),
                "--run-id",
                run_id,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        api.terminate()
        try:
            api.wait(timeout=10)
        except subprocess.TimeoutExpired:  # pragma: no cover - defensive
            api.kill()

    if completed.returncode != 0:
        raise RuntimeError(
            "deployment-lab Act mission failed "
            f"({completed.returncode}): {completed.stderr.strip() or completed.stdout.strip()}"
        )
    observations = json.loads(completed.stdout.strip().splitlines()[-1])
    observations["lab_python"] = str(lab_python)
    observations["lab_commit"] = lab_commit(root)
    return observations


def lab_commit(lab_root: Path) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(lab_root), "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() or None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab-root", default=None)
    parser.add_argument("--workdir", default=None)
    parser.add_argument(
        "--probe",
        action="store_true",
        help="Only report whether the lab is resolvable and runnable; exit 3 when it is not",
    )
    args = parser.parse_args(argv)
    try:
        if args.probe:
            root = resolve_lab_root(args.lab_root)
            python = resolve_lab_python(root)
            check_lab_dependencies(python)
            print(json.dumps({"deployment_lab": str(root), "python": str(python)}, sort_keys=True))
            return 0
        observations = run_act_mission(lab_root=args.lab_root, workdir=args.workdir)
    except DeploymentLabUnavailable as exc:
        print(f"DEPLOYMENT_LAB_UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(observations, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
