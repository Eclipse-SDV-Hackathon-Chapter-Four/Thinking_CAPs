#!/usr/bin/env python3
"""Generate the ASPICE SWE.1-SWE.6 evidence report for the X-COM Serial2CAN bridge.

Parses the work products in aspice/, renders the PlantUML views locally,
re-executes the host test suite (pytest + JUnit XML, coverage.py including the
CLI child process), runs ruff, mypy and lizard, checks the recorded hardware
and live X-Verse evidence against the current sources, computes bidirectional
traceability and writes:

    aspice/report/aspice-swe-report.html   aspice/report/summary.json   aspice/report/evidence/*

Run:  .venv/bin/python aspice/tools/generate_report.py      (from the bridge folder)
Needs the dev requirements plus ruff, coverage, mypy and lizard in .venv, and java.
"""
import csv
import hashlib
import html
import io
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ASPICE = Path(__file__).resolve().parents[1]
BRIDGE = ASPICE.parent
REPO = BRIDGE.parents[2]
REPORT = ASPICE / "report"
OUT = REPORT / "evidence"
VENV = BRIDGE / ".venv" / "bin"
EVIDENCE = BRIDGE / "evidence"
PLANTUML_VERSION, PLANTUML_SHA1 = "1.2024.7", "cb57b315d96413d55622edaa8c4b234e2ebf4b1f"
PLANTUML_JAR = REPO / "X-Verse" / ".cache" / "tools" / f"plantuml-{PLANTUML_VERSION}.jar"
LINE_TARGET, BRANCH_TARGET, CCN_LIMIT = 90.0, 85.0, 10
LEVEL_ORDER = ["UT", "IT", "QT", "AN", "RV"]


def run(cmd, check=True, env=None, timeout=900):
    result = subprocess.run(cmd, cwd=BRIDGE, capture_output=True, text=True, timeout=timeout,
                            env={**os.environ, "PYTHONPATH": "", **(env or {})}, check=False)
    if check and result.returncode:
        raise RuntimeError(f"{' '.join(map(str, cmd))} failed:\n{result.stdout[-2000:]}\n{result.stderr[-2000:]}")
    return result


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def first_line(cmd):
    try:
        out = run(cmd, check=False, timeout=60)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except (OSError, IndexError, subprocess.TimeoutExpired) as error:
        return f"unavailable ({error})"


# ---------------------------------------------------------------- work products
def md_tables(text):
    tables, lines, index = [], text.splitlines(), 0
    while index < len(lines) - 1:
        if lines[index].startswith("|") and re.match(r"^\|\s*:?-{3,}", lines[index + 1]):
            header = [cell.strip() for cell in lines[index].strip("|").split("|")]
            rows, index = [], index + 2
            while index < len(lines) and lines[index].startswith("|"):
                rows.append(dict(zip(header, (c.strip() for c in lines[index].strip("|").split("|")), strict=False)))
                index += 1
            tables.append(rows)
        else:
            index += 1
    return tables


def table_with(text, column):
    return next(rows for rows in md_tables(text) if rows and column in rows[0])


def ids(value, prefix):
    return re.findall(rf"\b{prefix}-\d+\b", value or "")


def parse_requirements(path, prefix):
    text, items = path.read_text(), {}
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        heading, _, body = block.partition("\n")
        match = re.match(rf"({prefix}-\d+)\s+(.*)", heading.strip())
        if not match:
            continue
        statement = []
        for line in body.strip().splitlines():
            if line.startswith(("|", "#")):
                break
            statement.append(line.rstrip())
        attributes = {row["Attribute"]: row.get("Value", "") for rows in md_tables(body) for row in rows if "Attribute" in row}
        items[match.group(1)] = {"id": match.group(1), "title": match.group(2), "text": "\n".join(s for s in statement if s),
                                 **{k.lower().replace(" ", "_"): v for k, v in attributes.items()}}
    return items


