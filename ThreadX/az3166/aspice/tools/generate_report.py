#!/usr/bin/env python3
"""Generate the ASPICE SWE.1-SWE.6 evidence report for the AZ3166 controller.

Parses the work products in az3166/aspice, executes the static and unit
verification tools, loads the recorded on-target integration (SWE.5) and live
X-Verse qualification (SWE.6) results, computes bidirectional traceability and
writes one self-contained HTML report plus machine-readable evidence:

    report/aspice-swe-report.html   report/summary.json   report/evidence/*

Run from anywhere:  ThreadX/.venv/bin/python az3166/aspice/tools/generate_report.py
Requires: gcc, gcov, cppcheck, java (PlantUML jar is fetched and SHA-1 checked),
arm-none-eabi toolchain + configured build-az3166/, gcovr and lizard (ThreadX/.venv).
"""
import argparse
import csv
import hashlib
import html
import io
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from collections import Counter
from pathlib import Path

ASPICE = Path(__file__).resolve().parents[1]
AZ3166 = ASPICE.parent
THREADX = AZ3166.parent
REPORT = ASPICE / "report"
EVIDENCE = REPORT / "evidence"
BUILD = THREADX / "build-aspice"
FIRMWARE_BUILD = THREADX / "build-az3166"
VENV_BIN = THREADX / ".venv" / "bin"
PLANTUML_VERSION = "1.2024.7"
PLANTUML_SHA1 = "cb57b315d96413d55622edaa8c4b234e2ebf4b1f"  # Maven Central .sha1
PLANTUML_JAR = THREADX / ".cache" / "tools" / f"plantuml-{PLANTUML_VERSION}.jar"
UNIT_SOURCES = ["src/lights_protocol.c", "az3166/src/slcan.c"]
STATIC_SOURCES = ["az3166/src", "src/lights_protocol.c"]
UNIT_TESTS = {
    "test_lights_protocol": (["tests/test_protocol.c", "src/lights_protocol.c"], ["src"]),
    "test_slcan": (["az3166/tests/test_slcan.c", "az3166/src/slcan.c"], ["az3166/src"]),
    "test_slcan_edge": (["az3166/tests/test_slcan_edge.c", "az3166/src/slcan.c"], ["az3166/src"]),
}
IT_RESULTS = THREADX / "artifacts" / "az3166-uart-can" / "results.json"
IT_BUILD = THREADX / "artifacts" / "az3166-uart-can" / "build.json"
QT_RESULTS = THREADX / "artifacts" / "az3166-xverse-carla" / "results.json"
LINUX_BUILD = THREADX / "artifacts" / "linux-zonal-lights" / "build.json"
CCN_LIMIT, CCN_JUSTIFIED_LIMIT = 15, 25


def run(cmd, cwd=THREADX, check=True, timeout=900):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(f"{' '.join(map(str, cmd))} failed:\n{result.stdout}\n{result.stderr}")
    return result


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tool_version(cmd):
    try:
        out = run(cmd, check=False, timeout=60)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except Exception as error:  # noqa: BLE001 - reported, not fatal
        return f"unavailable ({error})"


# --------------------------------------------------------------------------
# Work product parsing
# --------------------------------------------------------------------------
def md_tables(text):
    """All pipe tables as lists of dicts keyed by the header cells."""
    tables, lines = [], text.splitlines()
    index = 0
    while index < len(lines) - 1:
        if lines[index].startswith("|") and re.match(r"^\|\s*:?-{3,}", lines[index + 1]):
            header = [cell.strip() for cell in lines[index].strip("|").split("|")]
            rows, index = [], index + 2
            while index < len(lines) and lines[index].startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
                rows.append(dict(zip(header, cells)))
                index += 1
            tables.append(rows)
        else:
            index += 1
    return tables


def table_with(text, column):
    for rows in md_tables(text):
        if rows and column in rows[0]:
            return rows
    raise ValueError(f"no table with column {column!r}")


def ids(value, prefix):
    return re.findall(rf"\b{prefix}-\d+\b", value or "")


def parse_requirements(path, prefix):
    text = path.read_text()
    items = {}
    for block in re.split(r"^### ", text, flags=re.M)[1:]:
        heading, _, body = block.partition("\n")
        match = re.match(rf"({prefix}-\d+)\s+(.*)", heading.strip())
        if not match:
            continue
        statement = []
        for line in body.strip().splitlines():
            if line.startswith("|") or line.startswith("#"):
                break
            statement.append(line.strip())
        attributes = {}
        for rows in md_tables(body):
            for row in rows:
                if "Attribute" in row:
                    attributes[row["Attribute"]] = row.get("Value", "")
        section = ""
        before = text[: text.index("### " + heading)]
        sections = re.findall(r"^## (.+)$", before, flags=re.M)
        if sections:
            section = sections[-1]
        items[match.group(1)] = {"id": match.group(1), "title": match.group(2),
                                 "text": "\n".join(s for s in statement if s), "section": section,
                                 **{key.lower().replace(" ", "_"): value for key, value in attributes.items()}}
    return items


