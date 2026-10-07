#!/usr/bin/env python3
"""Deterministic contribution gates; agent assertions never replace measurements."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET

PACKAGE = Path(__file__).resolve().parent
REPO_ARTIFACTS = PACKAGE.parent / "artifacts"
ROOT = Path("/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/threadx-contributions/744")
SOURCE = ROOT / "source"
EVIDENCE = ROOT / "evidence"
IMAGE = "threadx-contribution-checks:744"
UPSTREAM = "eclipse-threadx/threadx"
MODEL = "gpt-6.1-sol"
EFFORT = "high"
FOCUSED = "test/tx/cmake/thread_stack_alignment"
REQUIRED = ["eclipsefdn/eca", "tx / run_tests", "smp / run_tests", "freertos / run_tests", "riscv / run_tests"]


def write(name, value):
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    p = EVIDENCE / name
    p.write_text(json.dumps(value, indent=2) + "\n")
    return value


def read(name):
    return json.loads((EVIDENCE / name).read_text())


def run(argv, cwd=SOURCE, timeout=120, check=True, log=None, env=None):
    started = time.time()
    if log:
        p = EVIDENCE / log
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w") as stream:
            stream.write("COMMAND " + json.dumps(argv) + "\n")
            stream.flush()
            result = subprocess.run(argv, cwd=cwd, env=env, stdout=stream,
                                    stderr=subprocess.STDOUT, timeout=timeout)
        record = {"argv": argv, "cwd": str(cwd), "exit_code": result.returncode,
                  "seconds": round(time.time() - started, 2), "log": log}
        write(log + ".json", record)
        if check and result.returncode:
            raise RuntimeError(f"Command failed ({result.returncode}); see {p}")
        return record
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(f"Command failed: {argv[:3]}: {result.stderr.decode(errors='replace')[-1200:]}")
    return result


def git(*args):
    return run(["git", *args]).stdout.decode().strip()


def gh_json(*args):
    return json.loads(run(["gh", *args]).stdout)


def base():
    return read("admission.json")["base_sha"]


def patch_bytes():
    return run(["git", "diff", "--binary", base(), "--"]).stdout


def patch_hash():
    return hashlib.sha256(patch_bytes()).hexdigest()


def docker(args, directory="/work", timeout=1200, log="command.log", check=True, src=SOURCE):
    return run(["docker", "run", "--rm", "--network", "none", "--user",
                f"{os.getuid()}:{os.getgid()}", "--cap-add", "SYS_NICE",
                "--ulimit", "rtprio=3:3", "-v", f"{src}:/work",
                "-v", f"{EVIDENCE}:/evidence", "-w", directory, IMAGE, *args],
               timeout=timeout, log=log, check=check)


def admit():
    if run(["findmnt", "-rn", "-S", "/dev/loop4", "-o", "TARGET"]).stdout.decode().strip() != str(ROOT.parents[1]):
        raise RuntimeError("Requested loop4 filesystem is not mounted at the configured storage root")
    if git("status", "--porcelain"):
        raise RuntimeError("Admission requires an isolated clean upstream checkout")
    issue = gh_json("issue", "view", "744", "--repo", UPSTREAM, "--json", "number,title,body,comments,state,assignees,url")
    if issue["state"] != "OPEN":
        raise RuntimeError("Issue #744 is no longer open; re-assess before implementation")
    git("fetch", "origin", "dev")
    sha = git("rev-parse", "HEAD")
    if sha != git("rev-parse", "origin/dev"):
        raise RuntimeError("Admission checkout must match the freshly fetched dev branch")
    contributor = gh_json("api", "user")
    write("issue.json", issue)
    rules = gh_json("api", f"repos/{UPSTREAM}/rules/branches/dev")
    write("upstream-rules.json", rules)
    required = [s["context"] for r in rules if r["type"] == "required_status_checks"
                for s in r["parameters"]["required_status_checks"]]
    dependencies = {}
    for number in [741, 742, 532]:
        kind = "pulls" if number == 742 else "issues"
        item = gh_json("api", f"repos/{UPSTREAM}/{kind}/{number}")
        dependencies[str(number)] = {k: item.get(k) for k in ["number", "state", "title", "html_url", "merged_at", "merge_commit_sha"]}
    write("dependencies.json", dependencies)
    guide = (SOURCE / "CONTRIBUTING.md").read_text()
    (EVIDENCE / "CONTRIBUTING.md").write_text(guide)
    (EVIDENCE / "PR-template.md").write_text((SOURCE / ".github/PULL_REQUEST_TEMPLATE.md").read_text())
    write("agent-settings.json", {"backend": "Codex CLI", "model": MODEL,
          "reasoning_effort": EFFORT, "fallbacks": [],
          "probe": "model-probe.jsonl", "human_review": "pending"})
    write("admission.json", {"base_sha": sha, "branch": git("branch", "--show-current"),
          "base_branch": "dev", "upstream": UPSTREAM,
          "author_login": contributor["login"], "author_name": contributor["name"],
          "author_email": git("config", "user.email"), "required_checks": required,
          "guide_sha256": hashlib.sha256(guide.encode()).hexdigest(),
          "coordination": "Issue is assigned; no issue comment sent by this workflow",
          "legal": "ECA must be confirmed by the external final-head check",
          "status": "admitted"})
    print("Admitted", sha, "required checks:", required)


def agent(role):
    roles = ["planner", "implement", "technical-review", "process-review", "repair", "pr-writer"]
    if role not in roles:
        raise RuntimeError("Unknown agent role")
    counts_path = EVIDENCE / "agent-visits.json"
    counts = json.loads(counts_path.read_text()) if counts_path.exists() else {}
    counts[role] = counts.get(role, 0) + 1
    write("agent-visits.json", counts)
    number = counts[role]
    prompt = (PACKAGE / "prompts" / (role + ".md")).read_text()
    values = {"issue_number": "744", "source_dir": str(SOURCE), "evidence_dir": str(EVIDENCE),
              "artifacts_dir": str(REPO_ARTIFACTS)}
    for key, value in values.items():
        prompt = prompt.replace("{{ inputs." + key + " }}", value)
    readonly = role in ["technical-review", "process-review"]
    if readonly:
        prompt += "\nYou run read-only. Return the review JSON as your final response; the driver will save it. Do not try to write review files.\n"
    if role in ["implement", "repair"]:
        prompt += f"\nDeterministic verification contract: add a standalone CMake/CTest regression under {FOCUSED}. It must configure directly with cmake -S {FOCUSED} -B /evidence/build/focused -G Ninja -DCMAKE_C_COMPILER=gcc-14. Compile and execute actual common/src/tx_thread_create.c with real Linux header widths on x86_64 and both TX_MISRA_ENABLE and TX_ENABLE_STACK_CHECKING; the port boundary may use recording stubs following native thread_transition tests. Avoid starting scheduler threads on the old invalid pointer: fail safely on concrete pointer/stack metadata assertions. Test every alignment offset and guard boundaries. Add it to upstream host CTest discovery so CI actually executes a native64 target despite parent -m32 flags. Keep normal native32 coverage. No production edits except common/src/tx_thread_create.c. New-file AI header must name Codex (gpt-6.1-sol), and honestly state that human provenance review is pending; never assert completed human review. Scope may include explicit MISRA deviation comment naming applicable rule. Read design at {PACKAGE.parent / 'regression-design.md'}.\n"
    logdir = EVIDENCE / "agents"
    logdir.mkdir(exist_ok=True)
    stem = f"{role}-{number}"
    final = logdir / (stem + ".txt")
    argv = ["codex", "exec", "--ignore-user-config", "--ephemeral", "--model", MODEL,
            "-c", 'model_reasoning_effort="high"', "-c", 'approval_policy="never"',
            "--sandbox", "read-only" if readonly else "workspace-write", "--cd", str(SOURCE),
            "--json", "-o", str(final)]
    if not readonly:
        argv += ["--add-dir", str(EVIDENCE)]
    if readonly:
        schema = {"type": "object", "additionalProperties": False,
                  "required": ["patch_sha256", "verdict", "findings", "readiness_blockers"],
                  "properties": {"patch_sha256": {"type": "string"},
                    "verdict": {"type": "string", "enum": ["pass", "fail"]},
                    "findings": {"type": "array", "items": {"type": "object", "additionalProperties": False,
                      "required": ["severity", "message", "evidence"],
                      "properties": {k: {"type": "string"} for k in ["severity", "message", "evidence"]}}},
                    "readiness_blockers": {"type": "array", "items": {"type": "string"}}}}
        schema_path = logdir / (stem + ".schema.json")
        schema_path.write_text(json.dumps(schema))
        argv += ["--output-schema", str(schema_path)]
    argv.append("-")
    env = os.environ.copy()
    env["TMPDIR"] = str(EVIDENCE / "tmp")
    Path(env["TMPDIR"]).mkdir(exist_ok=True)
    before = patch_hash() if readonly else None
    with (logdir / (stem + ".jsonl")).open("w") as out, (logdir / (stem + ".stderr")).open("w") as err:
        result = subprocess.run(argv, input=prompt, text=True, stdout=out, stderr=err,
                                env=env, timeout=1200)
    write("agents/" + stem + ".invocation.json", {"role": role, "argv": argv,
          "model": MODEL, "reasoning_effort": EFFORT, "exit_code": result.returncode})
    if result.returncode:
        raise RuntimeError(f"Codex {role} failed; inspect {stem} logs")
    if readonly:
        if before != patch_hash():
            raise RuntimeError("Read-only reviewer changed the frozen source")
        write(role + ".json", json.loads(final.read_text()))
    print("Completed Codex role", role, "visit", number)


def freeze():
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    for path in untracked:
        if not path.startswith(FOCUSED + "/"):
            raise RuntimeError("Unexpected untracked source: " + path)
        git("add", "-N", "--", path)
    paths = git("diff", "--name-only", base()).splitlines()
    allowed = {"common/src/tx_thread_create.c", "test/tx/cmake/CMakeLists.txt"}
    if "common/src/tx_thread_create.c" not in paths:
        raise RuntimeError("Expected production fix is absent")
    if not (SOURCE / FOCUSED / "CMakeLists.txt").exists():
        raise RuntimeError("Expected native-width regression is absent")
    if any(p not in allowed and not p.startswith(FOCUSED + "/") for p in paths):
        raise RuntimeError("Patch escaped the reviewed #744 scope")
    git("diff", "--check", base())
    data = patch_bytes()
    (EVIDENCE / "contribution.patch").write_bytes(data)
    write("freeze.json", {"patch_sha256": hashlib.sha256(data).hexdigest(),
          "base_sha": base(), "head_sha": git("rev-parse", "HEAD"), "files": paths,
          "frozen_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
    print("Frozen", patch_hash())


def verify():
    frozen = read("freeze.json")
    if frozen["patch_sha256"] != patch_hash():
        raise RuntimeError("Verification input differs from frozen patch")
    result = {"status": "fail", "patch_sha256": patch_hash(), "checks": [], "limitations": []}
    write("verification.json", result)
    docker(["gcc-14", "--version"], log="verification/toolchain.log")
    result["image_id"] = run(["docker", "image", "inspect", IMAGE, "--format", "{{.Id}}"], cwd=PACKAGE).stdout.decode().strip()
    baseline = ROOT / "baseline"
    if not baseline.exists():
        run(["git", "worktree", "add", "--detach", str(baseline), base()])
    test_source = SOURCE / FOCUSED
    test_baseline = baseline / FOCUSED
    if test_baseline.exists():
        shutil.rmtree(test_baseline)
    shutil.copytree(test_source, test_baseline, ignore=shutil.ignore_patterns("build*", "*.gcda", "*.gcno"))
    # Build both trees with the identical candidate regression. Only production differs.
    for name, tree in [("baseline", baseline), ("focused", SOURCE)]:
        build_dir = f"/evidence/build/{name}"
        docker(["cmake", "-S", FOCUSED, "-B", build_dir, "-G", "Ninja",
                "-DCMAKE_C_COMPILER=gcc-14", "-DCMAKE_BUILD_TYPE=Debug"],
               src=tree, log=f"verification/{name}-configure.log")
        docker(["cmake", "--build", build_dir, "--parallel", "4"],
               src=tree, log=f"verification/{name}-build.log")
        measured = docker(["ctest", "--test-dir", build_dir, "--output-on-failure",
                 "--no-tests=error", "--timeout", "30", "--output-junit", f"/evidence/verification/{name}.xml"],
                 src=tree, log=f"verification/{name}-test.log", check=False)
        report = ET.parse(EVIDENCE / "verification" / (name + ".xml")).getroot()
        if not report.findall("testcase"):
            raise RuntimeError("Focused regression did not execute any test")
        if name == "baseline" and measured["exit_code"] == 0:
            raise RuntimeError("Regression also passes on old production code")
        if name == "baseline" and not any(t.find("failure") is not None for t in report.findall("testcase")):
            raise RuntimeError("Baseline did not record a behavioral assertion failure")
        if name == "focused" and measured["exit_code"] != 0:
            raise RuntimeError("Patched behavioral regression failed")
        result["checks"].append({"name": name, "status": "expected-failure" if name == "baseline" else "pass", **measured})
        write("verification.json", result)
    # Serialize suites and gcovr. Never hide a first failure with until-pass retries.
    for suite, directory in [("tx", "test/tx/cmake"), ("smp", "test/smp/cmake"), ("freertos", "utility/rtos_compatibility_layers/FreeRTOS")]:
        coverage = "ON" if suite in ["tx", "smp"] else "OFF"
        build = docker(["env", "TX_COVERAGE=" + coverage, "CTEST_REPEAT_FAIL=1", "CTEST_TIMEOUT=120",
                        "bash", f"scripts/build_{suite}.sh"], timeout=1800,
                       log=f"verification/{suite}-build.log")
        tests = docker(["env", "TX_COVERAGE=" + coverage, "CTEST_REPEAT_FAIL=1", "CTEST_TIMEOUT=120",
                        "bash", f"scripts/test_{suite}.sh"], timeout=2400,
                       log=f"verification/{suite}-test.log")
        result["checks"].append({"name": suite, "status": "pass", "build": build, "test": tests})
        if suite in ["tx", "smp"]:
            report = ET.parse(SOURCE / directory / "coverage_report/merged.xml").getroot()
            line_rate = float(report.attrib["line-rate"])
            lines = int(report.attrib["lines-valid"])
            if lines == 0 or line_rate < 0.99:
                raise RuntimeError(f"{suite} coverage gate failed or report empty")
            result["checks"][-1]["coverage"] = {"line_rate": line_rate, "lines_valid": lines,
                                                   "branch_rate": report.attrib.get("branch-rate")}
        write("verification.json", result)
    for name, args in [("ai-disclosure", ["bash", "scripts/check_ai_disclosure.sh"]),
                       ("port-consistency", ["bash", "scripts/check_ports.sh"])]:
        measured = docker(args, timeout=600, log="verification/" + name + ".log")
        result["checks"].append({"name": name, "status": "pass", **measured})
    git("diff", "--check", base())
    if patch_hash() != frozen["patch_sha256"]:
        raise RuntimeError("Source changed while deterministic verification ran")
    result["status"] = "pass"
    result["limitations"] = ["RISC-V, Arm GCC/clang, Cortex-M and FVP are verified by upstream PR CI; not claimed locally",
                              "Hardware execution is not claimed", "Human contributor provenance review is pending"]
    write("verification.json", result)
    print("Measured verification passed for", result["patch_sha256"])


def review_gate():
    frozen = read("freeze.json")
    verification = read("verification.json")
    if patch_hash() != frozen["patch_sha256"] or verification["patch_sha256"] != patch_hash() or verification["status"] != "pass":
        raise RuntimeError("Frozen verification evidence is absent or stale")
    for name in ["technical-review.json", "process-review.json"]:
        review = read(name)
        if review["patch_sha256"] != patch_hash() or review["verdict"] != "pass":
            raise RuntimeError("Independent review rejected current patch: " + name)
        if any(f["severity"].lower() in ["blocking", "critical", "high"] for f in review["findings"]):
            raise RuntimeError("Unresolved blocking review finding: " + name)
    write("review-gate.json", {"status": "pass", "patch_sha256": patch_hash(),
                                "human_provenance_review": "pending"})
    print("Independent review gates passed")


def publish():
    review_gate()
    title = (EVIDENCE / "pr-title.txt").read_text().strip()
    if len(title) > 72 or not title.startswith(("Fixed ", "Preserved ", "Corrected ")):
        raise RuntimeError("PR title must be a past-tense statement within 72 characters")
    body = (EVIDENCE / "pr-body.md").read_text()
    if "744" not in body or "gpt-6.1-sol" not in body or "pending" not in body.lower():
        raise RuntimeError("PR body must reference issue, actual model, and pending human review")
    admission = read("admission.json")
    git("config", "user.name", admission["author_name"] or admission["author_login"])
    git("add", "--", *read("freeze.json")["files"])
    message = "Fixed MISRA stack alignment on ports with 64-bit pointers\n\n" + \
              "MISRA stack checking converted the stack address through 32-bit ULONG.\n\n" + \
              "Preserved ALIGN_TYPE width in both stack-alignment conversions. Added a\n" + \
              "native-width behavioral regression that fails on the original code.\n\n" + \
              "The frozen patch passed recorded focused and host regression checks.\n" + \
              "Human contributor provenance review remains pending on this draft.\n\n" + \
              "Fixes: eclipse-threadx/threadx#744\n" + \
              "Assisted-by: Codex (gpt-6.1-sol) <noreply@openai.com>\n"
    (EVIDENCE / "commit-message.txt").write_text(message)
    git("commit", "-F", str(EVIDENCE / "commit-message.txt"))
    if patch_hash() != read("freeze.json")["patch_sha256"]:
        raise RuntimeError("Commit differs from independently reviewed patch")
    run(["gh", "repo", "fork", UPSTREAM, "--clone=false", "--remote=false"], timeout=120,
        log="publication/fork.log")
    fork = admission["author_login"] + "/threadx"
    run(["git", "push", "https://github.com/" + fork + ".git", "HEAD:refs/heads/" + admission["branch"]],
        timeout=120, log="publication/push.log")
    created = run(["gh", "pr", "create", "--repo", UPSTREAM, "--base", "dev", "--head",
                   admission["author_login"] + ":" + admission["branch"], "--draft", "--title", title,
                   "--body-file", str(EVIDENCE / "pr-body.md")], timeout=120)
    url = created.stdout.decode().strip()
    write("publication.json", {"url": url, "head_sha": git("rev-parse", "HEAD"),
          "patch_sha256": patch_hash(), "draft": True, "human_provenance_review": "pending"})
    print(url)


def monitor():
    publication = read("publication.json")
    fields = "number,url,isDraft,headRefOid,baseRefName,reviewDecision,mergeStateStatus,mergeable,statusCheckRollup,reviews"
    for attempt in range(60):
        pr = gh_json("pr", "view", publication["url"], "--json", fields)
        write("pr-status.json", pr)
        if pr["headRefOid"] != publication["head_sha"]:
            raise RuntimeError("PR head differs from the reviewed publication")
        checks = pr["statusCheckRollup"] or []
        if checks and all(c.get("status", "COMPLETED") == "COMPLETED" and c.get("state") != "PENDING" for c in checks):
            break
        time.sleep(15)
    required = read("admission.json")["required_checks"]
    passed = {c.get("name", c.get("context")): c.get("conclusion", c.get("state")) for c in checks}
    blockers = []
    for name in required:
        if passed.get(name) not in ["SUCCESS", "NEUTRAL"]:
            blockers.append("Required check not passing: " + name)
    for c in checks:
        if c.get("conclusion") in ["FAILURE", "CANCELLED", "TIMED_OUT", "ACTION_REQUIRED"] or c.get("state") in ["FAILURE", "ERROR"]:
            blockers.append("Applicable check failed or needs action: " + c.get("name", c.get("context", "unknown")))
    if pr["isDraft"]:
        blockers.append("Draft awaits human contributor provenance review")
    if pr["reviewDecision"] != "APPROVED":
        blockers.append("Required upstream human/code-owner approval is pending")
    if pr["baseRefName"] != "dev" or pr["mergeable"] != "MERGEABLE":
        blockers.append("GitHub mergeability/base branch gate is not satisfied")
    write("readiness.json", {"status": "ready" if not blockers else "blocked", "blockers": blockers,
          "head_sha": pr["headRefOid"], "url": pr["url"], "checked_at": time.time()})
    print("PR readiness:", "ready" if not blockers else "blocked", blockers)


def export():
    REPO_ARTIFACTS.mkdir(exist_ok=True, parents=True)
    names = ["admission.json", "issue.json", "dependencies.json", "agent-settings.json", "freeze.json",
             "contribution.patch", "verification.json", "technical-review.json", "process-review.json",
             "review-gate.json", "pr-title.txt", "pr-body.md", "commit-message.txt", "publication.json",
             "pr-status.json", "readiness.json", "last-error.json", "upstream-rules.json"]
    for name in names:
        if (EVIDENCE / name).exists():
            shutil.copy2(EVIDENCE / name, REPO_ARTIFACTS / name)
    logs = EVIDENCE / "verification"
    if logs.exists():
        shutil.copytree(logs, REPO_ARTIFACTS / "verification", dirs_exist_ok=True)
    manifest = []
    for path in sorted(REPO_ARTIFACTS.rglob("*")):
        if path.is_file() and path.name != "manifest.json":
            manifest.append({"path": str(path.relative_to(REPO_ARTIFACTS)), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "bytes": path.stat().st_size})
    (REPO_ARTIFACTS / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    readiness = read("readiness.json") if (EVIDENCE / "readiness.json").exists() else {"status": "incomplete", "blockers": ["No final PR readiness assessment"]}
    print("Exported contribution artifacts:", REPO_ARTIFACTS)
    if readiness["status"] != "ready":
        raise RuntimeError("Artifacts exported; contribution is not yet ready to merge: " + json.dumps(readiness["blockers"]))


if __name__ == "__main__":
    actions = {"admit": admit, "freeze": freeze, "verify": verify, "review-gate": review_gate,
               "publish": publish, "monitor": monitor, "export": export}
    try:
        if sys.argv[1] == "agent":
            agent(sys.argv[2])
        else:
            actions[sys.argv[1]]()
    except Exception as error:
        write("last-error.json", {"action": sys.argv[1:], "error": str(error), "at": time.time()})
        print(str(error), file=sys.stderr)
        sys.exit(1)