def load_work_products():
    read = lambda rel: (ASPICE / rel).read_text()  # noqa: E731
    arch = read("swe2-architecture/architecture.md")
    guide = read("swe3-detailed-design/coding-guidelines.md")
    return {
        "sys": parse_requirements(ASPICE / "swe1-requirements/system-requirements.md", "SYS"),
        "swr": parse_requirements(ASPICE / "swe1-requirements/software-requirements.md", "SWR"),
        "elements": table_with(arch, "Satisfies"), "interfaces": table_with(arch, "Provider → consumer"),
        "decisions": table_with(arch, "Decision"),
        "units": table_with(read("swe3-detailed-design/detailed-design.md"), "Implements"),
        "guidelines": table_with(guide, "Rule"),
        "utc": table_with(read("swe4-unit-verification/unit-verification.md"), "Test"),
        "itc": table_with(read("swe5-integration-test/integration-test.md"), "Interfaces"),
        "qtc": table_with(read("swe6-qualification-test/qualification-test.md"), "Method"),
    }


# ---------------------------------------------------------------- tool runs
def render_diagrams():
    if not PLANTUML_JAR.exists():
        PLANTUML_JAR.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve("https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/"
                                   f"{PLANTUML_VERSION}/plantuml-{PLANTUML_VERSION}.jar", PLANTUML_JAR)
    if hashlib.sha1(PLANTUML_JAR.read_bytes()).hexdigest() != PLANTUML_SHA1:
        raise RuntimeError("PlantUML jar SHA-1 mismatch")
    out = REPORT / "diagrams"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    sources = [*sorted(ASPICE.glob("swe*/diagrams/*.puml")), BRIDGE / "docs" / "serial2can.puml"]
    run(["java", "-Djava.awt.headless=true", "-jar", str(PLANTUML_JAR), "-tsvg", "-o", str(out)]
        + [str(s) for s in sources], timeout=300)
    return {s.stem: {"svg": re.sub(r"<\?xml[^>]*\?>", "", (out / f"{s.stem}.svg").read_text()),
                     "source": s.relative_to(BRIDGE).as_posix()} for s in sources}


def run_tests():
    junit = OUT / "pytest-junit.xml"
    for stale in BRIDGE.glob(".coverage*"):
        stale.unlink()
    env = {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "SERIAL2CAN_COVERAGE": "1"}
    started = time.monotonic()
    result = run([str(VENV / "python"), "-m", "coverage", "run", "--parallel-mode", "--branch", "--source=src",
                  "-m", "pytest", "-q", "-p", "no:cacheprovider", "-W", "ignore::UserWarning",
                  f"--junitxml={junit}", "tests"], check=False, env=env, timeout=1200)
    duration = round(time.monotonic() - started, 1)
    (OUT / "pytest.txt").write_text(result.stdout + result.stderr)
    run([str(VENV / "python"), "-m", "coverage", "combine"])
    run([str(VENV / "python"), "-m", "coverage", "json", "-o", str(OUT / "coverage.json")])
    shutil.rmtree(REPORT / "coverage", ignore_errors=True)
    run([str(VENV / "python"), "-m", "coverage", "html", "-d", str(REPORT / "coverage")])
    (REPORT / "coverage" / ".gitignore").unlink(missing_ok=True)
    cases = {}
    for case in ET.parse(junit).getroot().iter("testcase"):
        key = case.get("classname").replace(".", "/") + ".py::" + case.get("name").split("[")[0]
        failed = any(child.tag in ("failure", "error") for child in case)
        entry = cases.setdefault(key, {"instances": 0, "failed": 0, "time": 0.0})
        entry["instances"] += 1
        entry["failed"] += failed
        entry["time"] += float(case.get("time", 0))
    coverage = json.loads((OUT / "coverage.json").read_text())
    return cases, coverage, {"returncode": result.returncode, "duration_s": duration,
                             "summary": (result.stdout.strip().splitlines() or [""])[-1]}


def static_analysis():
    ruff = run([str(VENV / "ruff"), "check", "--output-format", "json", "src", "tests", "launch"], check=False)
    findings = json.loads(ruff.stdout or "[]")
    (OUT / "ruff.json").write_text(json.dumps(findings, indent=2) + "\n")
    mypy = run([str(VENV / "mypy"), "--ignore-missing-imports", "--python-version", "3.10", "src"], check=False)
    (OUT / "mypy.txt").write_text(mypy.stdout + mypy.stderr)
    lizard = run([str(VENV / "lizard"), "--csv", "src", "launch"], check=False)
    (OUT / "complexity.csv").write_text(lizard.stdout)
    functions = [{"nloc": int(r[0]), "ccn": int(r[1]), "function": r[7], "file": r[6]}
                 for r in csv.reader(io.StringIO(lizard.stdout)) if len(r) >= 8 and r[1].isdigit()]
    return findings, {"ok": mypy.returncode == 0, "summary": mypy.stdout.strip().splitlines()[-1]}, functions


