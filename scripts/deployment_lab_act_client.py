#!/usr/bin/env python3
"""MCP client that drives the deployment lab's real tools for the S3 Act mission.

This file belongs to the Evaluation Kit but runs under the deployment lab's
interpreter (it needs ``fastmcp`` and ``httpx``), with ``PYTHONPATH`` pointing at
the lab's ``enterprise-mcp`` and ``workflow-runner`` packages. See
``scripts/deployment_lab_backend.py``, which resolves the lab, boots its
``enterprise-api``, and executes this module.

Every mutation below crosses an MCP stdio boundary into a freshly spawned
``enterprise_mcp.server`` process. Nothing here re-implements approval,
idempotency, or resume: those live in the lab and are exercised, not imitated.

Observed sequence:

    1. read/plan allowlist  -> the mutating tool is not on the wire at all
    2. write allowlist      -> propose_incident_plan returns an approval-gated plan
    3. apply, no capability -> pending_approval, no secret, zero side effects
    4. operator command     -> separate process grants an expiring capability
    5. apply + injected 500 -> the API commits and then fails (the awkward case)
    6. resume               -> same capability replays instead of re-applying
    7. readback             -> exactly one record; a third use is refused

Prints one JSON object of observations on stdout. Diagnostics go to stderr.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import httpx
from fastmcp import Client
from fastmcp.client.transports import StdioTransport

READ_PLAN_TOOLS = "check_enterprise_api,get_incident_context,propose_incident_plan"
ALL_TOOLS = "all"


class ActBridgeFailure(RuntimeError):
    """The lab did not behave the way the Act mission claims it behaves."""


def server_env(
    *,
    lab_root: Path,
    api_url: str,
    read_token: str,
    write_token: str | None,
    enabled_tools: str,
    audit_path: Path,
    approval_path: Path,
    run_id: str,
    inject: str | None = None,
) -> dict[str, str]:
    """Full environment for the MCP subprocess.

    MCP stdio does not inherit the parent environment; the SDK forwards only
    HOME, LOGNAME, PATH, SHELL, USER. Everything the lab server needs is passed
    explicitly here.
    """
    env = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": os.environ.get("HOME", ""),
        "PYTHONPATH": f"{lab_root / 'enterprise-mcp'}:{lab_root / 'workflow-runner'}",
        "PYTHONUNBUFFERED": "1",
        "FASTMCP_LOG_LEVEL": "WARNING",
        "ENTERPRISE_API_URL": api_url,
        "ENTERPRISE_API_TOKEN": read_token,
        "ENTERPRISE_API_TIMEOUT_SECONDS": "10",
        "ENTERPRISE_MCP_ENABLED_TOOLS": enabled_tools,
        "AUDIT_LOG_PATH": str(audit_path),
        "APPROVAL_STORE_PATH": str(approval_path),
        "AUDIT_RUN_ID": run_id,
    }
    if write_token:
        env["ENTERPRISE_API_WRITE_TOKEN"] = write_token
    if inject:
        env["ENTERPRISE_INJECT_FAILURE"] = inject
    return env


@asynccontextmanager
async def session(lab_root: Path, env: dict[str, str]):
    transport = StdioTransport(
        command=sys.executable,
        args=["-m", "enterprise_mcp.server"],
        env=env,
        cwd=str(lab_root),
    )
    async with Client(transport) as client:
        yield client


def unwrap(result: Any) -> dict[str, Any]:
    data = getattr(result, "data", None)
    return data if isinstance(data, dict) else {"raw": str(result)}


def operator_approve(
    *,
    lab_root: Path,
    approval_id: str,
    approver: str,
    audit_path: Path,
    approval_path: Path,
    run_id: str,
) -> str:
    """Grant through the lab's separate operator command, not through MCP."""
    env = os.environ.copy()
    env.update(
        {
            "PYTHONPATH": str(lab_root / "workflow-runner"),
            "APPROVAL_STORE_PATH": str(approval_path),
            "AUDIT_LOG_PATH": str(audit_path),
            "AUDIT_RUN_ID": run_id,
        }
    )
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "workflow_runner.approval_operator",
            "approve",
            approval_id,
            "--approver",
            approver,
        ],
        cwd=str(lab_root),
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ActBridgeFailure(
            f"operator approval failed ({completed.returncode}): {completed.stderr or completed.stdout}"
        )
    payload = json.loads(completed.stdout)
    if payload.get("status") != "approved":
        raise ActBridgeFailure(f"operator approval was not granted: {payload}")
    return str(payload["approval_capability"])


