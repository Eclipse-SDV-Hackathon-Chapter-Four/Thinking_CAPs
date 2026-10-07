#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate the ASPICE SWE.1-SWE.6 evidence report for the X-Verse end-to-end demonstration.

Reads the work products in aspice/, renders the PlantUML views (Docker image
plantuml/plantuml), runs the unit suites and the integration checks, evaluates the
qualification records, computes bidirectional traceability and writes:

    aspice/report/aspice-swe-report.html   aspice/report/README.md (GitHub view)
    aspice/report/summary.json             aspice/report/evidence/*.json

Run from the autoverse checkout while the system is up (run_autoverse.py):

    python3 aspice/tools/generate_report.py            # quick: unit suites that run on the host,
                                                       # recorded results for the container suites
    python3 aspice/tools/generate_report.py --full     # also OTA (Maven) and S-CORE / PR #16 (Bazel)

Exits non-zero when a test fails or traceability is incomplete.
"""
import argparse
import glob
import html
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
import ssl
import xml.etree.ElementTree as ET
from pathlib import Path

ASPICE = Path(__file__).resolve().parents[1]
ROOT = ASPICE.parent
REPORT = ASPICE / "report"
EVID = REPORT / "evidence"
DIAGRAMS = ASPICE / "swe2-architecture" / "diagrams"
DEVCONTAINER_LABEL = f"devcontainer.local_folder={(ROOT / 'vecu' / 's-core').resolve()}"
COMPONENTS = ["bridges/carla", "bridges/someip", "bridges/can", "vecu/s-core", "vecu/vcu_zenoh", "vecu/ota",
              "vecu/aaos_cuttlefish"]


def run(cmd, cwd=ROOT, timeout=1800, **kw):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, **kw)


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S")


# ---------------------------------------------------------------- work products

def md_rows(path):
    """Rows of every markdown table in a file, as dicts keyed by the header cells."""
    rows, header = [], None
    for line in Path(path).read_text().splitlines():
        if not line.startswith("|"):
            header = None
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if all(re.fullmatch(r":?-+:?", c) for c in cells):
            continue
        if header is None:
            header = cells
        else:
            rows.append(dict(zip(header, cells)))
    return rows


def ids(text, prefix):
    """IDs with the prefix in order of appearance; ranges like SWR-03..SWR-07 are expanded."""
    out = []
    for token in re.findall(rf"{prefix}-[A-Z0-9]+(?:\.\.{prefix}-[A-Z0-9]+)?", text):
        if ".." in token:
            a, b = token.split("..")
            width = len(a.split("-")[1])
            for n in range(int(a.split("-")[1]), int(b.split("-")[1]) + 1):
                out.append(f"{prefix}-{n:0{width}d}")
        else:
            out.append(token)
    return list(dict.fromkeys(out))


def load_work_products():
    sys_reqs = md_rows(ASPICE / "swe1-requirements/system-requirements.md")
    sw_reqs = md_rows(ASPICE / "swe1-requirements/software-requirements.md")
    unit = md_rows(ASPICE / "swe4-unit-verification/unit-verification.md")
    integ = md_rows(ASPICE / "swe5-integration-test/integration-test.md")
    qual = md_rows(ASPICE / "swe6-qualification-test/qualification-test.md")
    arch = md_rows(ASPICE / "swe2-architecture/architecture.md")
    return {"sys": sys_reqs, "swr": sw_reqs, "unit": unit, "integ": integ, "qual": qual, "arch": arch}


# ---------------------------------------------------------------- diagrams

def render_diagrams():
    sources = sorted(DIAGRAMS.glob("*.puml"))
    if shutil.which("docker"):
        r = run(["docker", "run", "--rm", "-u", f"{os.getuid()}:{os.getgid()}", "-v", f"{DIAGRAMS}:/data",
                 "plantuml/plantuml", "-tsvg", *[f"/data/{s.name}" for s in sources]], timeout=300)
        if r.returncode:
            print("PlantUML rendering failed; using the committed SVGs\n" + r.stdout + r.stderr, file=sys.stderr)
    out = {}
    for s in sources:
        svg = s.with_suffix(".svg")
        out[s.stem] = re.sub(r"<\?xml[^>]*\?>", "", svg.read_text()) if svg.exists() else "<p>(not rendered)</p>"
    return out


# ---------------------------------------------------------------- unit verification

def cached(name):
    p = EVID / f"{name}.json"
    if p.exists():
        data = json.loads(p.read_text())
        data["source"] = f"recorded {data.get('when', '?')}"
        return data
    return {"status": "NOT RUN", "tests": 0, "failures": 0, "detail": "no recorded result; run with --full",
            "source": "none"}


def save(name, data):
    data.setdefault("when", now())
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / f"{name}.json").write_text(json.dumps(data, indent=2) + "\n")
    return data


def ut_launcher():
    r = run([sys.executable, "-m", "unittest", "tests.test_run_autoverse"], timeout=300)
    m = re.search(r"Ran (\d+) tests?", r.stderr)
    tests = int(m.group(1)) if m else 0
    failures = 0 if r.returncode == 0 else len(re.findall(r"^(FAIL|ERROR):", r.stderr, re.M)) or 1
    return save("ut-launcher", {"status": "PASS" if r.returncode == 0 else "FAIL", "tests": tests,
                                "failures": failures, "detail": r.stderr.strip().splitlines()[-1], "source": "run now"})


def ut_someip():
    binary = ROOT / "bridges/someip/zenoh-someip-bridge/build/test_convert"
    if not binary.exists():
        return cached("ut-someip")
    r = run([str(binary)], timeout=120)
    m = re.search(r"checks=(\d+) failures=(\d+)", r.stdout + r.stderr)
    checks, fails = (int(m.group(1)), int(m.group(2))) if m else (0, 1)
    return save("ut-someip", {"status": "PASS" if r.returncode == 0 and fails == 0 else "FAIL", "tests": checks,
                              "failures": fails, "detail": f"checks={checks} failures={fails} (build/test_convert)",
                              "source": "run now"})


def ut_ota():
    src = ROOT / "vecu/ota/backend/java"
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "java"
        shutil.copytree(src, work, ignore=shutil.ignore_patterns("target"))
        r = run(["docker", "run", "--rm", "-v", "ota-m2-cache:/root/.m2", "-v", f"{work}:/src", "-w", "/src",
                 "maven:3.9-eclipse-temurin-21", "mvn", "-B", "-q", "test"], timeout=2400)
        tests = failures = 0
        suites = []
        for f in glob.glob(str(work / "target/surefire-reports/TEST-*.xml")):
            s = ET.parse(f).getroot()
            t, fl = int(s.get("tests", 0)), int(s.get("failures", 0)) + int(s.get("errors", 0))
            tests, failures = tests + t, failures + fl
            suites.append({"suite": s.get("name"), "tests": t, "failures": fl})
        run(["docker", "run", "--rm", "-v", f"{work}:/src", "alpine", "rm", "-rf", "/src/target"], timeout=120)
    ok = r.returncode == 0 and failures == 0 and tests > 0
    return save("ut-ota", {"status": "PASS" if ok else "FAIL", "tests": tests, "failures": failures,
                           "detail": f"{len(suites)} JUnit suites (mvn test)", "suites": suites, "source": "run now"})


def devcontainer():
    cid = run(["docker", "ps", "-aq", "--filter", f"label={DEVCONTAINER_LABEL}"]).stdout.split()
    if not cid:
        return None
    run(["docker", "start", cid[0]])
    return cid[0]


def bazel(cid, workdir, args, name, label):
    r = run(["docker", "exec", "-u", "root", "-w", workdir, cid, "bash", "-lc", f"bazel test {args} 2>&1"],
            timeout=3600)
    out = r.stdout
    targets = re.findall(r"^(//\S+)\s+(?:\(cached\) )?(PASSED|FAILED)", out, re.M)
    failed = len(re.findall(r"FAILED in|FAILED TO BUILD|NO STATUS", out))
    # Count the individual test cases of each target from its test log (gtest / Rust
    # libtest summaries); fall back to the JUnit test.xml of the target.
    cases = case_failures = 0
    for target, _ in targets:
        pkg, tname = target[2:].split(":")
        logs = f"bazel-testlogs/{pkg}/{tname}"
        log = run(["docker", "exec", "-w", workdir, cid, "bash", "-c", f"cat {logs}/test.log"], timeout=120).stdout
        rust = re.findall(r"test result: \w+\. (\d+) passed; (\d+) failed", log)
        gtest_pass = re.findall(r"\[  PASSED  \] (\d+) tests?", log)
        gtest_fail = re.findall(r"\[  FAILED  \] (\d+) tests?", log)
        if rust:
            cases += sum(int(p) + int(f) for p, f in rust)
            case_failures += sum(int(f) for _, f in rust)
        elif gtest_pass or gtest_fail:
            cases += sum(map(int, gtest_pass)) + sum(map(int, gtest_fail))
            case_failures += sum(map(int, gtest_fail))
        else:
            xml = run(["docker", "exec", "-w", workdir, cid, "bash", "-c", f"cat {logs}/test.xml"], timeout=120).stdout
            cases += len(re.findall(r"<testcase ", xml))
            case_failures += len(re.findall(r"<failure", xml))
    tests = cases or len(targets)
    ok = r.returncode == 0 and failed == 0 and case_failures == 0 and targets
    summary = [l.strip() for l in out.splitlines() if re.search(r"Executed \d+ out of", l)]
    return save(name, {"status": "PASS" if ok else "FAIL", "tests": tests, "failures": failed + case_failures,
                       "detail": f"{label}: {len(targets)} target(s), {cases} test cases"
                                 + (f" — {summary[-1]}" if summary else ""),
                       "targets": [f"{t} {s}" for t, s in targets], "source": "run now"})


def unit_results(full):
    res = {"UT-LAUNCHER": ut_launcher(), "UT-SOMEIP": ut_someip()}
    if full:
        res["UT-OTA"] = ut_ota()
        cid = devcontainer()
        if cid:
            res["UT-SCORE"] = bazel(cid, "/workspaces/s-core/cc_s-core", "--nocache_test_results --test_output=errors //score/cruise_control/...",
                                    "ut-score", "bazel test //score/cruise_control/...")
            res["UT-PR16"] = bazel(cid, "/workspaces/s-core/third_party/inc_diagnostics",
                                   "--config=score_diag_x86_64_linux --lockfile_mode=update --nocache_test_results --test_output=errors "
                                   "//score/mw/diag/sovd_adapter:all", "ut-pr16",
                                   "bazel test //score/mw/diag/sovd_adapter:all")
    for key, name in (("UT-OTA", "ut-ota"), ("UT-SCORE", "ut-score"), ("UT-PR16", "ut-pr16")):
        res.setdefault(key, cached(name))
    return res


# ---------------------------------------------------------------- integration + qualification

def integration_results():
    out = EVID / "integration.json"
    r = run([sys.executable, str(ASPICE / "tools/e2e_check.py"), "--out", str(out)], timeout=600)
    if not out.exists():
        return {}, f"not run: {r.stderr.strip()[-200:]}"
    data = json.loads(out.read_text())
    return {c["id"]: c for c in data["cases"]}, f"run now ({data['when']})"


def operator_campaigns():
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen("https://127.0.0.1:9444/api/campaigns", timeout=5, context=ctx) as resp:
            return json.load(resp)
    except OSError:
        return None


def qualification_results():
    res = {}
    logs = sorted(glob.glob(os.path.expanduser("~/.cache/autoverse-runner/supervisor-*.log")))
    started = [l for l in logs if "Supervisor is now running" in Path(l).read_text(errors="ignore")]
    stopped = [l for l in logs if "CARLA (shutdown)" in Path(l).read_text(errors="ignore")]
    res["QTC-01"] = {"status": "PASS" if started and stopped else "NOT RUN",
                     "detail": f"{len(started)} supervised run(s) reached 'Supervisor is now running', "
                               f"{len(stopped)} completed shutdown (~/.cache/autoverse-runner)"}
    witnessed = "witnessed live in the dry run in front of the competition (issue #44)"
    res["QTC-02"] = {"status": "PASS", "detail": "witnessed live in the dry run (cruise engaged before the fault)",
                     "manual": True}
    res["QTC-03"] = {"status": "PASS", "detail": witnessed, "manual": True}
    camps = operator_campaigns()
    if camps is None:
        for q in ("QTC-04", "QTC-05", "QTC-06"):
            res[q] = {"status": "NOT RUN", "detail": "OTA backend not reachable"}
        return res
    EVID.mkdir(parents=True, exist_ok=True)
    (EVID / "ota-campaigns.json").write_text(json.dumps(camps, indent=2) + "\n")

    def last(target, status, needle=None):
        hits = [c for c in camps if c["target"] == target and c["status"] == status
                and (needle is None or any(needle in s.get("detail", "") for s in c["statuses"]))]
        return max(hits, key=lambda c: c["campaignId"]) if hits else None

    cf, pi = last("PC-CUTTLEFISH-01", "success"), last("PI-ANDROID-15", "success")
    off = [c for c in camps if c["status"] == "failed" and any("unreachable" in s.get("detail", "") for s in c["statuses"])]
    for q, c, what in (("QTC-04", cf, "Cuttlefish"), ("QTC-05", pi, "Raspberry Pi")):
        res[q] = {"status": "PASS" if c else "FAIL",
                  "detail": f"campaign #{c['campaignId']} v{c['version']}: "
                            + " → ".join(s["phase"] for s in reversed(c["statuses"])) if c else f"no successful {what} campaign"}
    res["QTC-06"] = {"status": "PASS" if off else "FAIL",
                     "detail": f"campaign #{off[0]['campaignId']} closed failed: {off[0]['statuses'][0]['detail'][:70]}"
                     if off else "no campaign for an unreachable target"}
    return res


# ---------------------------------------------------------------- evaluation

def evaluate(wp, unit, integ, qual):
    cases = {}
    for row in wp["unit"]:
        r = unit.get(row["ID"], {})
        cases[row["ID"]] = {"level": "UT", "title": row["Suite"], "verifies": ids(row["Verifies"], "SWR"),
                            "status": r.get("status", "NOT RUN"), "detail": r.get("detail", ""),
                            "tests": r.get("tests"), "source": r.get("source", "")}
    for row in wp["integ"]:
        r = integ.get(row["ID"], {})
        cases[row["ID"]] = {"level": "IT", "title": row["Test case"], "verifies": ids(row["Verifies"], "SWR"),
                            "status": r.get("status", "NOT RUN"), "detail": r.get("detail", "")}
    for row in wp["qual"]:
        r = qual.get(row["ID"], {})
        cases[row["ID"]] = {"level": "QT", "title": row["Scenario"], "verifies": ids(row["Verifies"], "SWR"),
                            "status": r.get("status", "NOT RUN"), "detail": r.get("detail", ""),
                            "manual": r.get("manual", False)}
    sys_ids = [r["ID"] for r in wp["sys"]]
    issues, swr_status = [], {}
    for r in wp["swr"]:
        sid = r["ID"]
        for parent in ids(r["Derived from"], "SYS"):
            if parent not in sys_ids:
                issues.append(f"{sid} derives from unknown {parent}")
        planned = re.findall(r"(?:UT|ITC|QTC)-[A-Z0-9]+", r["Verified by"])
        actual = [c for c, v in cases.items() if sid in v["verifies"]]
        for c in planned:
            if c not in cases:
                issues.append(f"{sid}: verifying case {c} is not specified")
            elif sid not in cases[c]["verifies"]:
                issues.append(f"{sid}: {c} is listed but does not trace back to it")
        if not actual:
            issues.append(f"{sid} has no verifying test case")
        st = [cases[c]["status"] for c in actual]
        swr_status[sid] = ("FAIL" if "FAIL" in st else "VERIFIED" if st and all(s == "PASS" for s in st)
                           else "PARTIAL" if "PASS" in st else "NOT VERIFIED")
    for s in sys_ids:
        if not any(s in ids(r["Derived from"], "SYS") for r in wp["swr"]):
            issues.append(f"{s} is not refined by any software requirement")
    for c, v in cases.items():
        for sid in v["verifies"]:
            if sid not in swr_status:
                issues.append(f"{c} verifies unknown {sid}")
    return cases, swr_status, issues


# ---------------------------------------------------------------- HTML

def inline(text):
    t = html.escape(text)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{rel(m.group(2))}">{m.group(1)}</a>', t)
    return t


def rel(target):
    return target if target.startswith(("http", "#")) else target


def md_to_html(path):
    """Small markdown subset: headings, paragraphs, lists, tables, inline code/bold/links."""
    out, para, table, lst = [], [], [], []

    def flush():
        nonlocal para, table, lst
        if para:
            out.append(f"<p>{inline(' '.join(para))}</p>")
        if lst:
            out.append("<ul>" + "".join(f"<li>{inline(i)}</li>" for i in lst) + "</ul>")
        if table:
            rows = [r for r in table if not all(re.fullmatch(r":?-+:?", c) for c in r)]
            head, body = rows[0], rows[1:]
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
                       + "</tbody></table>")
        para, table, lst = [], [], []

    for line in Path(path).read_text().splitlines():
        if line.startswith("|"):
            if para or lst:
                flush()
            table.append([c.strip() for c in line.strip().strip("|").split("|")])
        elif line.startswith("#"):
            flush()
            level = min(len(line) - len(line.lstrip("#")) + 1, 5)
            out.append(f"<h{level}>{inline(line.lstrip('#').strip())}</h{level}>")
        elif line.startswith("- "):
            if para or table:
                flush()
            lst.append(line[2:])
        elif line.startswith("  ") and lst:
            lst[-1] += " " + line.strip()
        elif not line.strip():
            flush()
        else:
            if table or lst:
                flush()
            para.append(line.strip())
    flush()
    return "\n".join(out)


def badge(status):
    cls = {"PASS": "pass", "VERIFIED": "pass", "FAIL": "fail", "PARTIAL": "warn"}.get(status, "na")
    return f'<span class="badge {cls}">{html.escape(status)}</span>'


def provenance():
    repos = [("autoverse", ROOT)] + [(c, ROOT / c) for c in COMPONENTS]
    rows = []
    for name, path in repos:
        if not (path / ".git").exists():
            rows.append((name, "—", "not checked out"))
            continue
        head = run(["git", "-C", str(path), "log", "-1", "--format=%h %s"]).stdout.strip()
        branch = run(["git", "-C", str(path), "branch", "--show-current"]).stdout.strip() or "detached"
        dirty = run(["git", "-C", str(path), "-c", "core.fileMode=false", "status", "--porcelain", "--untracked-files=no"]).stdout
        rows.append((name, branch, head + (" (local changes)" if dirty.strip() else "")))
    return rows


CSS = """
body{font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;margin:0;color:#1d2433;background:#f6f7fb}
header{background:#123;color:#fff;padding:24px 40px}header h1{margin:0 0 6px;font-size:24px}header p{margin:0;opacity:.8}
nav{background:#fff;border-bottom:1px solid #dde;padding:10px 40px;position:sticky;top:0}nav a{margin-right:16px;color:#246;text-decoration:none;font-weight:600}
main{padding:24px 40px;max-width:1300px}section{background:#fff;border:1px solid #dde;border-radius:8px;padding:20px 24px;margin:0 0 20px}
h2{margin-top:0;color:#123}h3{color:#246}table{border-collapse:collapse;width:100%;margin:10px 0 16px;font-size:14px}
th,td{border:1px solid #dde;padding:6px 8px;text-align:left;vertical-align:top}th{background:#eef1f7}
code{background:#eef1f7;padding:1px 4px;border-radius:3px;font-size:13px}.cards{display:flex;gap:14px;flex-wrap:wrap}
.card{flex:1;min-width:160px;background:#f6f7fb;border:1px solid #dde;border-radius:8px;padding:14px}.card b{display:block;font-size:26px;color:#123}
.badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:12px;font-weight:700;color:#fff}
.pass{background:#2e7d32}.fail{background:#c62828}.warn{background:#ef6c00}.na{background:#78849a}
figure{margin:12px 0 24px;border:1px solid #dde;border-radius:6px;padding:10px;overflow-x:auto;background:#fff}
figcaption{font-size:13px;color:#556;margin-top:6px}.svg svg{max-width:100%;height:auto}.small{font-size:13px;color:#556}
.issue{color:#c62828}
"""


def render(wp, diagrams, cases, swr_status, issues, unit, integ_note, prov, stamp):
    swr = {r["ID"]: r for r in wp["swr"]}
    n_pass = sum(1 for c in cases.values() if c["status"] == "PASS")
    n_ver = sum(1 for s in swr_status.values() if s == "VERIFIED")
    unit_tests = sum((u.get("tests") or 0) for u in unit.values())
    parts = [f"<header><h1>ASPICE SWE.1–SWE.6 evidence — X-Verse end-to-end demonstration</h1>"
             f"<p>CARLA · virtual vehicle · Zenoh VCU · SOME/IP bridge · S-CORE ECU with DTC over SOVD (PR #16) · "
             f"OTA vECU (certgen, EOL backend, RTCU) · Android targets — generated {stamp}</p></header>",
             '<nav><a href="#summary">Summary</a><a href="#swe1">SWE.1</a><a href="#swe2">SWE.2</a><a href="#swe3">SWE.3</a>'
             '<a href="#swe4">SWE.4</a><a href="#swe5">SWE.5</a><a href="#swe6">SWE.6</a><a href="#trace">Traceability</a>'
             '<a href="#prov">Provenance</a></nav><main>']
    parts.append(f'<section id="summary"><h2>Summary</h2><div class="cards">'
                 f'<div class="card"><b>{n_ver}/{len(swr_status)}</b>software requirements verified</div>'
                 f'<div class="card"><b>{n_pass}/{len(cases)}</b>test cases passed</div>'
                 f'<div class="card"><b>{unit_tests}</b>unit test cases / checks executed</div>'
                 f'<div class="card"><b>{len(issues)}</b>traceability issues</div></div>'
                 f'<p class="small">Demonstration work products for code quality and traceability; not an assessed '
                 f'capability level. Manual (witnessed) qualification cases are marked.</p>'
                 + ("".join(f'<p class="issue">⚠ {html.escape(i)}</p>' for i in issues) if issues else "")
                 + "</section>")
    sys_rows = "".join(f"<tr><td>{r['ID']}</td><td>{inline(r['Requirement'])}</td><td>{inline(r['Source'])}</td>"
                       f"<td>{', '.join(x['ID'] for x in wp['swr'] if r['ID'] in ids(x['Derived from'], 'SYS'))}</td></tr>"
                       for r in wp["sys"])
    swr_rows = "".join(f"<tr><td>{s}</td><td>{inline(r['Requirement'])}</td><td>{r['Derived from']}</td>"
                       f"<td>{inline(r['Allocated to'])}</td><td>{r['Verified by']}</td><td>{badge(swr_status[s])}</td></tr>"
                       for s, r in swr.items())
    parts.append(f'<section id="swe1"><h2>SWE.1 Software requirements analysis</h2><h3>System requirements</h3>'
                 f"<table><thead><tr><th>ID</th><th>Requirement</th><th>Source</th><th>Refined by</th></tr></thead>"
                 f"<tbody>{sys_rows}</tbody></table><h3>Software requirements</h3><table><thead><tr><th>ID</th>"
                 f"<th>Requirement</th><th>Derived from</th><th>Allocated to</th><th>Verified by</th><th>Status</th>"
                 f"</tr></thead><tbody>{swr_rows}</tbody></table></section>")
    figs = "".join(f'<figure><div class="svg">{svg}</div><figcaption>{name}.puml</figcaption></figure>'
                   for name, svg in diagrams.items())
    parts.append(f'<section id="swe2"><h2>SWE.2 Software architectural design</h2>{figs}'
                 f'{md_to_html(ASPICE / "swe2-architecture/architecture.md").split("<h3>Software elements</h3>", 1)[-1]}'
                 f"</section>")
    parts.append(f'<section id="swe3"><h2>SWE.3 Software detailed design</h2>'
                 f'{md_to_html(ASPICE / "swe3-detailed-design/detailed-design.md")}</section>')

    def case_rows(level):
        return "".join(f"<tr><td>{c}</td><td>{inline(v['title'])}</td><td>{', '.join(v['verifies'])}</td>"
                       f"<td>{badge(v['status'])}{' <span class=small>(witnessed)</span>' if v.get('manual') else ''}</td>"
                       f"<td>{inline(str(v.get('tests') or '')) if level == 'UT' else ''}</td>"
                       f"<td>{inline(v['detail'])}{('<br><span class=small>' + html.escape(v['source']) + '</span>') if v.get('source') else ''}</td></tr>"
                       for c, v in cases.items() if v["level"] == level)
    head = "<table><thead><tr><th>ID</th><th>Test</th><th>Verifies</th><th>Result</th><th>{}</th><th>Detail</th></tr></thead><tbody>"
    parts.append(f'<section id="swe4"><h2>SWE.4 Software unit verification</h2>'
                 f'{head.format("Cases")}{case_rows("UT")}</tbody></table></section>')
    parts.append(f'<section id="swe5"><h2>SWE.5 Software integration and integration test</h2>'
                 f'<p class="small">tools/e2e_check.py against the running system — {html.escape(integ_note)}</p>'
                 f'{head.format("")}{case_rows("IT")}</tbody></table></section>')
    parts.append(f'<section id="swe6"><h2>SWE.6 Software qualification test</h2>'
                 f'{head.format("")}{case_rows("QT")}</tbody></table></section>')
    levels = [("UT", "Unit"), ("IT", "Integration"), ("QT", "Qualification")]
    trace = "".join(f"<tr><td>{s}</td>" + "".join(
        "<td>" + " ".join(f"{c} {badge(cases[c]['status'])}" for c in cases
                          if cases[c]["level"] == lv and s in cases[c]["verifies"]) + "</td>" for lv, _ in levels)
        + f"<td>{badge(swr_status[s])}</td></tr>" for s in swr)
    parts.append(f'<section id="trace"><h2>Bidirectional traceability</h2><table><thead><tr><th>Requirement</th>'
                 + "".join(f"<th>{n}</th>" for _, n in levels) + f"<th>Status</th></tr></thead><tbody>{trace}</tbody></table>"
                 + ("<p>No traceability issues: every system requirement is refined, every software requirement is "
                    "allocated and verified, and every test case traces to a requirement.</p>" if not issues else "")
                 + "</section>")
    parts.append('<section id="prov"><h2>Provenance</h2><table><thead><tr><th>Repository</th><th>Branch</th>'
                 '<th>Commit</th></tr></thead><tbody>'
                 + "".join(f"<tr><td>{html.escape(a)}</td><td>{html.escape(b)}</td><td>{html.escape(c)}</td></tr>" for a, b, c in prov)
                 + f"</tbody></table><p class=small>Host {html.escape(socket.gethostname())}. Regenerate with "
                   f"<code>python3 aspice/tools/generate_report.py --full</code>.</p></section></main>")
    return (f"<!doctype html><html lang=en><head><meta charset=utf-8><meta name=viewport content='width=device-width,"
            f"initial-scale=1'><title>ASPICE SWE report — X-Verse e2e</title><style>{CSS}</style></head><body>"
            + "".join(parts) + "</body></html>")


def render_markdown(wp, cases, swr_status, issues, unit, integ_note, prov, stamp):
    """GitHub-renderable version of the report (report/README.md); diagrams are embedded SVGs."""
    n_pass = sum(1 for c in cases.values() if c["status"] == "PASS")
    n_ver = sum(1 for s in swr_status.values() if s == "VERIFIED")
    icon = {"PASS": "✅ PASS", "VERIFIED": "✅ VERIFIED", "FAIL": "❌ FAIL", "PARTIAL": "⚠️ PARTIAL"}

    def cell(text):
        return str(text).replace("|", "\\|").replace("\n", " ")

    out = [f"# ASPICE SWE.1–SWE.6 report — X-Verse end-to-end demonstration", "",
           f"Generated {stamp} by `aspice/tools/generate_report.py` (the same data as "
           f"[aspice-swe-report.html](aspice-swe-report.html) and [summary.json](summary.json)).", "",
           "CARLA · virtual vehicle · Zenoh VCU · SOME/IP bridge · S-CORE ECU with DTC `CC.LostCommunication` "
           "over SOVD (inc_diagnostics PR #16 `sovd_adapter`) · OTA vECU (certgen, EOL backend, RTCU) · Android targets.", "",
           "## Summary", "",
           "| Software requirements verified | Test cases passed | Unit test cases / checks | Traceability issues |",
           "| --- | --- | --- | --- |",
           f"| **{n_ver}/{len(swr_status)}** | **{n_pass}/{len(cases)}** | "
           f"**{sum((u.get('tests') or 0) for u in unit.values())}** | **{len(issues)}** |", ""]
    out += [f"- ⚠️ {i}" for i in issues] + ([""] if issues else [])
    out += ["Demonstration work products for code quality and traceability; not an assessed capability level. "
            "Work products: [requirements](../swe1-requirements/), [architecture](../swe2-architecture/architecture.md), "
            "[detailed design](../swe3-detailed-design/detailed-design.md), [unit](../swe4-unit-verification/unit-verification.md), "
            "[integration](../swe5-integration-test/integration-test.md) and "
            "[qualification](../swe6-qualification-test/qualification-test.md) test specifications.", "",
            "## SWE.2 Architecture", ""]
    for name in sorted(p.stem for p in DIAGRAMS.glob("*.puml")):
        out += [f"![{name}](../swe2-architecture/diagrams/{name}.svg)", ""]
    out += ["## SWE.1 Software requirements", "", "| ID | Requirement | Derived from | Allocated to | Status |",
            "| --- | --- | --- | --- | --- |"]
    out += [f"| {r['ID']} | {cell(r['Requirement'])} | {r['Derived from']} | {cell(r['Allocated to'])} | "
            f"{icon.get(swr_status[r['ID']], swr_status[r['ID']])} |" for r in wp["swr"]]
    for level, title in (("UT", "SWE.4 Unit verification"), ("IT", "SWE.5 Integration test"),
                         ("QT", "SWE.6 Qualification test")):
        out += ["", f"## {title}", ""]
        if level == "IT":
            out += [f"`tools/e2e_check.py` against the running system — {integ_note}", ""]
        out += ["| ID | Test | Verifies | Result | Detail |", "| --- | --- | --- | --- | --- |"]
        for c, v in cases.items():
            if v["level"] != level:
                continue
            result = icon.get(v["status"], v["status"]) + (" (witnessed)" if v.get("manual") else "")
            detail = cell(v["detail"]) + (f" — {v['tests']} cases" if level == "UT" and v.get("tests") else "")
            out.append(f"| {c} | {cell(v['title'])} | {', '.join(v['verifies'])} | {result} | {detail} |")
    out += ["", "## Bidirectional traceability", "", "| Requirement | Unit | Integration | Qualification | Status |",
            "| --- | --- | --- | --- | --- |"]
    for sid in swr_status:
        cols = [" ".join(c for c, v in cases.items() if v["level"] == lv and sid in v["verifies"]) or "—"
                for lv in ("UT", "IT", "QT")]
        out.append(f"| {sid} | {' | '.join(cols)} | {icon.get(swr_status[sid], swr_status[sid])} |")
    out += ["", "## Provenance", "", "| Repository | Branch | Commit |", "| --- | --- | --- |"]
    out += [f"| {a} | {b} | {cell(c)} |" for a, b, c in prov]
    out += ["", "Regenerate with the system running: `python3 aspice/tools/generate_report.py --full`.", ""]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--full", action="store_true", help="also run the OTA (Maven) and S-CORE/PR16 (Bazel) suites")
    args = parser.parse_args()
    stamp = now()
    wp = load_work_products()
    print("rendering diagrams ...")
    diagrams = render_diagrams()
    print("unit verification ...")
    unit = unit_results(args.full)
    print("integration checks ...")
    integ, integ_note = integration_results()
    print("qualification records ...")
    qual = qualification_results()
    cases, swr_status, issues = evaluate(wp, unit, integ, qual)
    REPORT.mkdir(parents=True, exist_ok=True)
    (REPORT / "aspice-swe-report.html").write_text(render(wp, diagrams, cases, swr_status, issues, unit,
                                                          integ_note, provenance(), stamp))
    (REPORT / "README.md").write_text(render_markdown(wp, cases, swr_status, issues, unit, integ_note,
                                                      provenance(), stamp))
    summary = {"generated": stamp, "requirements": swr_status, "cases": cases, "traceability_issues": issues}
    (REPORT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    failed = [c for c, v in cases.items() if v["status"] == "FAIL"]
    print(f"requirements verified: {sum(s == 'VERIFIED' for s in swr_status.values())}/{len(swr_status)}; "
          f"cases passed: {sum(v['status'] == 'PASS' for v in cases.values())}/{len(cases)}; "
          f"traceability issues: {len(issues)}" + (f"; FAILED: {', '.join(failed)}" if failed else ""))
    print(f"report: {REPORT / 'aspice-swe-report.html'}")
    return 1 if failed or issues else 0


if __name__ == "__main__":
    sys.exit(main())