# ---------------------------------------------------------------- evaluation
def evaluate(wp, cases, coverage, ruff, mypy, functions):
    hw = json.loads((EVIDENCE / "hardware-check" / "results.json").read_text())
    qt = json.loads((EVIDENCE / "xverse-carla" / "results.json").read_text())
    manifest = json.loads((EVIDENCE / "manifest.json").read_text())
    hw_checks = {c["id"]: c for c in hw["checks"]}
    steps = {s["step"]: s for s in qt["steps"]}
    identity = {f: (h, sha256(BRIDGE / f)) for f, h in manifest["source_sha256"].items()}
    evidence_current = all(a == b for a, b in identity.values())
    results = {req: [] for req in wp["swr"]}

    def add(level, case_id, verifies, status):
        for req in ids(verifies, "SWR"):
            results.setdefault(req, []).append({"level": level, "case": case_id, "status": status})

    def pytest_status(test):
        entry = cases.get(test)
        return "missing" if entry is None else ("failed" if entry["failed"] else "passed")

    for case in wp["utc"]:
        case["status"] = pytest_status(case["Test"])
        case["detail"] = f'{cases.get(case["Test"], {}).get("instances", 0)} instance(s)'
        add("UT", case["ID"], case["Verifies"], case["status"])
    for case in wp["itc"]:
        if case["Test"].startswith("hw:"):
            check = hw_checks.get(case["Test"][3:])
            ok = bool(check) and check["status"] == "passed" and evidence_current
            if case["Test"] == "hw:all-256-status-bytes-through-bridge" and check:
                ok = ok and check["round_trip_ms"]["median"] <= 10
            case["status"] = "passed" if ok else ("failed" if check else "missing")
            case["detail"] = json.dumps({k: v for k, v in (check or {}).items() if k not in ("id", "status")})[:150]
            case["kind"] = "on target (recorded)"
        else:
            case["status"], case["kind"] = pytest_status(case["Test"]), "host (executed now)"
            case["detail"] = f'{cases.get(case["Test"], {}).get("time", 0):.2f} s'
        add("IT", case["ID"], case["Verifies"], case["status"])

    latencies = [round(s["key_to_carla_lights_ms"] - s["key_to_vcu_ms"], 1) for s in qt["steps"]]
    stats_lines = [line for line in (EVIDENCE / "xverse-carla" / "serial2can.log").read_text().splitlines()
                   if " stats " in line]
    live = json.loads(stats_lines[-1].split(" stats ", 1)[1]) if stats_lines else {}
    profile = json.loads((EVIDENCE / "xverse-carla" / "zenoh2can-udp.json").read_text())
    lock = json.loads((REPO / "ThreadX" / "dependencies.lock.json").read_text())["python"]["python-can"]
    pinned = re.search(r"python-can==([\d.]+)", (BRIDGE / "requirements.txt").read_text()).group(1)
    auto = {
        "end-to-end-latency": (len(latencies) == 6 and max(latencies) <= 100,
                               f"VCU → CARLA lamp {latencies} ms (max {max(latencies)})"),
        "udp-multicast-in-x-verse": (profile["can_buses"][0]["bus_type"] == "udp_multicast"
                                     and live.get("bus", {}).get("echo_suppressed", 0) > 0
                                     and live.get("bus", {}).get("can_tx_errors", 1) == 0,
                                     f"bus counters {live.get('bus')}"),
        "evidence-source-identity": (evidence_current, ", ".join(f"{Path(f).name} {'=' if a == b else '≠'}"
                                                                for f, (a, b) in identity.items())),
        "dependency-alignment": (pinned == lock and sys.version_info[:2] >= (3, 10),
                                 f"python-can {pinned} (X-Verse lock {lock}); report Python {sys.version.split()[0]}"),
    }
    for case in wp["qtc"]:
        kind, _, key = case["Source"].partition(":")
        if kind == "step":
            step = steps.get(key)
            ok = bool(step) and qt["status"] == "passed" and step["carla_light_mask"] & 72 == step["expected_bits"]
            case["status"] = "passed" if ok and evidence_current else "failed"
            case["detail"] = (f'mask {step["carla_light_mask"]}, key→VCU {step["key_to_vcu_ms"]} ms, '
                              f'key→CARLA {step["key_to_carla_lights_ms"]} ms') if step else "missing"
            case["image"] = step.get("image") if step else None
        elif kind == "auto":
            ok, case["detail"] = auto[key]
            case["status"] = "passed" if ok else "failed"
        else:
            case["status"], case["detail"] = {"not-run": ("not run", "Environment not available here")}.get(
                key, (key, ""))
        add({"Test": "QT", "Analysis": "AN", "Inspection": "RV"}[case["Method"]], case["ID"], case["Verifies"],
            case["status"])

    issues, children = [], {sid: [] for sid in wp["sys"]}
    alloc = {r: [e["ID"] for e in wp["elements"] if r in ids(e["Satisfies"], "SWR")] for r in wp["swr"]}
    units = {r: [u["ID"] for u in wp["units"] if r in ids(u["Implements"], "SWR")] for r in wp["swr"]}
    for req in wp["swr"].values():
        req["parents"] = ids(req.get("derived_from"), "SYS")
        for parent in req["parents"]:
            if parent not in wp["sys"]:
                issues.append(f"{req['id']} derives from unknown {parent}")
            children.setdefault(parent, []).append(req["id"])
        res = results.get(req["id"], [])
        statuses = {r["status"] for r in res}
        req["status"] = ("not verified" if not res else "failed" if statuses & {"failed", "missing"}
                         else "verified" if statuses == {"passed"} else "partially verified")
        planned = set(re.findall(r"\b(UT|IT|QT|AN|RV)\b", req.get("verification", "")))
        req.update(verifications=res, elements=alloc[req["id"]], units=units[req["id"]],
                   planned=sorted(planned, key=LEVEL_ORDER.index),
                   missing_levels=sorted(planned - {r["level"] for r in res if r["status"] == "passed"},
                                         key=LEVEL_ORDER.index))
        if not req["elements"]:
            issues.append(f"{req['id']} is not allocated to an architecture element")
        if not req["units"]:
            issues.append(f"{req['id']} is not implemented by a software unit")
    issues += [f"{sid} has no derived software requirement" for sid, c in children.items() if not c]
    for table in ("utc", "itc", "qtc", "elements", "units"):
        for row in wp[table]:
            refs = row.get("Verifies") or row.get("Satisfies") or row.get("Implements")
            issues += [f"{row['ID']} references unknown {r}" for r in ids(refs, "SWR") if r not in wp["swr"]]
    traced = {c["Test"] for c in wp["utc"] + wp["itc"]}
    untraced = sorted(set(cases) - traced)
    issues += [f"pytest function not traced to a test case: {t}" for t in untraced]
    for function in functions:
        function["status"] = "ok" if function["ccn"] <= 15 else "review"
    totals = coverage["totals"]
    return {"hw": hw, "qt": qt, "issues": issues, "children": children, "latencies": latencies,
            "evidence_current": evidence_current, "identity": identity, "ruff": ruff, "mypy": mypy,
            "line_pct": 100.0 * totals["covered_lines"] / max(totals["num_statements"], 1),
            "branch_pct": 100.0 * totals["covered_branches"] / max(totals["num_branches"], 1)}


