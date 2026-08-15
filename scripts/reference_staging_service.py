#!/usr/bin/env python3
"""FALLBACK Act target: a toy in-memory staging service.

This is the S3 Act target of last resort. The real target is the sister
repository, ``hermes-enterprise-deployment-lab``, whose MCP tools enforce a
scoped tool surface, separated operator approval, an approval-scoped idempotency
key, and recovery from a post-commit failure. Run the Act mission there:

    bash scripts/demo_mission_s3.sh
    python3 scripts/run_reference_suite.py --scenario s3-h --staging-backend deployment-lab

What this file provides instead is a single mutable rate-limit record with
observed readback and an exact rollback. It has **no** approval separation, no
idempotency key, no failure injection, and no resume semantics — a passing run
here is not evidence of any of those properties. Use it only when the deployment
lab is unavailable, or to exercise the change/rollback readback shape alone.

Not production infrastructure — synthetic target only.
"""

from __future__ import annotations

import argparse
import json
import threading
from pathlib import Path
from typing import Any
from wsgiref.simple_server import WSGIServer, make_server
from socketserver import ThreadingMixIn


class ThreadingWSGIServer(ThreadingMixIn, WSGIServer):
    daemon_threads = True

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURE = ROOT / "reference-suite/s3-act/fixtures/initial-state.json"


class RateLimitState:
    def __init__(self, initial: dict[str, Any]) -> None:
        self._lock = threading.Lock()
        self.service_id = initial["service_id"]
        self.environment = initial["environment"]
        self.resource = initial["resource"]
        self.rate_limit = dict(initial["rate_limit"])
        self.revision = 0

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "service_id": self.service_id,
                "environment": self.environment,
                "resource": self.resource,
                "rate_limit": dict(self.rate_limit),
                "revision": self.revision,
            }

    def apply(self, rate_limit: dict[str, Any]) -> dict[str, Any]:
        with self._lock:
            self.rate_limit = {
                "requests_per_minute": int(rate_limit["requests_per_minute"]),
                "burst": int(rate_limit["burst"]),
            }
            self.revision += 1
            return {
                "service_id": self.service_id,
                "environment": self.environment,
                "resource": self.resource,
                "rate_limit": dict(self.rate_limit),
                "revision": self.revision,
            }


STATE: RateLimitState | None = None


def json_response(start_response: Any, status: str, payload: dict[str, Any]) -> list[bytes]:
    body = json.dumps(payload, sort_keys=True).encode("utf-8")
    start_response(status, [("Content-Type", "application/json"), ("Content-Length", str(len(body)))])
    return [body]


def application(environ: dict[str, Any], start_response: Any) -> list[bytes]:
    assert STATE is not None
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "")

    if path == "/health" and method == "GET":
        return json_response(start_response, "200 OK", {"status": "ok", "synthetic": True})

    if path == "/rate-limit" and method == "GET":
        return json_response(start_response, "200 OK", STATE.snapshot())

    if path == "/rate-limit" and method in {"PUT", "POST"}:
        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
            body = environ["wsgi.input"].read(length)
            payload = json.loads(body.decode("utf-8"))
            rate_limit = payload["rate_limit"]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            return json_response(start_response, "400 Bad Request", {"error": "invalid_payload"})
        return json_response(start_response, "200 OK", STATE.apply(rate_limit))

    return json_response(start_response, "404 Not Found", {"error": "not_found", "path": path})


def load_initial(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    global STATE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    args = parser.parse_args()
    STATE = RateLimitState(load_initial(args.fixture))
    server = make_server(args.host, args.port, application, server_class=ThreadingWSGIServer)
    bound_port = server.server_port
    print(
        json.dumps(
            {
                "synthetic_staging_service": True,
                "listen": f"http://{args.host}:{bound_port}",
                "initial": STATE.snapshot(),
            },
            sort_keys=True,
        ),
        flush=True,
    )
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
