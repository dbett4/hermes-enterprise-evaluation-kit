"""Unit tests for Hermes runtime helpers."""

from __future__ import annotations

import os
import stat
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from hermes_runtime import runtime_reported_from_config  # noqa: E402


def _write_fake_hermes(path: Path, responses: dict[str, str]) -> None:
    lines = [
        "#!/usr/bin/env python3",
        "import sys",
        "key = sys.argv[-1] if len(sys.argv) > 1 else ''",
        "responses = " + repr(responses),
        "if sys.argv[1:4] == ['-p', 'decide-vendor-policy', 'config'] and key in responses:",
        "    print(responses[key]); raise SystemExit(0)",
        "raise SystemExit(1)",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_runtime_reported_reads_model_provider_with_provider_default_fallback(
    tmp_path: Path,
) -> None:
    hermes = tmp_path / "hermes"
    _write_fake_hermes(
        hermes,
        {
            "model.default": "anthropic/claude-fable-5",
            "model.provider": "nous",
        },
    )
    assert runtime_reported_from_config(str(hermes), "decide-vendor-policy") == {
        "model": "anthropic/claude-fable-5",
        "provider": "nous",
    }


def test_runtime_reported_falls_back_to_provider_default(tmp_path: Path) -> None:
    hermes = tmp_path / "hermes"
    _write_fake_hermes(
        hermes,
        {
            "model.default": "anthropic/claude-fable-5",
            "provider.default": "nous",
        },
    )
    assert runtime_reported_from_config(str(hermes), "decide-vendor-policy") == {
        "model": "anthropic/claude-fable-5",
        "provider": "nous",
    }


def test_runtime_reported_matches_shipped_profile_config() -> None:
    config = (ROOT / "packs/profiles/profile-decide-vendor-policy/config.yaml").read_text(
        encoding="utf-8"
    )
    assert "provider: nous" in config
    assert "default: anthropic/claude-fable-5" in config


@pytest.mark.skipif(not os.environ.get("HERMES_BIN"), reason="HERMES_BIN not set")
def test_runtime_reported_against_live_profile() -> None:
    hermes_bin = os.environ["HERMES_BIN"]
    profile_name = os.environ.get("HERMES_PROFILE", "decide-vendor-policy")
    runtime = runtime_reported_from_config(hermes_bin, profile_name)
    assert runtime["model"] != "unknown"
    assert runtime["provider"] in {"nous", "unknown"}