def load_work_products():
    sys_reqs = parse_requirements(ASPICE / "swe1-requirements" / "system-requirements.md", "SYS")
    swr = parse_requirements(ASPICE / "swe1-requirements" / "software-requirements.md", "SWR")
    arch_text = (ASPICE / "swe2-architecture" / "architecture.md").read_text()
    elements = table_with(arch_text, "Satisfies")
    interfaces = table_with(arch_text, "Provider → consumer")
    decisions = table_with(arch_text, "Decision")
    dd_text = (ASPICE / "swe3-detailed-design" / "detailed-design.md").read_text()
    units = table_with(dd_text, "Implements")
    cg_text = (ASPICE / "swe3-detailed-design" / "coding-guidelines.md").read_text()
    guidelines = table_with(cg_text, "Rule")
    deviations = table_with(cg_text, "Justification")
    utc = table_with((ASPICE / "swe4-unit-verification" / "unit-verification.md").read_text(), "Executable")
    itc = table_with((ASPICE / "swe5-integration-test" / "integration-test.md").read_text(), "Interfaces")
    qtc = table_with((ASPICE / "swe6-qualification-test" / "qualification-test.md").read_text(), "Method")
    return dict(sys=sys_reqs, swr=swr, elements=elements, interfaces=interfaces, decisions=decisions,
                units=units, guidelines=guidelines, deviations=deviations, utc=utc, itc=itc, qtc=qtc)


# --------------------------------------------------------------------------
# Tool execution
# --------------------------------------------------------------------------
def render_diagrams():
    if not PLANTUML_JAR.exists():
        PLANTUML_JAR.parent.mkdir(parents=True, exist_ok=True)
        url = ("https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/"
               f"{PLANTUML_VERSION}/plantuml-{PLANTUML_VERSION}.jar")
        urllib.request.urlretrieve(url, PLANTUML_JAR)
    digest = hashlib.sha1(PLANTUML_JAR.read_bytes()).hexdigest()
    if digest != PLANTUML_SHA1:
        raise RuntimeError(f"PlantUML jar SHA-1 mismatch: {digest}")
    out = REPORT / "diagrams"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    sources = sorted(ASPICE.glob("swe*/diagrams/*.puml"))
    run(["java", "-Djava.awt.headless=true", "-jar", str(PLANTUML_JAR), "-tsvg", "-o", str(out)]
        + [str(source) for source in sources], timeout=300)
    diagrams = {}
    for source in sources:
        svg = (out / f"{source.stem}.svg").read_text()
        svg = re.sub(r"<\?xml[^>]*\?>", "", svg)
        diagrams[source.stem] = {"svg": svg, "source": source.relative_to(THREADX).as_posix(),
                                 "process": source.parts[-3].split("-")[0].upper().replace("SWE", "SWE.")}
    return diagrams


def unit_tests():
    shutil.rmtree(BUILD, ignore_errors=True)
    BUILD.mkdir(parents=True)
    results = {}
    for name, (sources, includes) in UNIT_TESTS.items():
        cmd = ["gcc", "--coverage", "-O0", "-g", "-Wall", "-Wextra", "-Werror", "-o", str(BUILD / name)]
        cmd += [f"-I{THREADX / include}" for include in includes] + [str(THREADX / s) for s in sources]
        run(cmd, cwd=BUILD)
        start = time.monotonic()
        outcome = run([str(BUILD / name)], cwd=BUILD, check=False)
        results[name] = {"status": "passed" if outcome.returncode == 0 else "failed",
                         "output": (outcome.stdout + outcome.stderr).strip(),
                         "duration_ms": round((time.monotonic() - start) * 1000, 1),
                         "sources": sources}
    gcovr = [str(VENV_BIN / "gcovr"), "-r", str(THREADX), str(BUILD)]
    for source in UNIT_SOURCES:
        gcovr += ["--filter", str(THREADX / source)]
    run(gcovr + ["--json-summary-pretty", "--json-summary", str(EVIDENCE / "coverage-summary.json")], cwd=BUILD)
    summary = json.loads((EVIDENCE / "coverage-summary.json").read_text())
    shutil.rmtree(REPORT / "coverage", ignore_errors=True)
    (REPORT / "coverage").mkdir()
    run(gcovr + ["--html-details", str(REPORT / "coverage" / "index.html")], cwd=BUILD)
    (EVIDENCE / "unit-tests.json").write_text(json.dumps(results, indent=2) + "\n")
    return results, summary


def static_analysis():
    threadx_src = FIRMWARE_BUILD / "_deps" / "threadx-src"
    common = ["--std=c11", "--inline-suppr", "--quiet", "-I", "az3166/src", "-I", "az3166/compat", "-I", "src",
              "-DZONAL_VERSION=\"1.0.0\"", "-DTHREADX_REVISION=\"pinned\"", "-DZONAL_TIMEOUT_MS=0",
              "--suppress=missingIncludeSystem"]
    template = "--template={file}|{line}|{severity}|{id}|{message}"
    general = run(["cppcheck", "--enable=warning,style,performance,portability", template,
                   "-I", str(threadx_src / "common" / "inc"), "-I", str(threadx_src / "ports/cortex_m4/gnu/inc"),
                   "-DTX_INCLUDE_USER_DEFINE_FILE"] + common + STATIC_SOURCES, check=False)
    findings = []
    for line in general.stderr.splitlines():
        parts = line.split("|", 4)
        if len(parts) == 5:
            findings.append(dict(zip(("file", "line", "severity", "id", "message"), parts)))
    (EVIDENCE / "cppcheck.txt").write_text(general.stderr)
    misra = run(["cppcheck", "--addon=misra", "--suppress=missingInclude",
                 "--template={file}|{line}|{id}"] + common + STATIC_SOURCES, check=False, timeout=1200)
    misra_rules = Counter(line.split("|")[2] for line in misra.stderr.splitlines()
                          if line.count("|") == 2 and "misra" in line)
    (EVIDENCE / "misra-baseline.txt").write_text(misra.stderr)
    lizard = run([str(VENV_BIN / "lizard"), "--csv"] + STATIC_SOURCES, check=False)
    functions = []
    for row in csv.reader(io.StringIO(lizard.stdout)):
        if len(row) >= 8 and row[1].isdigit():
            functions.append({"nloc": int(row[0]), "ccn": int(row[1]), "tokens": int(row[2]),
                              "params": int(row[3]), "length": int(row[4]),
                              "function": row[7], "file": Path(row[6]).as_posix()})
    (EVIDENCE / "complexity.csv").write_text(lizard.stdout)
    return findings, misra_rules, functions


