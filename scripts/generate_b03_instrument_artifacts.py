#!/usr/bin/env python3
"""Deterministically validate authored B03 fixtures and materialize compiled artifacts."""
import argparse
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parents[1]
KIT = ROOT / "kit" / "instrument"
sys.path.insert(0, str(KIT))
from evaluator import _validate_result, evaluate  # noqa: E402

NAMES = [
    "prohibited_t0", "advisory_first_t1", "eligible_subsequent_t2",
    "material_reversible_t3", "severe_t4", "fixed_read_conventional",
    "ambiguous_bounded_human", "unknown_acceptance_defer_t1",
    "fully_known_no_trigger", "no_trigger_model_uplift",
    "no_trigger_six_uplifts",
]
ARTIFACTS = ("compiled-fixtures.json", "completed-example.json")

def canonical(value):
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def trace_counts(result):
    return {
        "disposition": sum(x.get("evaluation_pass") == "disposition" for x in result["trace"]),
        "proportionality": sum(x.get("evaluation_pass") == "proportionality" for x in result["trace"]),
        "uplift": sum(x.get("evaluation_pass") == "uplift" for x in result["trace"]),
        "output_leaf": sum(x.get("record_type") == "output_leaf" for x in result["trace"]),
        "total": len(result["trace"]),
    }

def authored_cases():
    doc = read_json(KIT / "fixtures.json")
    cases = doc.get("cases")
    if not isinstance(cases, list) or [c.get("id") for c in cases] != NAMES:
        raise ValueError("fixtures.json must contain the exact ordered 11 authored IDs")
    for case in cases:
        if set(case) != {"id", "input", "expected"}:
            raise ValueError(f"fixture {case.get('id')} envelope is not exactly id/input/expected")
        if set(case["expected"]) != {"rule_id", "disposition", "O01_agent_decision", "O05_risk_tier", "O06_control_plan", "O10_unresolved_risk_register", "trace_counts"}:
            raise ValueError(f"fixture {case['id']} expected keys are not the authored seven")
    return cases

def compare_expected(case, result):
    expected = case["expected"]
    actual = {
        "rule_id": result["rule_id"],
        "disposition": result["disposition"],
        "O01_agent_decision": result["outputs"][0]["value"],
        "O05_risk_tier": result["outputs"][4]["value"],
        "O06_control_plan": result["outputs"][5]["value"],
        "O10_unresolved_risk_register": result["outputs"][9]["value"],
        "trace_counts": trace_counts(result),
    }
    if actual != expected:
        raise ValueError(f"authored expectation mismatch for {case['id']}")

def compile_all():
    cases = authored_cases()
    compiled = {}
    sources = {}
    for case in cases:
        result = evaluate(case["input"])
        _validate_result(result, case["input"])
        compare_expected(case, result)
        compiled[case["id"]] = result
        sources[case["id"]] = case["input"]
    blank = read_json(KIT / "blank-intake.json")
    blank_result = evaluate(blank)
    _validate_result(blank_result, blank)
    compiled["blank_unknown"] = blank_result
    sources["blank_unknown"] = blank
    return compiled, sources

def artifact_bytes(compiled):
    return {
        "compiled-fixtures.json": canonical(compiled),
        "completed-example.json": canonical(compiled["eligible_subsequent_t2"]),
    }

def validate_artifact_root(root, sources):
    root = Path(root)
    docs = read_json(root / "compiled-fixtures.json")
    if set(docs) != set(sources) or len(docs) != 12:
        raise ValueError("compiled identity mismatch")
    for key, source in sources.items():
        raw = (root / "compiled-fixtures.json").read_bytes()
        parsed = json.loads(raw)
        if canonical(parsed) != raw:
            raise ValueError("non-canonical compiled fixture bytes")
        _validate_result(parsed[key], source)
    completed = (root / "completed-example.json").read_bytes()
    if completed != canonical(docs["eligible_subsequent_t2"]):
        raise ValueError("completed example mismatch")

def write_root(root, compiled, sources=None):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for name, data in artifact_bytes(compiled).items():
        (root / name).write_bytes(data)
    if sources is not None:
        validate_artifact_root(root, sources)

def check():
    before = {name: (KIT / name).read_bytes() for name in ARTIFACTS}
    fixture_before = (KIT / "fixtures.json").read_bytes()
    compiled, _ = compile_all()
    with tempfile.TemporaryDirectory(prefix="b03-a-") as a, tempfile.TemporaryDirectory(prefix="b03-b-") as b:
        write_root(a, compiled, _)
        write_root(b, compiled, _)
        for name in ARTIFACTS:
            if (Path(a) / name).read_bytes() != (Path(b) / name).read_bytes():
                raise ValueError(f"non-deterministic generation: {name}")
            if (Path(a) / name).read_bytes() != before[name]:
                raise ValueError(f"tracked artifact differs: {name}")
    if (KIT / "fixtures.json").read_bytes() != fixture_before or any((KIT / n).read_bytes() != before[n] for n in ARTIFACTS):
        raise ValueError("--check changed tracked bytes")

def fsync_file(path):
    with open(path, "rb") as handle:
        os.fsync(handle.fileno())

def fsync_dir(path):
    fd = os.open(path, os.O_RDONLY)
    try: os.fsync(fd)
    finally: os.close(fd)

def write():
    compiled, sources = compile_all()
    payload = artifact_bytes(compiled)
    old = {name: (KIT / name).read_bytes() for name in ARTIFACTS}
    stage = Path(tempfile.mkdtemp(prefix="b03-stage-", dir=KIT))
    rollback = Path(tempfile.mkdtemp(prefix="b03-rollback-", dir=KIT))
    replaced = []
    try:
        for name, data in payload.items():
            target = stage / name
            target.write_bytes(data); fsync_file(target)
        write_root(stage, compiled, sources)
        for name in ARTIFACTS: fsync_file(stage / name)
        for name, data in old.items():
            backup = rollback / name; backup.write_bytes(data); fsync_file(backup)
        fsync_dir(stage); fsync_dir(rollback)
        for name in ARTIFACTS:
            os.replace(stage / name, KIT / name); replaced.append(name)
            fsync_file(KIT / name); fsync_dir(KIT)
            if os.environ.get("B03_INJECT_FAILURE") == "AFTER_FIRST_REPLACE" and len(replaced) == 1:
                raise RuntimeError("injected failure AFTER_FIRST_REPLACE")
        for name, data in payload.items():
            if (KIT / name).read_bytes() != data: raise IOError(f"artifact readback mismatch: {name}")
    except Exception:
        for name, data in old.items():
            (rollback / name).write_bytes(data); fsync_file(rollback / name)
        for name in ARTIFACTS:
            os.replace(rollback / name, KIT / name); fsync_file(KIT / name)
        fsync_dir(KIT)
        if any((KIT / name).read_bytes() != data for name, data in old.items()):
            raise IOError("rollback readback mismatch")
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True); shutil.rmtree(rollback, ignore_errors=True)

def main():
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.check:
        check()
    else:
        write()

if __name__ == "__main__":
    main()