# ---------------------------------------------------------------- HTML
def inline_md(text):
    text = html.escape(text or "")
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)


def statement_html(text):
    """Requirement statement in written order: prose paragraphs and '- ' bullet lists."""
    blocks: list[tuple[str, list[str]]] = []
    for line in (text or "").splitlines():
        if line.startswith("- "):
            if not blocks or blocks[-1][0] != "list":
                blocks.append(("list", []))
            blocks[-1][1].append(line[2:])
        elif line.startswith(" ") and blocks and blocks[-1][0] == "list":
            blocks[-1][1][-1] += " " + line.strip()  # wrapped continuation of a bullet
        elif blocks and blocks[-1][0] == "prose":
            blocks[-1][1].append(line.strip())
        else:
            blocks.append(("prose", [line.strip()]))
    return "".join(inline_md(" ".join(items)) if kind == "prose" else
                   "<ul>" + "".join(f"<li>{inline_md(item)}</li>" for item in items) + "</ul>"
                   for kind, items in blocks)

def badge(status):
    cls = {"passed": "ok", "verified": "ok", "ok": "ok", "failed": "bad", "missing": "bad", "not verified": "bad",
           "partially verified": "warn", "not run": "warn", "review": "warn"}.get(status, "neutral")
    return f'<span class="badge {cls}">{html.escape(status)}</span>'