def firmware_checks():
    build = run(["cmake", "--build", str(FIRMWARE_BUILD)], check=False, timeout=900)
    log = build.stdout + build.stderr
    (EVIDENCE / "firmware-build.log").write_text(log)
    elf = FIRMWARE_BUILD / "threadx-zonal-lights-az3166.elf"
    binary = FIRMWARE_BUILD / "threadx-zonal-lights-az3166.bin"
    text, data, bss = map(int, run(["arm-none-eabi-size", str(elf)]).stdout.splitlines()[1].split()[:3])
    cmake = (AZ3166 / "CMakeLists.txt").read_text()
    pinned = re.search(r"set\(THREADX_REVISION ([0-9a-f]{40})\)", cmake).group(1)
    source = FIRMWARE_BUILD / "_deps" / "threadx-src"
    actual = run(["git", "-C", str(source), "rev-parse", "HEAD"]).stdout.strip()
    clean = run(["git", "-C", str(source), "diff", "--quiet", "HEAD"], check=False).returncode == 0
    tested = json.loads(IT_BUILD.read_text())["firmware"]["sha256"]
    linux_hash = json.loads(LINUX_BUILD.read_text())["source_sha256"]["src/lights_protocol.c"]
    return {
        "build_ok": build.returncode == 0,
        "warnings": len(re.findall(r"warning:", log)),
        "flash_bytes": text + data, "ram_bytes": data + bss,
        "bin_sha256": sha256(binary), "tested_sha256": tested,
        "threadx_pinned": pinned, "threadx_actual": actual, "threadx_clean": clean,
        "protocol_sha256": sha256(THREADX / "src" / "lights_protocol.c"), "linux_protocol_sha256": linux_hash,
    }


# --------------------------------------------------------------------------
# Evaluation and traceability
# --------------------------------------------------------------------------
def evaluate(wp, unit_results, coverage, findings, misra_rules, functions, firmware):
    it = json.loads(IT_RESULTS.read_text())
    qt = json.loads(QT_RESULTS.read_text())
    it_checks = {check["id"]: check for check in it["checks"]}
    qt_steps = {step["step"]: step for step in qt["steps"]}
    verifications = {req: [] for req in wp["swr"]}

    def add(level, case_id, verifies, status, detail=""):
        for req in ids(verifies, "SWR"):
            verifications.setdefault(req, []).append(
                {"level": level, "case": case_id, "status": status, "detail": detail})

    for case in wp["utc"]:
        status = unit_results.get(case["Executable"], {}).get("status", "missing")
        case["status"] = status
        add("UT", case["ID"], case["Verifies"], status, case["Executable"])

    p95 = it_checks.get("all-256-status-bytes", {}).get("round_trip_ms", {}).get("p95")
    for case in wp["itc"]:
        check = it_checks.get(case["Check"])
        status = check["status"] if check else "missing"
        if case["Check"] == "all-256-status-bytes" and (p95 is None or p95 > 20):
            status = "failed"
        case["status"] = status
        case["detail"] = {k: v for k, v in (check or {}).items() if k not in ("id", "status")}
        add("IT", case["ID"], case["Verifies"], status, case["Check"])

    latencies = [round(s["key_to_carla_lights_ms"] - s["key_to_vcu_ms"], 1) for s in qt["steps"]]
    auto = {
        "end-to-end-latency": (all(v <= 100 for v in latencies) and len(latencies) == 6,
                               f"VCU → CARLA lamp: {latencies} ms (max {max(latencies)} ms)"),
        "resource-budget": (firmware["flash_bytes"] <= 64 * 1024 and firmware["ram_bytes"] <= 32 * 1024,
                            f"flash {firmware['flash_bytes']} B, static RAM {firmware['ram_bytes']} B"),
        "threadx-pinned": (firmware["threadx_pinned"] == firmware["threadx_actual"] and firmware["threadx_clean"],
                           f"pinned {firmware['threadx_pinned'][:12]}, fetched {firmware['threadx_actual'][:12]}, "
                           f"clean={firmware['threadx_clean']}"),
        "shared-protocol-identity": (firmware["protocol_sha256"] == firmware["linux_protocol_sha256"],
                                     f"sha256 {firmware['protocol_sha256'][:16]}…"),
        "firmware-identity": (firmware["bin_sha256"] == firmware["tested_sha256"],
                              f"current {firmware['bin_sha256'][:16]}…, tested {firmware['tested_sha256'][:16]}…"),
    }
    for case in wp["qtc"]:
        kind, _, key = case["Source"].partition(":")
        if kind == "step":
            step = qt_steps.get(key)
            ok = bool(step) and step["carla_light_mask"] & 72 == step["expected_bits"] and qt["status"] == "passed"
            case["status"] = "passed" if ok else "failed"
            case["detail"] = (f"mask {step['carla_light_mask']} (expected bits {step['expected_bits']}), "
                              f"key→VCU {step['key_to_vcu_ms']} ms, key→CARLA {step['key_to_carla_lights_ms']} ms"
                              if step else "step missing")
            case["image"] = step.get("image") if step else None
        elif kind == "auto":
            ok, detail = auto[key]
            case["status"], case["detail"] = ("passed" if ok else "failed"), detail
        else:
            case["status"] = {"reviewed": "passed", "open": "open", "not-run": "not run"}.get(key, key)
            case["detail"] = {"reviewed": "Desk review of the fault paths; no fault injection executed",
                              "open": "Visual inspection not yet recorded",
                              "not-run": "Requires a separate timeout build; not executed"}.get(key, "")
        level = {"Test": "QT", "Analysis": "AN", "Inspection": "RV"}[case["Method"]]
        add(level, case["ID"], case["Verifies"], case["status"], case["Source"])

    # Static findings against deviations.
    justified = {row["ID"]: row for row in wp["deviations"]}
    deviation_for = {"comparePointers": "DEV-01", "unsignedPositive": "DEV-02"}
    for finding in findings:
        finding["deviation"] = deviation_for.get(finding["id"])
        finding["file"] = Path(finding["file"]).as_posix().replace(THREADX.as_posix() + "/", "")
    open_findings = [f for f in findings if not f["deviation"] or f["deviation"] not in justified]
    for function in functions:
        function["file"] = function["file"].replace(THREADX.as_posix() + "/", "")
        if function["ccn"] <= CCN_LIMIT:
            function["status"] = "ok"
        elif function["ccn"] <= CCN_JUSTIFIED_LIMIT and "DEV-03" in justified:
            function["status"] = "justified (DEV-03)"
        else:
            function["status"] = "violation"

    # Requirement status and traceability consistency.
    allocation = {req: [] for req in wp["swr"]}
    for element in wp["elements"]:
        for req in ids(element["Satisfies"], "SWR"):
            allocation.setdefault(req, []).append(element["ID"])
    units = {req: [] for req in wp["swr"]}
    for unit in wp["units"]:
        for req in ids(unit["Implements"], "SWR"):
            units.setdefault(req, []).append(unit["ID"])
    issues = []
    sys_children = {sid: [] for sid in wp["sys"]}
    for req in wp["swr"].values():
        parents = ids(req.get("derived_from"), "SYS")
        req["parents"] = parents
        for parent in parents:
            if parent not in wp["sys"]:
                issues.append(f"{req['id']} derives from unknown {parent}")
            sys_children.setdefault(parent, []).append(req["id"])
        results = verifications.get(req["id"], [])
        statuses = {r["status"] for r in results}
        if not results:
            status = "not verified"
        elif "failed" in statuses or "missing" in statuses:
            status = "failed"
        elif statuses == {"passed"}:
            status = "verified"
        elif "passed" in statuses:
            status = "partially verified"
        else:
            status = "open"
        planned = set(re.findall(r"\b(UT|IT|QT|AN|RV)\b", req.get("verification", "")))
        achieved = {r["level"] for r in results if r["status"] == "passed"}
        req.update(status=status, verifications=results, elements=allocation.get(req["id"], []),
                   units=units.get(req["id"], []), planned=sorted(planned),
                   missing_levels=sorted(planned - achieved))
        if not req["elements"]:
            issues.append(f"{req['id']} is not allocated to an architecture element")
        if not req["units"]:
            issues.append(f"{req['id']} is not implemented by a software unit")
    for sid, children in sys_children.items():
        if not children:
            issues.append(f"{sid} has no derived software requirement")
    referenced = [(case["ID"], req) for table in ("utc", "itc", "qtc") for case in wp[table]
                  for req in ids(case["Verifies"], "SWR")]
    referenced += [(row["ID"], req) for table in ("elements", "units") for row in wp[table]
                   for req in ids(row.get("Satisfies") or row.get("Implements"), "SWR")]
    for source, req in referenced:
        if req not in wp["swr"]:
            issues.append(f"{source} references unknown {req}")
    for unit in wp["units"]:
        for element in ids(unit["Element"], "ARC"):
            if element not in {e["ID"] for e in wp["elements"]}:
                issues.append(f"{unit['ID']} allocated to unknown {element}")
    return dict(it=it, qt=qt, open_findings=open_findings, issues=issues, sys_children=sys_children,
                latencies=latencies, misra_total=sum(misra_rules.values()))