async def run_act(
    *,
    lab_root: Path,
    api_url: str,
    read_token: str,
    write_token: str,
    audit_path: Path,
    approval_path: Path,
    run_id: str,
    incident_id: str,
    action_id: str,
    approver: str,
) -> dict[str, Any]:
    read_headers = {"Authorization": f"Bearer {read_token}"}
    write_headers = {"Authorization": f"Bearer {write_token}"}

    def store_count() -> int:
        response = httpx.get(
            f"{api_url}/v1/incidents/{incident_id}/actions", headers=read_headers, timeout=10
        )
        response.raise_for_status()
        return int(response.json()["count"])

    # Deterministic prestate.
    reset = httpx.post(f"{api_url}/v1/admin/reset-actions", headers=write_headers, timeout=10)
    reset.raise_for_status()

    base = dict(
        lab_root=lab_root,
        api_url=api_url,
        read_token=read_token,
        write_token=write_token,
        audit_path=audit_path,
        approval_path=approval_path,
        run_id=run_id,
    )

    # 1. Scoped surface: the mutating tool is not registered at all.
    async with session(lab_root, server_env(enabled_tools=READ_PLAN_TOOLS, **base)) as client:
        read_plan_tools = sorted(tool.name for tool in await client.list_tools())
    if "apply_incident_plan" in read_plan_tools:
        raise ActBridgeFailure("read/plan allowlist exposed the mutating tool")

    write_env = server_env(enabled_tools=ALL_TOOLS, **base)
    prestate_count = store_count()

    # 2-3. Plan, then request a mutation without a capability.
    async with session(lab_root, write_env) as client:
        write_tools = sorted(tool.name for tool in await client.list_tools())
        if "apply_incident_plan" not in write_tools:
            raise ActBridgeFailure("write allowlist did not expose the mutating tool")
        plan = unwrap(await client.call_tool("propose_incident_plan", {"incident_id": incident_id}))
        approval_required_actions = [
            action["action_id"]
            for action in plan.get("proposed_actions", [])
            if action.get("approval_required")
        ]
        pending = unwrap(
            await client.call_tool(
                "apply_incident_plan", {"incident_id": incident_id, "action_id": action_id}
            )
        )
    requested_count = store_count()
    if pending.get("status") != "pending_approval":
        raise ActBridgeFailure(f"expected pending_approval, got {pending.get('status')}")
    if requested_count != prestate_count:
        raise ActBridgeFailure("an unapproved request changed the enterprise store")
    capability_leaked = "approval_capability" in pending or "approval_token" in pending
    if capability_leaked:
        raise ActBridgeFailure("the approval request response leaked a capability")
    approval_id = str(pending["approval_id"])

    # 4. Separate operator path.
    capability = operator_approve(
        lab_root=lab_root,
        approval_id=approval_id,
        approver=approver,
        audit_path=audit_path,
        approval_path=approval_path,
        run_id=run_id,
    )

    # 5. Post-commit fault: the API commits, then returns 500.
    fault_env = server_env(enabled_tools=ALL_TOOLS, inject="error_after_commit", **base)
    async with session(lab_root, fault_env) as client:
        failed = unwrap(
            await client.call_tool(
                "apply_incident_plan",
                {
                    "incident_id": incident_id,
                    "action_id": action_id,
                    "approval_capability": capability,
                },
            )
        )
    if failed.get("status") != "error":
        raise ActBridgeFailure(f"expected an error after the injected fault, got {failed}")
    failure_count = store_count()

    # 6. Resume on the same capability.
    async with session(lab_root, write_env) as client:
        resumed = unwrap(
            await client.call_tool(
                "apply_incident_plan",
                {
                    "incident_id": incident_id,
                    "action_id": action_id,
                    "approval_capability": capability,
                },
            )
        )
    if resumed.get("status") != "replayed":
        raise ActBridgeFailure(f"expected replayed, got {resumed.get('status')}")

    # 7. Exactly-once, and the capability is terminal.
    final_count = store_count()
    async with session(lab_root, write_env) as client:
        terminal = unwrap(
            await client.call_tool(
                "apply_incident_plan",
                {
                    "incident_id": incident_id,
                    "action_id": action_id,
                    "approval_capability": capability,
                },
            )
        )
    terminal_count = store_count()

    return {
        "mode": "deployment-lab-mcp-observed",
        "mcp_server": "enterprise_mcp.server",
        "lab_root": str(lab_root),
        "api_url": api_url,
        "incident_id": incident_id,
        "action_id": action_id,
        "tools_under_read_plan_allowlist": read_plan_tools,
        "tools_under_write_allowlist": write_tools,
        "plan_outcome": plan.get("outcome"),
        "approval_required_action_ids": approval_required_actions,
        "approval_id": approval_id,
        "approver": approver,
        "capability_returned_to_requester": capability_leaked,
        "prestate_action_count": prestate_count,
        "post_request_action_count": requested_count,
        "injected_fault": "error_after_commit",
        "failure_status": failed.get("status"),
        "failure_error_code": (failed.get("error") or {}).get("code"),
        "post_failure_action_count": failure_count,
        "resume_status": resumed.get("status"),
        "resume_replayed": bool(resumed.get("replayed")),
        "final_action_count": final_count,
        "terminal_reuse_reason": terminal.get("reason"),
        "post_terminal_action_count": terminal_count,
        "evidence_basis": "observed",
        "staging_service_invoked": True,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab-root", required=True, type=Path)
    parser.add_argument("--api-url", required=True)
    parser.add_argument("--read-token", required=True)
    parser.add_argument("--write-token", required=True)
    parser.add_argument("--audit-log", required=True, type=Path)
    parser.add_argument("--approval-store", required=True, type=Path)
    parser.add_argument("--run-id", default="evaluation-kit-s3-act")
    parser.add_argument("--incident-id", default="INC-2026-0042")
    parser.add_argument("--action-id", default="RB-PAY-GATEWAY-01-S2")
    parser.add_argument("--approver", default="staging-release-owner@example.com")
    args = parser.parse_args(argv)

    args.audit_log.parent.mkdir(parents=True, exist_ok=True)
    args.approval_store.parent.mkdir(parents=True, exist_ok=True)

    try:
        observations = asyncio.run(
            run_act(
                lab_root=args.lab_root.resolve(),
                api_url=args.api_url.rstrip("/"),
                read_token=args.read_token,
                write_token=args.write_token,
                audit_path=args.audit_log,
                approval_path=args.approval_store,
                run_id=args.run_id,
                incident_id=args.incident_id,
                action_id=args.action_id,
                approver=args.approver,
            )
        )
    except ActBridgeFailure as exc:
        print(f"DEPLOYMENT_LAB_ACT_FAILED: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(observations, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
