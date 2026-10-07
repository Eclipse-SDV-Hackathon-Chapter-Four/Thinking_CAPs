"""Remeasure the pinned checker directly; never repair or waive inherited headers."""

import datetime
import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path

from score_sw_fabric.storage import validate_run_root


HERE = Path(__file__).resolve().parent
INFO = json.loads((HERE / "workspace.json").read_text())
ROOT = Path(INFO["run_root"])
WORKSPACE = Path(INFO["workspace"])
OLD = ROOT.parent / "score-communication1167-review-wzlezbhr"
RUNFILES = OLD / "native-workspace/bazel-bin/copyright.check.runfiles"
CHECKER = RUNFILES / "score_tooling+/cr_checker/tool/cr_checker.py"
PYTHON = RUNFILES / "rules_python++python+python_3_12_x86_64-unknown-linux-gnu/bin/python3"
RAPIDFUZZ = RUNFILES / "rules_python++pip+pip_cr_checker_312_rapidfuzz/site-packages"
OUTPUT = HERE / "copyright"
INPUTS = [".github", "BUILD", "MODULE.bazel", "quality", "score", "third_party", "tools"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name, value):
    (OUTPUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def run_check(name, workspace):
    validate_run_root(ROOT)
    env = dict(os.environ, **INFO["environment"], PYTHONDONTWRITEBYTECODE="1",
               PYTHONPATH=str(RAPIDFUZZ), BUILD_WORKSPACE_DIRECTORY=str(workspace))
    args = [str(PYTHON), "-B", str(CHECKER), "-t", "third_party/cr_checker/templates.ini",
            "-c", "third_party/cr_checker/config.json", *INPUTS]
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    result = subprocess.run(args, cwd=workspace, env=env, capture_output=True)
    (OUTPUT / f"{name}.stdout").write_bytes(result.stdout)
    (OUTPUT / f"{name}.stderr").write_bytes(result.stderr)
    text = re.sub(r"\x1b\[[0-9;]*m", "", (result.stdout + result.stderr).decode())
    findings = sorted(line.split("ERROR:", 1)[1].strip().replace(str(workspace) + "/", "")
                      for line in text.splitlines() if "ERROR:" in line)
    write(f"{name}.json", {"started_at_utc": start, "exit_code": result.returncode,
                           "command": args, "cwd": str(workspace), "findings": findings})
    return result.returncode, findings


def main():
    global INFO, ROOT, WORKSPACE, OUTPUT
    parser = argparse.ArgumentParser()
    parser.add_argument("--binding", type=Path, default=HERE)
    options = parser.parse_args()
    binding = options.binding.resolve()
    INFO = json.loads((binding / "workspace.json").read_text())
    ROOT = Path(INFO["run_root"])
    WORKSPACE = Path(INFO["workspace"])
    OUTPUT = binding / "copyright"
    validate_run_root(ROOT)
    OUTPUT.mkdir(exist_ok=True)
    subject = json.loads((binding / "subject.json").read_text())
    for path, expected in subject["source_hashes"].items():
        if sha(WORKSPACE / path) != expected:
            raise ValueError(f"Subject changed: {path}")
    baseline = ROOT / "copyright-base"
    subprocess.run(["git", "-C", str(WORKSPACE), "worktree", "add", "--detach",
                    str(baseline), INFO["pr_base"]], check=True)
    # Native baseline contains the already documented checker input-path defect.
    # Overlay only the two corrected strings to compare findings on equal inputs.
    build = baseline / "BUILD"
    original = build.read_text()
    corrected = original.replace('"//:BUILD",', '"BUILD",').replace(
        '"//:MODULE.bazel",', '"MODULE.bazel",')
    if corrected == original:
        raise ValueError("Expected historical checker-path defect is absent")
    build.write_text(corrected)
    patch = subprocess.check_output(["git", "-C", str(baseline), "diff", "--", "BUILD"])
    (OUTPUT / "baseline-input-path-overlay.patch").write_bytes(patch)
    for control in ["MODULE.bazel", "third_party/cr_checker/config.json",
                    "third_party/cr_checker/templates.ini"]:
        if sha(baseline / control) != sha(WORKSPACE / control):
            raise ValueError(f"Checker controls differ: {control}")
    base_exit, base = run_check("baseline", baseline)
    candidate_exit, candidate = run_check("candidate", WORKSPACE)
    for path, expected in subject["source_hashes"].items():
        if sha(WORKSPACE / path) != expected:
            raise ValueError(f"Checker modified subject: {path}")
    write("comparison.json", {
        "baseline_commit": INFO["pr_base"], "candidate_commit": INFO["pr_merge_commit"],
        "candidate_tree": subject["merge_tree"], "baseline_exit_code": base_exit,
        "candidate_exit_code": candidate_exit, "baseline_count": len(base),
        "candidate_count": len(candidate), "identical_normalized_findings": base == candidate,
        "candidate_only_findings": sorted(set(candidate) - set(base)),
        "baseline_only_findings": sorted(set(base) - set(candidate)),
        "execution_kind": "direct pinned score_tooling 2.3.1 checker with carried Bazel Python/rapidfuzz runtime; not a fresh bazel run",
        "baseline_overlay": "only the two checker input paths in root BUILD",
        "no_source_changes": True, "waiver": False,
        "tool_hashes": {str(path): sha(path) for path in [CHECKER, PYTHON]},
        "control_hashes": {path: sha(WORKSPACE / path) for path in [
            "MODULE.bazel", "third_party/cr_checker/config.json", "third_party/cr_checker/templates.ini"]},
    })
    print(json.dumps({"baseline_count": len(base), "candidate_count": len(candidate),
                      "identical": base == candidate, "exits": [base_exit, candidate_exit]}))


if __name__ == "__main__":
    main()