# --------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------
def inline_md(text):
    text = html.escape(text or "")
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)


def statement_html(text):
    """Requirement statement: prose lines joined, '- ' lines as a bullet list."""
    prose, bullets = [], []
    for line in (text or "").splitlines():
        (bullets if line.startswith("- ") else prose).append(line[2:] if line.startswith("- ") else line)
    out = inline_md(" ".join(prose))
    if bullets:
        out += "<ul>" + "".join(f"<li>{inline_md(b)}</li>" for b in bullets) + "</ul>"
    return out


LEVEL_ORDER = ["UT", "IT", "QT", "AN", "RV"]


def badge(status):
    cls = {"passed": "ok", "verified": "ok", "ok": "ok", "failed": "bad", "violation": "bad", "missing": "bad",
           "partially verified": "warn", "open": "warn", "not run": "warn", "not verified": "bad"}.get(
        status, "warn" if "justified" in status else "neutral")
    return f'<span class="badge {cls}">{html.escape(status)}</span>'


def table(headers, rows, cls=""):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table class="{cls}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def link(path, label=None):
    rel = Path("../../..") / Path(path)
    return f'<a href="{html.escape(rel.as_posix())}">{html.escape(label or Path(path).name)}</a>'


def render(wp, diagrams, unit_results, coverage, findings, misra_rules, functions, firmware, ev, tools):
    swr = wp["swr"]
    counts = Counter(req["status"] for req in swr.values())
    total = len(swr)
    cov = coverage
    line_pct = cov.get("line_percent", 0.0)
    branch_pct = cov.get("branch_percent", 0.0)
    ut_pass = sum(r["status"] == "passed" for r in unit_results.values())
    it_pass = sum(c["status"] == "passed" for c in wp["itc"])
    qt_pass = sum(c["status"] == "passed" for c in wp["qtc"])
    qt_open = [c for c in wp["qtc"] if c["status"] not in ("passed",)]
    kpis = [
        ("Requirements verified", f"{counts['verified']}/{total}",
         f"{counts['partially verified']} partial · {counts['open'] + counts['not verified']} open"),
        ("Unit tests", f"{ut_pass}/{len(unit_results)}", f"{len(wp['utc'])} test cases"),
        ("Unit coverage", f"{line_pct:.0f}% / {branch_pct:.0f}%", "line / branch (host units)"),
        ("Static findings open", str(len(ev["open_findings"])),
         f"{len(findings)} reported · {len(findings) - len(ev['open_findings'])} justified"),
        ("Integration tests", f"{it_pass}/{len(wp['itc'])}", "on target AZ3166"),
        ("Qualification", f"{qt_pass}/{len(wp['qtc'])}", f"{len(qt_open)} open/not run"),
        ("Trace issues", str(len(ev["issues"])), "bidirectional consistency"),
        ("Firmware", f"{firmware['flash_bytes'] / 1024:.1f} KiB", f"flash · RAM {firmware['ram_bytes'] / 1024:.1f} KiB"),
    ]
    kpi_html = "".join(f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div>'
                       f'<div class="kpi-sub">{c}</div></div>' for a, b, c in kpis)

    def diagram_block(names):
        out = []
        for name in names:
            d = diagrams[name]
            out.append(f'<figure class="diagram"><div class="svg">{d["svg"]}</div>'
                       f'<figcaption>{html.escape(name)} — {link(d["source"], d["source"])}</figcaption></figure>')
        return "".join(out)

    sys_rows = [[f'<span class="id">{s["id"]}</span>', inline_md(s["title"]), statement_html(s["text"]),
                 ", ".join(ev["sys_children"].get(s["id"], [])) or badge("not derived")] for s in wp["sys"].values()]
    req_rows = [[f'<span class="id" id="{r["id"]}">{r["id"]}</span>',
                 f'<strong>{inline_md(r["title"])}</strong><div class="muted">{statement_html(r["text"])}</div>',
                 html.escape(r.get("type", "")), ", ".join(r["parents"]), " ".join(sorted(r["planned"], key=LEVEL_ORDER.index)),
                 inline_md(r.get("criterion", "")), badge(r["status"])] for r in swr.values()]
    trace_rows = []
    for r in swr.values():
        by_level = {}
        for v in r["verifications"]:
            by_level.setdefault(v["level"], []).append(
                f'<span class="tc {"ok" if v["status"] == "passed" else "warn" if v["status"] in ("open", "not run") else "bad"}">{v["case"]}</span>')
        trace_rows.append([f'<a href="#{r["id"]}">{r["id"]}</a>', ", ".join(r["parents"]), ", ".join(r["elements"]),
                           ", ".join(r["units"])] + [" ".join(by_level.get(level, [])) or "—"
                                                     for level in ("UT", "IT", "QT", "AN", "RV")] + [badge(r["status"])])
    element_rows = [[f'<span class="id">{e["ID"]}</span>', inline_md(e["Element"]), inline_md(e["Responsibility"]),
                     e["Satisfies"]] for e in wp["elements"]]
    interface_rows = [[f'<span class="id">{i["ID"]}</span>', inline_md(i["Interface"]), inline_md(i["Provider → consumer"]),
                       inline_md(i["Type and contract"])] for i in wp["interfaces"]]
    decision_rows = [[f'<span class="id">{d["ID"]}</span>', inline_md(d["Decision"]), inline_md(d["Rationale"])]
                     for d in wp["decisions"]]
    unit_rows = [[f'<span class="id">{u["ID"]}</span>', inline_md(u["Unit"]), inline_md(u["Source / functions"]),
                  u["Element"], u["Implements"]] for u in wp["units"]]
    guideline_rows = [[f'<span class="id">{g["ID"]}</span>', inline_md(g["Rule"]), inline_md(g["Check"])]
                      for g in wp["guidelines"]]
    finding_rows = [[html.escape(f'{f["file"]}:{f["line"]}'), html.escape(f["severity"]), f'<code>{html.escape(f["id"])}</code>',
                     html.escape(f["message"]), badge(f"justified ({f['deviation']})") if f["deviation"] else badge("open")]
                    for f in findings] or [["—", "—", "—", "No findings", badge("ok")]]
    deviation_rows = [[f'<span class="id">{d["ID"]}</span>', inline_md(d["Tool / rule"]), inline_md(d["Location"]),
                       inline_md(d["Justification"])] for d in wp["deviations"]]
    complex_rows = [[html.escape(f["file"]), f'<code>{html.escape(f["function"])}</code>', f["nloc"], f["ccn"], badge(f["status"])]
                    for f in sorted(functions, key=lambda f: -f["ccn"]) if f["ccn"] > 10]
    misra_rows = [[f"<code>{html.escape(rule)}</code>", count] for rule, count in misra_rules.most_common()]
    ccn_values = [f["ccn"] for f in functions]
    file_cov = [[html.escape(f["filename"]), f'{f["line_covered"]}/{f["line_total"]}', f'{f["line_percent"]:.1f}%',
                 f'{f["branch_covered"]}/{f["branch_total"]}', f'{f["branch_percent"]:.1f}%']
                for f in coverage.get("files", [])]
    utc_rows = [[f'<span class="id">{c["ID"]}</span>', inline_md(c["Test case"]), c["Unit"], c["Verifies"],
                 f'<code>{c["Executable"]}</code>', badge(c["status"])] for c in wp["utc"]]
    run_rows = [[f"<code>{name}</code>", badge(r["status"]), f'{r["duration_ms"]} ms', f'<span class="muted">{html.escape(r["output"])}</span>']
                for name, r in unit_results.items()]
    itc_rows = [[f'<span class="id">{c["ID"]}</span>', f'<code>{c["Check"]}</code>', inline_md(c["Test case"]),
                 c["Interfaces"], c["Verifies"], badge(c["status"]),
                 f'<span class="muted">{html.escape(json.dumps(c["detail"])[:160]) if c["detail"] else ""}</span>']
                for c in wp["itc"]]
    qtc_rows = [[f'<span class="id">{c["ID"]}</span>', inline_md(c["Test case"]), c["Method"], c["Verifies"], badge(c["status"]),
                 f'<span class="muted">{html.escape(c.get("detail", ""))}</span>'] for c in wp["qtc"]]
    gallery = "".join(
        f'<figure class="shot"><img src="{html.escape((Path("../../../artifacts/az3166-xverse-carla") / c["image"]).as_posix())}" '
        f'alt="{c["ID"]} CARLA rear camera"><figcaption>{c["ID"]} · {html.escape(c["Source"].split(":")[1])}</figcaption></figure>'
        for c in wp["qtc"] if c.get("image"))
    gaps = [f'{r["id"]} {inline_md(r["title"])} — {r["status"]}'
            + (f' (missing: {", ".join(r["missing_levels"])})' if r["missing_levels"] else "")
            for r in swr.values() if r["status"] != "verified"]
    issues = ev["issues"] or ["None — every SYS has derived SWR; every SWR is allocated, implemented and referenced consistently."]
    evidence_rows = [
        ["SWE.1", link("az3166/aspice/swe1-requirements/system-requirements.md"), "System requirement input"],
        ["SWE.1", link("az3166/aspice/swe1-requirements/software-requirements.md"), "Software requirements"],
        ["SWE.2", link("az3166/aspice/swe2-architecture/architecture.md"), "Architecture, elements, interfaces, resources"],
        ["SWE.3", link("az3166/aspice/swe3-detailed-design/detailed-design.md"), "Units and detailed design"],
        ["SWE.3", link("az3166/aspice/swe3-detailed-design/coding-guidelines.md"), "Coding guidelines and deviations"],
        ["SWE.4", link("az3166/aspice/swe4-unit-verification/unit-verification.md"), "Unit verification strategy and cases"],
        ["SWE.4", '<a href="coverage/index.html">coverage/index.html</a>', "gcovr line/branch coverage details"],
        ["SWE.4", '<a href="evidence/cppcheck.txt">evidence/cppcheck.txt</a> · <a href="evidence/misra-baseline.txt">misra-baseline.txt</a> · <a href="evidence/complexity.csv">complexity.csv</a>', "Static verification outputs"],
        ["SWE.5", link("az3166/aspice/swe5-integration-test/integration-test.md"), "Integration strategy and cases"],
        ["SWE.5", link("artifacts/az3166-uart-can/results.json"), "On-target integration results"],
        ["SWE.6", link("az3166/aspice/swe6-qualification-test/qualification-test.md"), "Qualification strategy and cases"],
        ["SWE.6", link("artifacts/az3166-xverse-carla/results.json"), "Live X-Verse + CARLA results"],
        ["All", '<a href="summary.json">summary.json</a>', "Machine-readable summary of this report"],
    ]
    tool_rows = [[html.escape(k), html.escape(v)] for k, v in tools.items()]
    nav = [("overview", "Overview"), ("swe1", "SWE.1 Requirements"), ("swe2", "SWE.2 Architecture"),
           ("swe3", "SWE.3 Detailed design"), ("swe4", "SWE.4 Unit verification"), ("swe5", "SWE.5 Integration test"),
           ("swe6", "SWE.6 Qualification test"), ("trace", "Traceability"), ("gaps", "Gaps & issues"), ("evidence", "Evidence & tools")]
    nav_html = "".join(f'<a href="#{a}">{b}</a>' for a, b in nav)
    generated = time.strftime("%Y-%m-%d %H:%M %Z")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ASPICE SWE Evidence</title>