def table(headers, rows, cls=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def link(rel, label=None):
    return f'<a href="{html.escape((Path("../..") / rel).as_posix())}">{html.escape(label or Path(rel).name)}</a>'


def render(wp, diagrams, cases, coverage, run_info, functions, ev, tools):
    swr = wp["swr"]
    counts = Counter(r["status"] for r in swr.values())
    ut_pass = sum(c["status"] == "passed" for c in wp["utc"])
    it_pass = sum(c["status"] == "passed" for c in wp["itc"])
    qt_pass = sum(c["status"] == "passed" for c in wp["qtc"])
    instances = sum(c["instances"] for c in cases.values())
    failed_instances = sum(c["failed"] for c in cases.values())
    kpis = [
        ("Requirements verified", f"{counts['verified']}/{len(swr)}", f"{counts['partially verified']} partial"),
        ("Host tests", f"{instances - failed_instances}/{instances}", f"pytest in {run_info['duration_s']} s"),
        ("Coverage", f"{ev['line_pct']:.0f}% / {ev['branch_pct']:.0f}%", "line / branch (target 90 / 85)"),
        ("Lint + types", f"{len(ev['ruff'])} / {'0' if ev['mypy']['ok'] else 'errors'}", "ruff findings / mypy errors"),
        ("Unit cases", f"{ut_pass}/{len(wp['utc'])}", "SWE.4"),
        ("Integration", f"{it_pass}/{len(wp['itc'])}", "host + AZ3166"),
        ("Qualification", f"{qt_pass}/{len(wp['qtc'])}", "live X-Verse + analysis"),
        ("Trace issues", str(len(ev["issues"])), "bidirectional"),
    ]
    kpi_html = "".join(f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div>'
                       f'<div class="kpi-sub">{c}</div></div>' for a, b, c in kpis)

    def diagrams_html(names):
        return "".join(f'<figure class="diagram"><div class="svg">{diagrams[n]["svg"]}</div><figcaption>{n} — '
                       f'{link(diagrams[n]["source"], diagrams[n]["source"])}</figcaption></figure>' for n in names)

    sys_rows = [[f'<span class="id">{s["id"]}</span>', inline_md(s["title"]), statement_html(s["text"]),
                 ", ".join(ev["children"].get(s["id"], [])) or badge("not derived")] for s in wp["sys"].values()]
    req_rows = [[f'<span class="id" id="{r["id"]}">{r["id"]}</span>', f'<strong>{inline_md(r["title"])}</strong>'
                 f'<div class="muted">{statement_html(r["text"])}</div>', html.escape(r.get("type", "")),
                 ", ".join(r["parents"]), " ".join(r["planned"]), inline_md(r.get("criterion", "")), badge(r["status"])]
                for r in swr.values()]
    trace_rows = []
    for r in swr.values():
        cells = {}
        for v in r["verifications"]:
            cls = "ok" if v["status"] == "passed" else "warn" if v["status"] == "not run" else "bad"
            cells.setdefault(v["level"], []).append(f'<span class="tc {cls}">{v["case"]}</span>')
        trace_rows.append([f'<a href="#{r["id"]}">{r["id"]}</a>', ", ".join(r["parents"]), ", ".join(r["elements"]),
                           ", ".join(r["units"])] + [" ".join(cells.get(lv, [])) or "—" for lv in LEVEL_ORDER]
                          + [badge(r["status"])])
    utc_rows = [[f'<span class="id">{c["ID"]}</span>', inline_md(c["Test case"]), c["Unit"], c["Verifies"],
                 f'<code>{html.escape(c["Test"].split("::")[1])}</code>', badge(c["status"]),
                 f'<span class="muted">{c["detail"]}</span>'] for c in wp["utc"]]
    itc_rows = [[f'<span class="id">{c["ID"]}</span>', inline_md(c["Test case"]), c["Interfaces"], c["Verifies"],
                 f'<span class="muted">{c["kind"]}</span>', badge(c["status"]),
                 f'<span class="muted">{html.escape(c["detail"])}</span>'] for c in wp["itc"]]
    qtc_rows = [[f'<span class="id">{c["ID"]}</span>', inline_md(c["Test case"]), c["Method"], c["Verifies"],
                 badge(c["status"]), f'<span class="muted">{html.escape(c["detail"])}</span>'] for c in wp["qtc"]]
    gallery = "".join(f'<figure class="shot"><img src="../../evidence/xverse-carla/{html.escape(c["image"])}" '
                      f'alt="{c["ID"]}"><figcaption>{c["ID"]} · {c["Source"][5:]}</figcaption></figure>'
                      for c in wp["qtc"] if c.get("image"))
    files = coverage["files"]
    cov_rows = [[html.escape(name), f'{f["summary"]["covered_lines"]}/{f["summary"]["num_statements"]}',
                 f'{100 * f["summary"]["covered_lines"] / max(f["summary"]["num_statements"], 1):.1f}%',
                 f'{f["summary"]["covered_branches"]}/{f["summary"]["num_branches"]}',
                 f'{100 * f["summary"]["covered_branches"] / max(f["summary"]["num_branches"], 1):.1f}%']
                for name, f in sorted(files.items())]
    ruff_rows = [[html.escape(f'{Path(f["filename"]).relative_to(BRIDGE)}:{f["location"]["row"]}'),
                  f'<code>{f["code"]}</code>', html.escape(f["message"])] for f in ev["ruff"]] or [
                     ["—", "—", "No findings with the CG-02 rule set"]]
    ccn = [f["ccn"] for f in functions]
    complex_rows = [[html.escape(f["file"]), f'<code>{html.escape(f["function"])}</code>', f["nloc"], f["ccn"],
                     badge(f["status"])] for f in sorted(functions, key=lambda f: -f["ccn"])[:8]]
    element_rows = [[f'<span class="id">{e["ID"]}</span>', inline_md(e["Element"]), inline_md(e["Responsibility"]),
                     e["Satisfies"]] for e in wp["elements"]]
    interface_rows = [[f'<span class="id">{i["ID"]}</span>', inline_md(i["Interface"]), inline_md(i["Provider → consumer"]),
                       inline_md(i["Type and contract"])] for i in wp["interfaces"]]
    decision_rows = [[f'<span class="id">{d["ID"]}</span>', inline_md(d["Decision"]), inline_md(d["Rationale"])]
                     for d in wp["decisions"]]
    unit_rows = [[f'<span class="id">{u["ID"]}</span>', inline_md(u["Unit"]), inline_md(u["Source / functions"]),
                  u["Element"], u["Implements"]] for u in wp["units"]]
    guide_rows = [[f'<span class="id">{g["ID"]}</span>', inline_md(g["Rule"]), inline_md(g["Check"])] for g in wp["guidelines"]]
    gaps = [f'{r["id"]} {inline_md(r["title"])}: {r["status"]}' + (f' (missing {", ".join(r["missing_levels"])})'
            if r["missing_levels"] else "") for r in swr.values() if r["status"] != "verified"]
    issues = ev["issues"] or ["None: every SYS has derived SWR; every SWR is allocated, implemented and verified by "
                              "traced cases; every pytest function is traced."]
    evidence_rows = [[p, link(f, f), d] for p, f, d in [
        ("SWE.1", "aspice/swe1-requirements/software-requirements.md", "Software requirements (input: system-requirements.md)"),
        ("SWE.2", "aspice/swe2-architecture/architecture.md", "Architecture, decisions, elements, interfaces"),
        ("SWE.3", "aspice/swe3-detailed-design/detailed-design.md", "Units, design notes"),
        ("SWE.3", "aspice/swe3-detailed-design/coding-guidelines.md", "Coding guidelines"),
        ("SWE.4", "aspice/swe4-unit-verification/unit-verification.md", "Unit verification strategy and cases"),
        ("SWE.5", "aspice/swe5-integration-test/integration-test.md", "Integration strategy and cases"),
        ("SWE.5", "evidence/hardware-check/results.json", "AZ3166 hardware integration run"),
        ("SWE.6", "aspice/swe6-qualification-test/qualification-test.md", "Qualification strategy and cases"),
        ("SWE.6", "evidence/xverse-carla/results.json", "Live X-Verse + CARLA run"),
        ("All", "evidence/manifest.json", "Source hashes of the recorded evidence")]]
    evidence_rows += [["SWE.4", '<a href="coverage/index.html">coverage/index.html</a> · <a href="evidence/ruff.json">ruff.json</a> · '
                       '<a href="evidence/mypy.txt">mypy.txt</a> · <a href="evidence/complexity.csv">complexity.csv</a> · '
                       '<a href="evidence/pytest-junit.xml">pytest-junit.xml</a>', "Tool outputs of this generation"],
                      ["All", '<a href="summary.json">summary.json</a>', "Machine-readable summary"]]
    nav = "".join(f'<a href="#{a}">{b}</a>' for a, b in [
        ("overview", "Overview"), ("swe1", "SWE.1 Requirements"), ("swe2", "SWE.2 Architecture"),
        ("swe3", "SWE.3 Detailed design"), ("swe4", "SWE.4 Unit verification"), ("swe5", "SWE.5 Integration test"),
        ("swe6", "SWE.6 Qualification test"), ("trace", "Traceability"), ("gaps", "Gaps & issues"),
        ("evidence", "Evidence & tools")])
    css = (ASPICE / "tools" / "report.css").read_text()
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Serial2CAN ASPICE Evidence</title><style>{css}</style></head><body>
<header><h1>ASPICE SWE evidence: X-COM Serial2CAN bridge</h1>
<p>X-Verse/bridges/serial2can · sources <code>{sha256(BRIDGE / "src" / "serial2can_bridge.py")[:12]}</code> · generated {time.strftime("%Y-%m-%d %H:%M %Z")}.
Demonstration of SWE.1–SWE.6 work products, not an assessed capability level.</p></header>
<div class="layout"><nav>{nav}</nav><main>
<section id="overview"><h2>Overview</h2><p class="lead">The host tests, coverage and static analysis are re-executed for every report. The hardware and X-Verse runs are recorded evidence, and the generator checks they were made with the current sources ({badge("passed" if ev["evidence_current"] else "failed")}).</p><div class="kpis">{kpi_html}</div></section>
<section id="swe1"><h2>SWE.1 Software requirements analysis</h2><p class="lead">{len(swr)} software requirements derived from {len(wp["sys"])} system requirements.</p>
<h3>System requirements (input)</h3>{table(["ID", "Title", "Statement", "Derived SWR"], sys_rows)}
<h3>Software requirements</h3>{table(["ID", "Requirement", "Type", "From", "Planned", "Criterion", "Status"], req_rows)}</section>
<section id="swe2"><h2>SWE.2 Software architectural design</h2><p class="lead">{len(wp["elements"])} elements, {len(wp["interfaces"])} interfaces, {len(wp["decisions"])} design decisions. PlantUML is rendered locally.</p>
{diagrams_html(["context", "components", "threads", "handshake", "forwarding", "link-state"])}
<h3>Elements</h3>{table(["ID", "Element", "Responsibility", "Satisfies"], element_rows)}
<h3>Interfaces</h3>{table(["ID", "Interface", "Provider → consumer", "Contract"], interface_rows)}
<h3>Design decisions</h3>{table(["ID", "Decision", "Rationale"], decision_rows)}</section>
<section id="swe3"><h2>SWE.3 Software detailed design and unit construction</h2><p class="lead">{len(wp["units"])} software units.</p>
{table(["ID", "Unit", "Source / functions", "Element", "Implements"], unit_rows)}
{diagrams_html(["reader", "forwarding-core"])}
<h3>Coding guidelines</h3>{table(["ID", "Rule", "Check"], guide_rows)}</section>
<section id="swe4"><h2>SWE.4 Software unit verification</h2><p class="lead">pytest: {html.escape(run_info["summary"])}.</p>
<h3>Unit test cases</h3>{table(["ID", "Test case", "Unit", "Verifies", "pytest function", "Result", "Runs"], utc_rows)}
<h3>Structural coverage (host suite incl. CLI child process)</h3>{table(["File", "Lines", "Line %", "Branches", "Branch %"], cov_rows)}
<p class="muted">Details: <a href="coverage/index.html">coverage/index.html</a></p>
<h3>Lint (ruff, CG-02): {len(ev["ruff"])} findings</h3>{table(["Location", "Rule", "Message"], ruff_rows)}
<h3>Types (mypy, Python 3.10): {badge("passed" if ev["mypy"]["ok"] else "failed")} {html.escape(ev["mypy"]["summary"])}</h3>
<h3>Complexity (lizard, information; {len(functions)} functions, max {max(ccn)}, average {sum(ccn) / len(ccn):.1f}; gate is ruff C901 ≤ {CCN_LIMIT})</h3>{table(["File", "Function", "NLOC", "CCN", "Status"], complex_rows)}</section>
<section id="swe5"><h2>SWE.5 Software integration and integration test</h2><p class="lead">Host integration on pseudo-terminal ECUs (executed now), plus HW/SW integration with the physical AZ3166 (recorded {html.escape(ev["hw"].get("started", ""))}).</p>
{table(["ID", "Test case", "Interfaces", "Verifies", "Kind", "Result", "Detail"], itc_rows)}</section>
<section id="swe6"><h2>SWE.6 Software qualification test</h2><p class="lead">Live X-Verse (<code>run_autoverse.py --enable-camera-display --vcu-zenoh</code>, CARLA {html.escape(ev["qt"].get("carla_server", ""))}) with Serial2CAN in the path, recorded {html.escape(ev["qt"].get("started", ""))}.</p>
{table(["ID", "Test case", "Method", "Verifies", "Result", "Detail"], qtc_rows)}
<h3>CARLA rear-camera frames</h3><div class="gallery">{gallery}</div></section>
<section id="trace"><h2>Bidirectional traceability</h2><p class="lead">SYS → SWR → element → unit → verification cases.</p>
{table(["SWR", "SYS", "ARC", "DD", "UT", "IT", "QT", "AN", "RV", "Status"], trace_rows, "matrix")}</section>
<section id="gaps"><h2>Gaps and consistency issues</h2>
<h3>Requirements not fully verified ({len(gaps)})</h3><ul class="plain">{"".join(f"<li>{g}</li>" for g in gaps) or "<li>None</li>"}</ul>
<h3>Traceability consistency ({len(ev["issues"])} issues)</h3><ul class="plain">{"".join(f"<li>{html.escape(i)}</li>" for i in issues)}</ul></section>
<section id="evidence"><h2>Evidence index and tools</h2>{table(["Process", "Work product", "Content"], evidence_rows)}
<h3>Tool versions</h3>{table(["Tool", "Version"], [[html.escape(k), html.escape(v)] for k, v in tools.items()])}</section>
</main></div></body></html>
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    wp = load_work_products()
    diagrams = render_diagrams()
    cases, coverage, run_info = run_tests()
    ruff, mypy, functions = static_analysis()
    ev = evaluate(wp, cases, coverage, ruff, mypy, functions)
    python = str(VENV / "python")
    tools = {"Python": first_line([python, "--version"]), "pytest": first_line([python, "-m", "pytest", "--version"]),
             "coverage.py": first_line([python, "-m", "coverage", "--version"]),
             "ruff": first_line([str(VENV / "ruff"), "--version"]), "mypy": first_line([str(VENV / "mypy"), "--version"]),
             "lizard": "lizard " + first_line([str(VENV / "lizard"), "--version"]),
             "python-can": first_line([python, "-W", "ignore", "-c", "import can; print(can.__version__)"]),
             "PlantUML": f"{PLANTUML_VERSION} (sha1 {PLANTUML_SHA1[:12]})"}
    (REPORT / "aspice-swe-report.html").write_text(render(wp, diagrams, cases, coverage, run_info, functions, ev, tools))
    summary = {"generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "tools": tools, "tests": run_info,
               "coverage": {"line_percent": round(ev["line_pct"], 2), "branch_percent": round(ev["branch_pct"], 2)},
               "ruff_findings": len(ruff), "mypy_ok": mypy["ok"], "evidence_current": ev["evidence_current"],
               "requirements": {r["id"]: {k: r[k] for k in ("title", "status", "parents", "elements", "units",
                                                            "planned", "missing_levels", "verifications")}
                                for r in wp["swr"].values()},
               "integration": [{k: c[k] for k in ("ID", "Test", "status")} for c in wp["itc"]],
               "qualification": [{k: c.get(k) for k in ("ID", "Source", "status", "detail")} for c in wp["qtc"]],
               "trace_issues": ev["issues"]}
    (REPORT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    for stale in BRIDGE.glob(".coverage*"):
        stale.unlink()
    print(json.dumps({"report": str(REPORT / "aspice-swe-report.html"),
                      "requirements": dict(Counter(r["status"] for r in wp["swr"].values())),
                      "tests": run_info["summary"], "coverage": summary["coverage"], "ruff": len(ruff),
                      "mypy_ok": mypy["ok"], "evidence_current": ev["evidence_current"], "issues": ev["issues"]}, indent=2))
    return 0 if run_info["returncode"] == 0 and not ev["issues"] else 1


if __name__ == "__main__":
    sys.exit(main())
