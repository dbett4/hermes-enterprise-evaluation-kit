"""Fail-closed tests for owner spend-authorization file handling."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTH_DIR = ROOT / "spend-authorization"
RUNNER = ROOT / "scripts/run_live_mission_hermes_user.sh"


def _run(auth_file: Path, cap: str = "1.00") -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["SPEND_AUTHORIZATION_FILE"] = str(auth_file)
    env["SPEND_CAP_USD"] = cap
    env["HERMES_BIN"] = "/bin/true"
    return subprocess.run(
        ["bash", str(RUNNER)],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _write_auth(path: Path, *, cap: str = "1.00", mode: int = 0o600) -> None:
    path.write_text(
        "\n".join(
            [
                "GATE_ID=live-run-spend-cap",
                f"AUTHORIZED_CAP_USD={cap}",
                "AUTHORIZED_BY=test-harness",
                "AUTHORIZED_AT=2026-08-11T00:00:00Z",
                'SCOPE="one S1 live mission single one-shot"',
                "",
            ]
        ),
        encoding="utf-8",
    )
    path.chmod(mode)


def test_shipped_example_cannot_authorize_spend() -> None:
    proc = _run(AUTH_DIR / "live-s1-spend-gate.example")

    assert proc.returncode == 3
    assert "real *.authorization file" in proc.stderr
    assert "SPEND_GATE_PASS" not in proc.stdout


def test_symlink_cannot_authorize_spend(tmp_path: Path) -> None:
    target = tmp_path / "owner.authorization"
    _write_auth(target)
    link = AUTH_DIR / ".test-symlink.authorization"
    link.symlink_to(target)
    try:
        proc = _run(link)
        assert proc.returncode == 3
        assert "must not be a symlink" in proc.stderr
        assert "SPEND_GATE_PASS" not in proc.stdout
    finally:
        link.unlink(missing_ok=True)


def test_permissive_file_mode_cannot_authorize_spend() -> None:
    auth = AUTH_DIR / ".test-permissions.authorization"
    _write_auth(auth, mode=0o644)
    try:
        proc = _run(auth)
        assert proc.returncode == 3
        assert "permissions must be 400 or 600" in proc.stderr
        assert "SPEND_GATE_PASS" not in proc.stdout
    finally:
        auth.unlink(missing_ok=True)


def test_invalid_currency_precision_cannot_authorize_spend() -> None:
    auth = AUTH_DIR / ".test-cap.authorization"
    _write_auth(auth, cap="0.001")
    try:
        proc = _run(auth, cap="0.001")
        assert proc.returncode == 3
        assert "positive USD amount with at most two decimals" in proc.stderr
        assert "SPEND_GATE_PASS" not in proc.stdout
    finally:
        auth.unlink(missing_ok=True)