<style>
:root{{--bg:#f6f7f9;--panel:#fff;--ink:#1d2330;--muted:#5d6675;--line:#e3e6eb;--accent:#2a5bd7;--ok:#1f7a4d;--ok-bg:#e3f4ea;--warn:#8a5a00;--warn-bg:#fdf1d8;--bad:#a62b2b;--bad-bg:#fbe5e5;--neutral-bg:#eceef2;--code:#eef1f6}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#12151b;--panel:#1a1f27;--ink:#e6e9ee;--muted:#9aa3b2;--line:#2b323d;--accent:#7aa2ff;--ok:#6fd39f;--ok-bg:#16301f;--warn:#f0c46b;--warn-bg:#33290f;--bad:#ff8f8f;--bad-bg:#3a1a1a;--neutral-bg:#262c36;--code:#232a35}}}}
:root[data-theme="dark"]{{--bg:#12151b;--panel:#1a1f27;--ink:#e6e9ee;--muted:#9aa3b2;--line:#2b323d;--accent:#7aa2ff;--ok:#6fd39f;--ok-bg:#16301f;--warn:#f0c46b;--warn-bg:#33290f;--bad:#ff8f8f;--bad-bg:#3a1a1a;--neutral-bg:#262c36;--code:#232a35}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}}
header{{background:var(--panel);border-bottom:1px solid var(--line);padding:20px 24px}}
header h1{{margin:0 0 4px;font-size:22px}}header p{{margin:0;color:var(--muted)}}
.layout{{display:grid;grid-template-columns:220px minmax(0,1fr);gap:24px;max-width:1440px;margin:0 auto;padding:16px}}
nav{{position:sticky;top:16px;align-self:start;display:flex;flex-direction:column;gap:2px}}
nav a{{color:var(--ink);text-decoration:none;padding:6px 10px;border-radius:6px}}nav a:hover{{background:var(--neutral-bg)}}
section{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px 22px;margin-bottom:20px}}
h2{{margin:0 0 6px;font-size:19px}}h3{{margin:20px 0 8px;font-size:15px}}.lead{{color:var(--muted);margin:0 0 14px}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}}
.kpi{{border:1px solid var(--line);border-radius:8px;padding:12px}}.kpi-label{{color:var(--muted);font-size:12px}}
.kpi-value{{font-size:24px;font-weight:650;font-variant-numeric:tabular-nums}}.kpi-sub{{color:var(--muted);font-size:12px}}
.table-wrap{{overflow-x:auto;margin:8px 0}}table{{border-collapse:collapse;width:100%;font-size:13px}}
th,td{{text-align:left;vertical-align:top;padding:7px 9px;border-bottom:1px solid var(--line)}}th{{background:var(--neutral-bg);font-weight:600;white-space:nowrap}}
code{{background:var(--code);padding:1px 5px;border-radius:4px;font-size:12px}}.muted{{color:var(--muted)}}
.id{{font-family:ui-monospace,Menlo,monospace;font-weight:600;white-space:nowrap}}
.badge{{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}}
.badge.ok{{background:var(--ok-bg);color:var(--ok)}}.badge.warn{{background:var(--warn-bg);color:var(--warn)}}
.badge.bad{{background:var(--bad-bg);color:var(--bad)}}.badge.neutral{{background:var(--neutral-bg);color:var(--muted)}}
.tc{{font-family:ui-monospace,Menlo,monospace;font-size:12px;padding:0 4px;border-radius:4px;white-space:nowrap}}
.tc.ok{{background:var(--ok-bg);color:var(--ok)}}.tc.warn{{background:var(--warn-bg);color:var(--warn)}}.tc.bad{{background:var(--bad-bg);color:var(--bad)}}
.diagram{{margin:14px 0;border:1px solid var(--line);border-radius:8px;overflow:hidden}}
.diagram .svg{{background:#fff;overflow-x:auto;padding:8px}}.diagram svg{{max-width:100%;height:auto}}
.diagram figcaption,.shot figcaption{{padding:6px 10px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}}
.gallery{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
.shot{{margin:0;border:1px solid var(--line);border-radius:8px;overflow:hidden}}.shot img{{width:100%;display:block}}
ul.plain{{margin:6px 0;padding-left:18px}}td ul{{margin:4px 0;padding-left:18px}}a{{color:var(--accent)}}
.matrix td{{min-width:56px}}.matrix td:nth-child(-n+4){{white-space:nowrap}}.matrix .tc{{display:inline-block;margin:1px 0}}
@media (max-width:860px){{.layout{{grid-template-columns:1fr;padding:16px}}nav{{position:static;flex-direction:row;flex-wrap:wrap}}header{{padding:16px}}}}
</style></head><body>
<header><h1>ASPICE SWE evidence — ThreadX zonal lighting on MXChip AZ3166</h1>
<p>Software <code>threadx-zonal-lights-az3166</code> 1.0.0 · firmware <code>{firmware['bin_sha256'][:16]}…</code> · ThreadX <code>{firmware['threadx_pinned'][:12]}</code> · generated {generated}. Demonstration of SWE.1–SWE.6 work products. This is not an assessed ASPICE capability level.</p></header>
<div class="layout"><nav>{nav_html}</nav><main>
<section id="overview"><h2>Overview</h2><p class="lead">The key indicators below are computed from the work products and from tool runs during generation. Integration and qualification results are the recorded runs on the physical board and in live X-Verse; the generator checks that they used the same firmware image as the current build.</p>
<div class="kpis">{kpi_html}</div></section>

<section id="swe1"><h2>SWE.1 Software requirements analysis</h2><p class="lead">{total} software requirements, derived from {len(wp['sys'])} system requirements. Each has a type, a verification criterion and planned verification levels (UT/IT/QT/AN/RV).</p>
<h3>System requirements (input)</h3>{table(["ID", "Title", "Statement", "Derived SWR"], sys_rows)}
<h3>Software requirements</h3>{table(["ID", "Requirement", "Type", "From", "Planned", "Criterion", "Status"], req_rows)}</section>

<section id="swe2"><h2>SWE.2 Software architectural design</h2><p class="lead">{len(wp['elements'])} architecture elements, {len(wp['interfaces'])} interfaces and {len(wp['decisions'])} design decisions. The PlantUML views below are rendered locally from source.</p>
{diagram_block(["context", "deployment", "components", "tasks", "sequence", "link-state"])}
<h3>Elements</h3>{table(["ID", "Element", "Responsibility", "Satisfies"], element_rows)}
<h3>Interfaces</h3>{table(["ID", "Interface", "Provider → consumer", "Contract"], interface_rows)}
<h3>Design decisions</h3>{table(["ID", "Decision", "Rationale"], decision_rows)}</section>

<section id="swe3"><h2>SWE.3 Software detailed design and unit construction</h2><p class="lead">{len(wp['units'])} software units. Firmware build: {badge('passed' if firmware['build_ok'] and not firmware['warnings'] else 'failed')} with <code>-Wall -Wextra -Werror</code> ({firmware['warnings']} warnings).</p>
{table(["ID", "Unit", "Source / functions", "Element", "Implements"], unit_rows)}
{diagram_block(["handle-line", "control-loop", "uart-driver"])}
<h3>Coding guidelines</h3>{table(["ID", "Rule", "Check"], guideline_rows)}
<h3>Justified deviations</h3>{table(["ID", "Tool / rule", "Location", "Justification"], deviation_rows)}</section>

<section id="swe4"><h2>SWE.4 Software unit verification</h2><p class="lead">Host unit tests of the target-independent units with gcov coverage, plus static verification of all units.</p>
<h3>Unit test cases</h3>{table(["ID", "Test case", "Unit", "Verifies", "Executable", "Result"], utc_rows)}
<h3>Test execution</h3>{table(["Executable", "Result", "Duration", "Output"], run_rows)}
<h3>Structural coverage</h3>{table(["File", "Lines", "Line %", "Branches", "Branch %"], file_cov)}
<p class="muted">Details: <a href="coverage/index.html">coverage/index.html</a></p>
<h3>Static analysis — cppcheck (warning, style, performance, portability)</h3>{table(["Location", "Severity", "Check", "Message", "Disposition"], finding_rows)}
<h3>Complexity — lizard (functions with CCN &gt; 10 of {len(functions)}; max {max(ccn_values)}, average {sum(ccn_values) / len(ccn_values):.1f})</h3>{table(["File", "Function", "NLOC", "CCN", "Status"], complex_rows)}
<h3>MISRA C:2012 baseline (informative, compliance not claimed) — {ev['misra_total']} findings</h3>{table(["Rule", "Findings"], misra_rows)}</section>

<section id="swe5"><h2>SWE.5 Software integration and integration test</h2><p class="lead">On the physical AZ3166 through the SLCAN/UART interface and the unmodified Zenoh2CAN bridge. Recorded {html.escape(ev['it'].get('started', ''))} with firmware <code>{firmware['tested_sha256'][:16]}…</code> {badge('passed' if firmware['bin_sha256'] == firmware['tested_sha256'] else 'failed')} matching the current build.</p>
{table(["ID", "Check", "Test case", "Interfaces", "Verifies", "Result", "Measured"], itc_rows)}</section>

<section id="swe6"><h2>SWE.6 Software qualification test</h2><p class="lead">In the complete X-Verse environment (<code>run_autoverse.py --enable-camera-display --vcu-zenoh</code>, CARLA {html.escape(ev['qt'].get('carla_server', ''))}), driven through Vehicle Manual Control keys. Recorded {html.escape(ev['qt'].get('started', ''))}.</p>
{table(["ID", "Test case", "Method", "Verifies", "Result", "Detail"], qtc_rows)}
<h3>CARLA rear-camera frames per step</h3><div class="gallery">{gallery}</div></section>

<section id="trace"><h2>Bidirectional traceability</h2><p class="lead">SYS → SWR → architecture element → unit → verification cases. Green cases passed; amber cases are open or not run.</p>
{table(["SWR", "SYS", "ARC", "DD", "UT", "IT", "QT", "AN", "RV", "Status"], trace_rows, "matrix")}</section>

<section id="gaps"><h2>Gaps and consistency issues</h2>
<h3>Requirements not fully verified ({len(gaps)})</h3><ul class="plain">{"".join(f"<li>{g}</li>" for g in gaps) or "<li>None</li>"}</ul>
<h3>Traceability consistency ({len(ev['issues'])} issues)</h3><ul class="plain">{"".join(f"<li>{html.escape(i)}</li>" for i in issues)}</ul></section>

<section id="evidence"><h2>Evidence index and tools</h2>{table(["Process", "Work product", "Content"], evidence_rows)}
<h3>Tool versions</h3>{table(["Tool", "Version"], tool_rows)}</section>
</main></div></body></html>
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.parse_args()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    wp = load_work_products()
    diagrams = render_diagrams()
    unit_results, coverage = unit_tests()
    findings, misra_rules, functions = static_analysis()
    firmware = firmware_checks()
    ev = evaluate(wp, unit_results, coverage, findings, misra_rules, functions, firmware)
    tools = {
        "gcc (host)": tool_version(["gcc", "--version"]),
        "arm-none-eabi-gcc": tool_version(["arm-none-eabi-gcc", "--version"]),
        "cppcheck": tool_version(["cppcheck", "--version"]),
        "lizard": "lizard " + tool_version([str(VENV_BIN / "lizard"), "--version"]),
        "gcovr": tool_version([str(VENV_BIN / "gcovr"), "--version"]),
        "PlantUML": f"{PLANTUML_VERSION} (sha1 {PLANTUML_SHA1[:12]}), " + tool_version(["java", "-version"]),
        "Python": sys.version.split()[0],
    }
    page = render(wp, diagrams, unit_results, coverage, findings, misra_rules, functions, firmware, ev, tools)
    (REPORT / "aspice-swe-report.html").write_text(page)
    summary = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "firmware": firmware, "tools": tools,
        "requirements": {r["id"]: {k: r[k] for k in ("title", "status", "parents", "elements", "units",
                                                     "planned", "missing_levels")} | {"verifications": r["verifications"]}
                         for r in wp["swr"].values()},
        "coverage": {k: coverage.get(k) for k in ("line_percent", "branch_percent", "line_total", "branch_total")},
        "static": {"cppcheck": findings, "open": ev["open_findings"], "misra_total": ev["misra_total"],
                   "complexity_over_limit": [f for f in functions if f["ccn"] > CCN_LIMIT]},
        "unit_tests": unit_results,
        "integration": [{k: c[k] for k in ("ID", "Check", "Verifies", "status")} for c in wp["itc"]],
        "qualification": [{k: c.get(k) for k in ("ID", "Source", "Verifies", "status", "detail")} for c in wp["qtc"]],
        "trace_issues": ev["issues"],
    }
    (REPORT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    counts = Counter(r["status"] for r in wp["swr"].values())
    print(json.dumps({"report": str(REPORT / "aspice-swe-report.html"), "requirements": dict(counts),
                      "coverage": [coverage.get("line_percent"), coverage.get("branch_percent")],
                      "open_static_findings": len(ev["open_findings"]), "trace_issues": ev["issues"]}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
