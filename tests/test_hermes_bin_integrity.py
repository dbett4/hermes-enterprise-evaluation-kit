"""Regression: spend-gated live path forwards validated HERMES_BIN (no PATH fallback)."""

from __future__ import annotations

import os
import stat
import subprocess
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEND_AUTH_DIR = ROOT / "spend-authorization"


def _write_executable(path: Path, body: str) -> None:
    path.write_text(body, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _auth_file(name: str) -> Path:
    path = SPEND_AUTH_DIR / name
    path.write_text(
        textwrap.dedent(
            """\
            GATE_ID=live-run-spend-cap
            AUTHORIZED_CAP_USD=1.00
            AUTHORIZED_BY=test-harness
            AUTHORIZED_AT=2026-08-11T00:00:00Z
            SCOPE="hermes-bin integrity regression (non-spend)"
            """
        ),
        encoding="utf-8",
    )
    path.chmod(0o600)
    return path


def _fake_python_recorder(bin_dir: Path, record_path: Path) -> None:
    """Intercept python3 so live mission never reaches a provider."""
    fake = bin_dir / "python3"
    _write_executable(
        fake,
        textwrap.dedent(
            f"""\
            #!/usr/bin/env bash
            printf '%s\\n' "$@" > "{record_path}"
            exit 0
            """
        ),
    )


def test_demo_live_forwards_exact_hermes_bin(tmp_path: Path) -> None:
    hermes = tmp_path / "validated-hermes"
    hermes.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hermes.chmod(hermes.stat().st_mode | stat.S_IXUSR)
    record = tmp_path / "argv.txt"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_python_recorder(bin_dir, record)

    env = os.environ.copy()
    env.pop("HERMES_HOME", None)
    env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
    env["HERMES_BIN"] = str(hermes)

    proc = subprocess.run(
        ["bash", str(ROOT / "scripts/demo_mission_s1.sh"), "--live"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr
    argv = record.read_text(encoding="utf-8").splitlines()
    assert argv[0].endswith("scripts/run_mission_s1.py")
    assert "--hermes-binary" in argv
    assert argv[argv.index("--hermes-binary") + 1] == str(hermes)


def test_demo_live_rejects_cli_hermes_binary_when_env_set(tmp_path: Path) -> None:
    hermes = tmp_path / "validated-hermes"
    hermes.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hermes.chmod(hermes.stat().st_mode | stat.S_IXUSR)
    other = tmp_path / "other-hermes"
    other.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    other.chmod(other.stat().st_mode | stat.S_IXUSR)

    env = os.environ.copy()
    env["HERMES_BIN"] = str(hermes)

    proc = subprocess.run(
        [
            "bash",
            str(ROOT / "scripts/demo_mission_s1.sh"),
            "--live",
            "--hermes-binary",
            str(other),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 3
    assert "refusing --hermes-binary while HERMES_BIN is set" in proc.stderr


def test_spend_gate_requires_hermes_bin() -> None:
    auth = _auth_file(".test-hermes-bin-missing.authorization")
    try:
        env = os.environ.copy()
        env.pop("HERMES_BIN", None)
        env["SPEND_AUTHORIZATION_FILE"] = str(auth.relative_to(ROOT))
        env["SPEND_CAP_USD"] = "1.00"

        proc = subprocess.run(
            ["bash", str(ROOT / "scripts/run_live_mission_hermes_user.sh")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 3
        assert "HERMES_BIN is required" in proc.stderr
        assert "SPEND_GATE_PASS" not in proc.stdout
    finally:
        auth.unlink(missing_ok=True)


def test_spend_gate_rejects_invalid_hermes_bin(tmp_path: Path) -> None:
    auth = _auth_file(".test-hermes-bin-invalid.authorization")
    missing = tmp_path / "does-not-exist-hermes"
    try:
        env = os.environ.copy()
        env["HERMES_BIN"] = str(missing)
        env["SPEND_AUTHORIZATION_FILE"] = str(auth.relative_to(ROOT))
        env["SPEND_CAP_USD"] = "1.00"

        proc = subprocess.run(
            ["bash", str(ROOT / "scripts/run_live_mission_hermes_user.sh")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 3
        assert "HERMES_BIN is not an executable file" in proc.stderr
    finally:
        auth.unlink(missing_ok=True)


def test_spend_gate_rejects_non_executable_hermes_bin(tmp_path: Path) -> None:
    auth = _auth_file(".test-hermes-bin-non-executable.authorization")
    non_executable = tmp_path / "non-executable-hermes"
    non_executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    non_executable.chmod(0o600)
    try:
        env = os.environ.copy()
        env["HERMES_BIN"] = str(non_executable)
        env["SPEND_AUTHORIZATION_FILE"] = str(auth.relative_to(ROOT))
        env["SPEND_CAP_USD"] = "1.00"

        proc = subprocess.run(
            ["bash", str(ROOT / "scripts/run_live_mission_hermes_user.sh")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 3
        assert "HERMES_BIN is not an executable file" in proc.stderr
    finally:
        auth.unlink(missing_ok=True)


def test_spend_gate_forwards_exact_hermes_bin(tmp_path: Path) -> None:
    auth = _auth_file(".test-hermes-bin-forward.authorization")
    hermes = tmp_path / "validated-hermes"
    hermes.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hermes.chmod(hermes.stat().st_mode | stat.S_IXUSR)
    record = tmp_path / "argv.txt"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_python_recorder(bin_dir, record)

    try:
        env = os.environ.copy()
        env.pop("HERMES_HOME", None)
        env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
        env["HERMES_BIN"] = str(hermes)
        env["SPEND_AUTHORIZATION_FILE"] = str(auth.relative_to(ROOT))
        env["SPEND_CAP_USD"] = "1.00"

        proc = subprocess.run(
            ["bash", str(ROOT / "scripts/run_live_mission_hermes_user.sh")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        assert "SPEND_GATE_PASS" in proc.stdout
        argv = record.read_text(encoding="utf-8").splitlines()
        assert "--hermes-binary" in argv
        assert argv[argv.index("--hermes-binary") + 1] == str(hermes)
        assert argv.count("--hermes-binary") == 1
    finally:
        auth.unlink(missing_ok=True)


def test_live_proof_blocks_missing_hermes_bin() -> None:
    env = os.environ.copy()
    env["LIVE_PROOF_AUTHORIZED"] = "yes"
    env["SPEND_AUTHORIZATION_FILE"] = "spend-authorization/live-s1-spend-gate.example"
    env["SPEND_CAP_USD"] = "1.00"
    env.pop("HERMES_BIN", None)

    proc = subprocess.run(
        ["bash", str(ROOT / "scripts/live_proof.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 3
    assert "LIVE_PROOF_BLOCKED" in proc.stderr
    assert "HERMES_BIN" in proc.stderr


def test_live_proof_blocks_invalid_hermes_bin(tmp_path: Path) -> None:
    env = os.environ.copy()
    env["LIVE_PROOF_AUTHORIZED"] = "yes"
    env["SPEND_AUTHORIZATION_FILE"] = "spend-authorization/live-s1-spend-gate.example"
    env["SPEND_CAP_USD"] = "1.00"
    env["HERMES_BIN"] = str(tmp_path / "missing-hermes")

    proc = subprocess.run(
        ["bash", str(ROOT / "scripts/live_proof.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 3
    assert "LIVE_PROOF_BLOCKED" in proc.stderr
    assert "not an executable file" in proc.stderr


def test_live_proof_blocks_non_executable_hermes_bin(tmp_path: Path) -> None:
    non_executable = tmp_path / "non-executable-hermes"
    non_executable.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    non_executable.chmod(0o600)
    env = os.environ.copy()
    env["LIVE_PROOF_AUTHORIZED"] = "yes"
    env["SPEND_AUTHORIZATION_FILE"] = "spend-authorization/live-s1-spend-gate.example"
    env["SPEND_CAP_USD"] = "1.00"
    env["HERMES_BIN"] = str(non_executable)

    proc = subprocess.run(
        ["bash", str(ROOT / "scripts/live_proof.sh")],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 3
    assert "LIVE_PROOF_BLOCKED" in proc.stderr
    assert "not an executable file" in proc.stderr


def test_live_proof_chain_forwards_exact_hermes_bin(tmp_path: Path) -> None:
    auth = _auth_file(".test-hermes-bin-live-proof-forward.authorization")
    hermes = tmp_path / "validated-hermes"
    hermes.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    hermes.chmod(hermes.stat().st_mode | stat.S_IXUSR)
    record = tmp_path / "argv.txt"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    _fake_python_recorder(bin_dir, record)

    try:
        env = os.environ.copy()
        env.pop("HERMES_HOME", None)
        env["PATH"] = f"{bin_dir}:{env.get('PATH', '')}"
        env["LIVE_PROOF_AUTHORIZED"] = "yes"
        env["SPEND_AUTHORIZATION_FILE"] = str(auth.relative_to(ROOT))
        env["SPEND_CAP_USD"] = "1.00"
        env["HERMES_BIN"] = str(hermes)

        proc = subprocess.run(
            ["bash", str(ROOT / "scripts/live_proof.sh")],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        assert proc.returncode == 0, proc.stderr
        assert "LIVE_PROOF_ARMED" in proc.stdout
        assert "SPEND_GATE_PASS" in proc.stdout
        argv = record.read_text(encoding="utf-8").splitlines()
        assert "--hermes-binary" in argv
        assert argv[argv.index("--hermes-binary") + 1] == str(hermes)
        assert argv.count("--hermes-binary") == 1
    finally:
        auth.unlink(missing_ok=True)
