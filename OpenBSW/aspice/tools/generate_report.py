#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate the ASPICE SWE.1-SWE.6 evidence report for the OpenBSW zonal diagnostic gateway.

Parses the work products in OpenBSW/aspice, runs the unit and static verification
(including the upstream OpenBSW gates for the contributed transportRouter module), loads the
recorded SWE.5 integration results, computes the SWE.6 automated qualification checks and
the bidirectional traceability, and writes:

    report/aspice-swe-report.html   report/summary.json   report/evidence/*

Run from the repository root:  python3 OpenBSW/aspice/tools/generate_report.py
Requires the SIL workspace on the build volume (OpenBSW/scripts/bootstrap.sh), java for
PlantUML, cppcheck, clang-tidy, and the PR tools (OpenBSW/scripts/openbsw-pr.sh tools).
Use --skip-upstream to reuse the last upstream gate run instead of re-running it.
"""

from __future__ import annotations

import argparse
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
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ASPICE = Path(__file__).resolve().parents[1]
OBSW = ASPICE.parent
REPO = OBSW.parent
REPORT = ASPICE / "report"
EVIDENCE = REPORT / "evidence"
IT_EVIDENCE = OBSW / "evidence" / "gateway-it"
SIL_EVIDENCE = OBSW / "evidence" / "sil-baseline"
BOARD_IT_EVIDENCE = OBSW / "evidence" / "board-gateway-it"
BOARD_BASELINE = OBSW / "evidence" / "board-baseline"
# gateway RTOS, same switch and defaults as the scripts: FreeRTOS for the POSIX simulation
# (OP-8), ThreadX on the S32K148EVB; ZGW_RTOS overrides both
RTOS = os.environ.get("ZGW_RTOS", "FREERTOS")
BOARD_RTOS = os.environ.get("ZGW_RTOS", "THREADX")
ARM_TOOLCHAIN = "arm-gnu-toolchain-14.3.rel1-x86_64-arm-none-eabi"
POSIX_HEADERS = re.compile(r"#\s*include\s*<(unistd|pthread|signal|termios|poll|fcntl|sys/[\w/]+|net/[\w/]+|netinet/[\w/]+|arpa/[\w/]+)\.h>")
PLANTUML_VERSION = "1.2024.7"
PLANTUML_SHA1 = "cb57b315d96413d55622edaa8c4b234e2ebf4b1f"
PLANTUML_JAR = REPO / "X-Verse" / ".cache" / "tools" / f"plantuml-{PLANTUML_VERSION}.jar"
CCN_LIMIT, CCN_JUSTIFIED_LIMIT = 15, 25
BITRATE = 500_000

MODULE_SRC = OBSW / "contrib" / "libs" / "bsw" / "transportRouter" / "src"
DOIP_CLIENT_SRC = OBSW / "contrib" / "libs" / "bsw" / "doipClient" / "src"
DOIP_CLIENT_EVIDENCE = OBSW / "evidence" / "doip-client-ut"
GATEWAY_LIB_SRC = OBSW / "gateway" / "lib" / "src"
APP = OBSW / "gateway" / "app" / "application" / "src"
GATEWAY_APP_SOURCES = [APP / "uds" / "GatewayDiagJobs.cpp", APP / "systems" / "TransportSystem.cpp",
                       APP / "systems" / "DoCanSystem.cpp", APP / "systems" / "UdsSystem.cpp",
                       APP / "uds" / "DemoDtcManager.cpp", APP / "app" / "app.cpp",
                       APP / "systems" / "DoIpClientSystem.cpp"]
GENERATOR = OBSW / "gateway" / "tools" / "gen_routing.py"


def run(cmd, cwd=REPO, check=True, timeout=1800, env=None):
    result = subprocess.run([str(c) for c in cmd], cwd=cwd, capture_output=True, text=True,
                            timeout=timeout, env=env)
    if check and result.returncode:
        raise RuntimeError(f"{' '.join(map(str, cmd))} failed:\n{result.stdout[-3000:]}\n{result.stderr[-3000:]}")
    return result


def sha256(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def workspace() -> dict:
    out = run(["bash", "-c", "source OpenBSW/scripts/storage.sh >/dev/null && "
               "echo $OBSW_WORKSPACE; echo $OBSW_SRC; echo $OBSW_VENV"]).stdout.split()
    return {"workspace": Path(out[0]), "openbsw": Path(out[1]), "venv": Path(out[2])}


def rel(path) -> str:
    return Path(path).resolve().relative_to(REPO).as_posix() if str(path).startswith(str(REPO)) else str(path)


# --------------------------------------------------------------------------------------------
# Work product parsing (same table conventions as the AZ3166 and Serial2CAN reports)
# --------------------------------------------------------------------------------------------
def md_tables(text):
    tables, lines, index = [], text.splitlines(), 0
    while index < len(lines) - 1:
        if lines[index].startswith("|") and re.match(r"^\|\s*:?-{3,}", lines[index + 1]):
            header = [cell.strip() for cell in lines[index].strip("|").split("|")]
            rows, index = [], index + 2
            while index < len(lines) and lines[index].startswith("|"):
                cells = [cell.strip() for cell in re.split(r"(?<!\\)\|", lines[index].strip().strip("|"))]
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
            statement.append(line.rstrip())
        attributes = {}
        for rows in md_tables(body):
            for row in rows:
                if "Attribute" in row:
                    attributes[row["Attribute"]] = row.get("Value", "")
        before = text[: text.index("### " + heading)]
        sections = re.findall(r"^## (.+)$", before, flags=re.M)
        items[match.group(1)] = {"id": match.group(1), "title": match.group(2),
                                 "text": "\n".join(s for s in statement if s),
                                 "section": sections[-1] if sections else "",
                                 **{k.lower().replace(" ", "_"): v for k, v in attributes.items()}}
    return items


def load_work_products():
    arch = (ASPICE / "swe2-architecture" / "architecture.md").read_text()
    dd = (ASPICE / "swe3-detailed-design" / "detailed-design.md").read_text()
    cg = (ASPICE / "swe3-detailed-design" / "coding-guidelines.md").read_text()
    return dict(
        sys=parse_requirements(ASPICE / "swe1-requirements" / "system-requirements.md", "SYS"),
        swr=parse_requirements(ASPICE / "swe1-requirements" / "software-requirements.md", "SWR"),
        elements=table_with(arch, "Satisfies"), interfaces=table_with(arch, "Provider → consumer"),
        decisions=table_with(arch, "Decision"), units=table_with(dd, "Implements"),
        guidelines=table_with(cg, "Rule"), deviations=table_with(cg, "Justification"),
        utc=table_with((ASPICE / "swe4-unit-verification" / "unit-verification.md").read_text(), "Executable"),
        itc=table_with((ASPICE / "swe5-integration-test" / "integration-test.md").read_text(), "Interfaces"),
        qtc=table_with((ASPICE / "swe6-qualification-test" / "qualification-test.md").read_text(), "Method"))


# --------------------------------------------------------------------------------------------
# Tool execution
# --------------------------------------------------------------------------------------------
def render_diagrams():
    if not PLANTUML_JAR.exists():
        raise RuntimeError(f"PlantUML jar missing: {PLANTUML_JAR} (run the Serial2CAN report once)")
    digest = hashlib.sha1(PLANTUML_JAR.read_bytes()).hexdigest()
    if digest != PLANTUML_SHA1:
        raise RuntimeError(f"PlantUML jar SHA-1 mismatch: {digest}")
    out = REPORT / "diagrams"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    sources = sorted(ASPICE.glob("swe*/diagrams/*.puml"))
    run(["java", "-Djava.awt.headless=true", "-jar", PLANTUML_JAR, "-tsvg", "-o", out] + sources, timeout=600)
    return {s.stem: {"svg": re.sub(r"<\?xml[^>]*\?>", "", (out / f"{s.stem}.svg").read_text()),
                     "source": rel(s), "process": s.parts[-3].split("-")[0].upper().replace("SWE", "SWE.")}
            for s in sources}


def junit_cases(path, name_attr="name", class_prefix=False):
    """{test name: status} from a JUnit file (gtest, ctest or pytest flavour)."""
    cases = {}
    for case in ET.parse(path).getroot().iter("testcase"):
        name = case.get(name_attr) or ""
        if class_prefix and case.get("classname"):
            name = f"{case.get('classname').split('.')[-1]}.{name}"
        failed = case.find("failure") is not None or case.find("error") is not None
        skipped = case.find("skipped") is not None or case.get("status") == "notrun"
        cases[name] = "failed" if failed else "skipped" if skipped else "passed"
    return cases


def upstream_gates(ws, skip):
    """The contributed module in the pinned OpenBSW: format, copyright, unit tests, tidy, Bazel."""
    run_dir = ws["workspace"] / "runs" / "report-upstream"
    if not skip:
        shutil.rmtree(run_dir, ignore_errors=True)
        env = dict(os.environ, RUN=str(run_dir))
        script = OBSW / "scripts" / "openbsw-pr.sh"
        steps = {}
        for step in ("sync", "format", "copyright", "test", "tidy", "bazel"):
            result = run(["bash", script, step], check=False, env=env, timeout=3600)
            steps[step] = "passed" if result.returncode == 0 else "failed"
            (run_dir / f"{step}.out").write_text(result.stdout + result.stderr)
        (run_dir / "steps.json").write_text(json.dumps(steps, indent=2))
    steps = json.loads((run_dir / "steps.json").read_text())
    cases = junit_cases(run_dir / "junit.xml")
    coverage = json.loads((run_dir / "coverage-summary.json").read_text())
    tidy = (run_dir / "clang-tidy.txt").read_text()
    bazel = (run_dir / "bazel-test.txt").read_text()
    for name in ("junit.xml", "coverage-summary.json", "clang-tidy.txt", "bazel-test.txt", "treefmt.txt",
                 "copyright.txt", "ctest.txt", "build-warnings.txt"):
        if (run_dir / name).exists():
            shutil.copy2(run_dir / name, EVIDENCE / f"module-{name}")
    shutil.rmtree(REPORT / "coverage-module", ignore_errors=True)
    (REPORT / "coverage-module").mkdir()
    for page in run_dir.glob("coverage*.html"):
        shutil.copy2(page, REPORT / "coverage-module" / ("index.html" if page.name == "coverage.html" else page.name))
    tidy_findings = int(re.search(r"clang-tidy findings in module: (\d+)", tidy).group(1)) if "findings in module" in tidy else -1
    return {"steps": steps, "cases": cases, "coverage": coverage, "tidy_findings": tidy_findings,
            "bazel": re.findall(r"^(//\S+)\s+(?:\(cached\)\s+)?(PASSED|FAILED)", bazel, flags=re.M),
            "build_warnings": int((run_dir / "build-warnings.txt").read_text().strip() or 0)
            if (run_dir / "build-warnings.txt").exists() else -1}


def doip_client_gates(skip):
    """The contributed DoIP client module in the pinned OpenBSW: format, unit tests, coverage, tidy."""
    if not skip:
        result = run(["bash", OBSW / "scripts" / "doip-client-test.sh"], check=False, timeout=3600)
        (EVIDENCE / "doipclient-run.txt").write_text(result.stdout + result.stderr)
    ev = DOIP_CLIENT_EVIDENCE
    tidy = (ev / "clang-tidy.txt").read_text()
    for name in ("junit.xml", "coverage.txt", "coverage-summary.json", "clang-tidy.txt", "treefmt.txt", "ctest.txt"):
        shutil.copy2(ev / name, EVIDENCE / f"doipclient-{name}")
    warnings = (ev / "build-warnings.txt").read_text().strip() if (ev / "build-warnings.txt").exists() else "0"
    return {"cases": junit_cases(ev / "junit.xml"),
            "coverage": json.loads((ev / "coverage-summary.json").read_text()),
            "tidy_findings": int(re.search(r"clang-tidy findings in module: (\d+)", tidy).group(1)),
            "format_clean": "format: clean" in (ev / "treefmt.txt").read_text(),
            "base": (ev / "openbsw-base.txt").read_text().strip(),
            "build_warnings": int(warnings or 0)}


def gateway_unit_tests(ws):
    build = ws["workspace"] / "build" / "gateway-ut"
    venv_bin = ws["venv"] / "bin"
    env = dict(os.environ, PATH=f"{venv_bin}:{os.environ['PATH']}")
    run(["cmake", "-S", OBSW / "gateway", "-B", build, "-G", "Ninja", f"-DOPENBSW_DIR={ws['openbsw']}",
         f"-DBUILD_TARGET_RTOS={RTOS}", "-DCMAKE_BUILD_TYPE=Debug", "-DZGW_UNIT_TESTS=ON", "-DCMAKE_EXPORT_COMPILE_COMMANDS=ON"], env=env)
    for gcda in build.rglob("*.gcda"):
        gcda.unlink()
    run(["cmake", "--build", build, "--target", "gatewayUnitTest"], env=env)
    xml = EVIDENCE / "gateway-ut.xml"
    run([build / "lib" / "gatewayUnitTest", f"--gtest_output=xml:{xml}"], check=False)
    cases = junit_cases(xml, class_prefix=True)
    run([venv_bin / "gcovr", "-r", OBSW, "--filter", GATEWAY_LIB_SRC, "--filter", APP / "uds" / "DemoDtcManager.cpp",
         "--exclude-throw-branches", "--exclude-unreachable-branches",
         "--json-summary-pretty", "--json-summary", EVIDENCE / "gateway-coverage.json", build], env=env)
    return cases, json.loads((EVIDENCE / "gateway-coverage.json").read_text()), build


def generator_tests(ws):
    py = ws["venv"] / "bin" / "python"
    tools = GENERATOR.parent
    data = EVIDENCE / ".coverage-generator"
    env = dict(os.environ, COVERAGE_FILE=str(data))
    env.pop("PYTHONPATH", None)
    run([py, "-m", "coverage", "run", "--branch", f"--include={GENERATOR}", "-m", "pytest", "-q", "-p",
         "no:cacheprovider", f"--junitxml={EVIDENCE / 'generator-ut.xml'}", "test_gen_routing.py"],
        cwd=tools, check=False, env=env)
    run([py, "-m", "coverage", "json", "-o", EVIDENCE / "generator-coverage.json"], cwd=tools, env=env)
    data.unlink(missing_ok=True)
    cases = {f"test_gen_routing.py::{n}": s for n, s in junit_cases(EVIDENCE / "generator-ut.xml").items()}
    totals = json.loads((EVIDENCE / "generator-coverage.json").read_text())["totals"]
    return cases, totals


def static_analysis(ws, ut_build):
    sources = [MODULE_SRC, DOIP_CLIENT_SRC, GATEWAY_LIB_SRC] + GATEWAY_APP_SOURCES
    includes = ["-I", OBSW / "contrib/libs/bsw/transportRouter/include", "-I", OBSW / "contrib/libs/bsw/doipClient/include",
                "-I", OBSW / "gateway/lib/include",
                "-I", OBSW / "gateway/app/application/include"]
    cpp = run(["cppcheck", "--enable=warning,style,performance,portability", "--std=c++17", "--inline-suppr",
               "--quiet", "--suppress=missingIncludeSystem", "-DDECLARE_LOGGER_COMPONENT(x)=",
               "-DDEFINE_LOGGER_COMPONENT(x)=", "--template={file}|{line}|{severity}|{id}|{message}"]
              + includes + sources, check=False)
    (EVIDENCE / "cppcheck.txt").write_text(cpp.stderr)
    findings = [dict(zip(("file", "line", "severity", "id", "message"), line.split("|", 4)))
                for line in cpp.stderr.splitlines() if line.count("|") >= 4]
    tidy_sources = sorted(GATEWAY_LIB_SRC.rglob("*.cpp"))
    tidy = run(["clang-tidy", "-p", ut_build, "--quiet"] + tidy_sources, check=False)
    (EVIDENCE / "clang-tidy-gateway.txt").write_text(tidy.stdout + tidy.stderr)
    gateway_tidy = re.findall(r"^(\S+?):(\d+):\d+: (?:warning|error): (.*) \[([\w.,-]+)\]$",
                              re.sub(r"\x1b\[[0-9;]*m", "", tidy.stdout), flags=re.M)
    lizard = run([ws["venv"] / "bin" / "lizard", "--csv"] + sources + [GENERATOR], check=False)
    (EVIDENCE / "complexity.csv").write_text(lizard.stdout)
    functions = [{"nloc": int(r[0]), "ccn": int(r[1]), "function": r[7], "file": rel(r[6])}
                 for r in csv.reader(io.StringIO(lizard.stdout)) if len(r) >= 8 and r[1].isdigit()]
    return findings, gateway_tidy, functions


def build_checks(ws):
    elf = ws["workspace"] / "build" / "gateway-ut" / "app" / "application" / "openbsw-zonal-gw.elf"
    release = ws["workspace"] / "build" / "gateway"
    venv_bin = ws["venv"] / "bin"
    env = dict(os.environ, PATH=f"{venv_bin}:{os.environ['PATH']}")
    run(["cmake", "-S", OBSW / "gateway", "-B", release, "-G", "Ninja", f"-DOPENBSW_DIR={ws['openbsw']}",
         f"-DBUILD_TARGET_RTOS={RTOS}", "-DCMAKE_BUILD_TYPE=Release"], env=env)
    (release / "app/application/openbsw-zonal-gw.elf").unlink(missing_ok=True)
    build = run(["cmake", "--build", release, "--target", "openbsw-zonal-gw"], check=False, env=env)
    log = build.stdout + build.stderr
    (EVIDENCE / "gateway-build.log").write_text(log)
    elf = release / "app" / "application" / "openbsw-zonal-gw.elf"
    symbols = run(["nm", "-C", elf]).stdout
    middleware = sorted({m.group(0).lower() for m in re.finditer(r"someip|zenoh|middleware::", symbols, re.I)})
    lock = json.loads((OBSW / "dependencies.lock.json").read_text())["openbsw"]["revision"]
    head = run(["git", "-C", ws["openbsw"], "rev-parse", "HEAD"]).stdout.strip()
    clean = run(["git", "-C", ws["openbsw"], "status", "--porcelain", "--untracked-files=no"]).stdout.strip() == ""
    forbidden = []
    for source in [*MODULE_SRC.rglob("*.cpp"), *DOIP_CLIENT_SRC.rglob("*.cpp"), *GATEWAY_LIB_SRC.rglob("*.cpp"),
                   *GATEWAY_APP_SOURCES]:
        for number, line in enumerate(source.read_text().splitlines(), 1):
            code = line.split("//")[0]
            if re.search(r"\bnew\b|\bmalloc\s*\(|\bthrow\b|\bdynamic_cast\b", code):
                forbidden.append(f"{rel(source)}:{number}: {line.strip()}")
    derived = []
    for source in (OBSW / "gateway" / "app").rglob("*.[ch]*"):
        text = source.read_text(errors="replace")
        if "Modified for the zonal diagnostic gateway" in text and "Accenture" not in text and "An Dao" not in text:
            derived.append(rel(source))
    # the gateway work starts with the commit that added OpenBSW/; diff against its parent
    first = run(["git", "log", "--diff-filter=A", "--format=%H", "--", "OpenBSW/README.md"]).stdout.split()
    base = f"{first[-1]}^" if first else "main"
    branch = run(["git", "diff", "--name-only", f"{base}...HEAD"], check=False).stdout.split()
    work = [line[3:] for line in run(["git", "status", "--porcelain"]).stdout.splitlines()]
    outside = sorted({p for p in branch + work if not (p.startswith("OpenBSW/") or p.startswith("contributions/"))})
    return {"build_ok": build.returncode == 0, "warnings": len(re.findall(r"warning:", log)),
            "elf_sha256": sha256(elf), "elf_bytes": elf.stat().st_size, "middleware_symbols": middleware,
            "openbsw_lock": lock, "openbsw_head": head, "openbsw_clean": clean, "forbidden": forbidden,
            "derived_without_origin": derived, "outside_paths": outside}


def board_checks(ws):
    """Build the gateway for the S32K148EVB and read its memory regions (SWR-051)."""
    build = ws["workspace"] / "build" / f"gateway-s32k148-{BOARD_RTOS.lower()}"
    arm = ws["workspace"] / "tools" / ARM_TOOLCHAIN / "bin"
    if not (arm / "arm-none-eabi-gcc").exists():
        return {"available": False}
    env = dict(os.environ, PATH=f"{arm}:{ws['venv'] / 'bin'}:{os.environ['PATH']}",
               CC="arm-none-eabi-gcc", CXX="arm-none-eabi-g++")
    if not (build / "build.ninja").exists():
        run(["cmake", "-S", OBSW / "gateway", "-B", build, "-G", "Ninja", f"-DOPENBSW_DIR={ws['openbsw']}",
             "-DBUILD_TARGET_PLATFORM=S32K148EVB", f"-DBUILD_TARGET_RTOS={BOARD_RTOS}",
             f"-DCMAKE_TOOLCHAIN_FILE={ws['openbsw'] / 'cmake' / 'toolchains' / 'ArmNoneEabi.cmake'}",
             "-DCMAKE_BUILD_TYPE=RelWithDebInfo", "-DCMAKE_C_FLAGS_RELWITHDEBINFO=-g3 -O2 -DNDEBUG",
             "-DCMAKE_CXX_FLAGS_RELWITHDEBINFO=-g3 -O2 -DNDEBUG", "-DCMAKE_ASM_FLAGS_RELWITHDEBINFO=-g3"], env=env)
    elf = build / "app" / "application" / "openbsw-zonal-gw.elf"
    elf.unlink(missing_ok=True)  # relink to get the memory region table
    result = run(["cmake", "--build", build], check=False, env=env)
    log = result.stdout + result.stderr
    (EVIDENCE / "board-build.log").write_text(log)
    regions = {m.group(1): {"used": int(m.group(2)), "percent": float(m.group(3))}
               for m in re.finditer(r"^\s*(\w+):\s+(\d+) B\s+\S+ \w+\s+([\d.]+)%", log, flags=re.M)}
    for m in re.finditer(r"^\s*(\w+):\s+([\d.]+) KB\s+\S+ \w+\s+([\d.]+)%", log, flags=re.M):
        regions.setdefault(m.group(1), {"used": int(float(m.group(2)) * 1024), "percent": float(m.group(3))})
    # warnings that the reference app shares (newlib syscall stubs, RWX segment) are not counted
    own = [w for w in re.findall(r"warning: .*", log) if "is not implemented and will always fail" not in w
           and "RWX permissions" not in w]
    headers = []
    roots = [OBSW / "gateway" / "app" / "application", OBSW / "gateway" / "lib", OBSW / "contrib"]
    for root in roots:
        for source in [*root.rglob("*.cpp"), *root.rglob("*.h")]:
            for number, line in enumerate(source.read_text(errors="replace").splitlines(), 1):
                if POSIX_HEADERS.search(line):
                    headers.append(f"{rel(source)}:{number}: {line.strip()}")
    return {"available": True, "rtos": BOARD_RTOS, "build_ok": result.returncode == 0 and elf.exists(),
            "elf_sha256": sha256(elf) if elf.exists() else None, "regions": regions,
            "own_warnings": own, "posix_headers": headers}


# --------------------------------------------------------------------------------------------
# Qualification analyses
# --------------------------------------------------------------------------------------------
def frame_bits(dlc=8):
    payload = 8 * dlc
    return 47 + payload + (34 + payload - 1) // 4


def bus_load(it):
    sys.path.insert(0, str(GENERATOR.parent))
    import gen_routing  # noqa: PLC0415
    cfg = gen_routing.validate(gen_routing.load(OBSW / "gateway" / "config" / "routing.yaml"))
    # worst case: the largest requests of all CAN routes at once, STmin 0 granted by the ECUs;
    # the gateway's pacing (can_tx_min_gap_us) caps the frames it sends in any 1 s window
    can_routes = [r for r in cfg["routes"] if r["transport"] == "docan"]
    frames = sum(gen_routing.isotp_frames(r["max_length"]) for r in can_routes)
    cap = 1 + (1_000_000 - 1) // cfg["can_tx_min_gap_us"]
    worst = 100 * min(frames, cap) * frame_bits() / BITRATE
    measured = it["can_load"]["gateway_tx"]["peak_percent"] if it else None
    return cfg, {"worst_frames": min(frames, cap), "requested_frames": frames, "gap_us": cfg["can_tx_min_gap_us"],
                 "worst_percent": round(worst, 2), "measured_percent": measured}


def qualification(wp, ws, upstream, checks, it, board, board_it, doip):
    cfg, load = bus_load(it)
    profiles = sorted((REPO / "X-Verse" / "bridges" / "serial2can" / "config").glob("*.json"))
    import gen_routing  # noqa: PLC0415
    problems = [p for prof in profiles for p in gen_routing.check_profile(cfg, prof)]
    sil = json.loads((SIL_EVIDENCE / "manifest.json").read_text())
    logs = "".join(p.read_text(errors="replace") for p in IT_EVIDENCE.glob("*-gateway.log"))
    latency = it.get("latency_ms", {}) if it else {}
    gates_ok = all(v == "passed" for v in upstream["steps"].values()) and upstream["bazel"] \
        and all(s == "PASSED" for _, s in upstream["bazel"])
    auto = {
        "sil-baseline": (sil["result"]["tests"] == 104 and sil["result"]["failures"] == 0 and sil["result"]["errors"] == 0
                         and sil["openbsw_revision"] == checks["openbsw_lock"],
                         f"{sil['result']['tests'] - sil['result']['failures'] - sil['result']['errors']}/{sil['result']['tests']} "
                         f"passed, {sil['preset'].split()[0]} at {sil['openbsw_revision'][:12]}"),
        "upstream-gates": (gates_ok, ", ".join(f"{k} {v}" for k, v in upstream["steps"].items())
                           + f"; bazel {sum(s == 'PASSED' for _, s in upstream['bazel'])}/{len(upstream['bazel'])}"),
        "openbsw-pinned": (checks["openbsw_head"] == checks["openbsw_lock"] and checks["openbsw_clean"],
                           f"lock {checks['openbsw_lock'][:12]}, checkout {checks['openbsw_head'][:12]}, clean={checks['openbsw_clean']}"),
        "no-vehicle-middleware": (not checks["middleware_symbols"],
                                  "no SOME/IP, Zenoh or middleware symbols" if not checks["middleware_symbols"]
                                  else f"found: {checks['middleware_symbols']}"),
        "no-dynamic-memory": (not checks["forbidden"], "none found" if not checks["forbidden"]
                              else "; ".join(checks["forbidden"][:4])),
        "bus-load": (load["worst_percent"] <= 10 and (load["measured_percent"] or 0) <= 10,
                     f"worst case {load['worst_percent']} % ({load['worst_frames']} of {load['requested_frames']} "
                     f"frames of {max(r['max_length'] for r in cfg['routes'])}-byte requests on every CAN route "
                     f"in 1 s, STmin 0, paced at {load['gap_us']} us); measured peak {load['measured_percent']} %"),
        "configuration-consistency": (not problems, f"{len(profiles)} Serial2CAN profiles consistent" if not problems
                                      else "; ".join(problems)),
        "latency": (bool(latency) and latency.get("down_p95_ms", 99) <= 10 and latency.get("up_p95_ms", 99) <= 10,
                    f"p95 DoIP→CAN {latency.get('down_p95_ms')} ms, CAN→DoIP {latency.get('up_p95_ms')} ms "
                    f"({latency.get('samples')} samples)"),
        "observability": (f"routing table {cfg['hash']}" in logs and "stats local=" in logs,
                          f"start-up hash {cfg['hash']} {'found' if f'routing table {cfg['hash']}' in logs else 'missing'}; "
                          f"statistics line {'found' if 'stats local=' in logs else 'missing'}"),
        "baseline-untouched": (not checks["outside_paths"], "only OpenBSW/ and contributions/ changed"
                               if not checks["outside_paths"] else f"outside: {checks['outside_paths']}"),
    }
    if board.get("available"):
        app_region, ram = board["regions"].get("Application", {}), board["regions"].get("MainRAM", {})
        board_current = bool(board_it) and board_it.get("executable_sha256") == board["elf_sha256"]
        auto["target-build"] = (
            board["build_ok"] and not board["posix_headers"] and not board["own_warnings"]
            and 0 < app_region.get("percent", 101) < 100 and 0 < ram.get("percent", 101) < 100 and board_current,
            f"{board['rtos']}: flash {app_region.get('used')} B ({app_region.get('percent')} %), MainRAM {ram.get('used')} B "
            f"({ram.get('percent')} %); POSIX headers outside platforms/posix: {len(board['posix_headers'])}; "
            f"recorded board run {'uses' if board_current else 'does not use'} the current image")
    else:
        auto["target-build"] = (False, "Arm GNU Toolchain 14.3.rel1 not found on the build volume")
    base = json.loads((BOARD_BASELINE / "manifest.json").read_text()) if (BOARD_BASELINE / "manifest.json").exists() else None
    auto["board-baseline"] = (
        bool(base) and base["result"]["failures"] == 0 and base["result"]["errors"] == 0 and base["result"]["tests"] > 0
        and base["openbsw_revision"] == checks["openbsw_lock"],
        f"{base['result']['tests'] - base['result']['failures']}/{base['result']['tests']} on {base['target']}, "
        f"{base['preset'].split()[0]} "
        f"at {base['openbsw_revision'][:12]}" if base else "no board baseline recorded")
    doip_pc = [t for t in (it or {}).get("tests", []) if t["name"].startswith("test_doip_")]
    doip_board = [t for t in (board_it or {}).get("tests", []) if t["name"].startswith("test_board_doip_")]
    pc_current = bool(it) and it.get("executable_sha256") == checks["elf_sha256"]
    board_now = bool(board_it) and board.get("available") and board_it.get("executable_sha256") == board.get("elf_sha256")
    auto["doip-routing"] = (
        bool(doip_pc) and bool(doip_board) and pc_current and board_now
        and all(t["status"] == "passed" for t in doip_pc + doip_board),
        f"Linux {sum(t['status'] == 'passed' for t in doip_pc)}/{len(doip_pc)} "
        f"({'current' if pc_current else 'stale'} executable), S32K148EVB "
        f"{sum(t['status'] == 'passed' for t in doip_board)}/{len(doip_board)} "
        f"({'current' if board_now else 'stale'} image)")
    doip_cases = doip["cases"]
    doip_lines = doip["coverage"]["line_percent"]
    auto["doip-client-gates"] = (
        doip["format_clean"] and bool(doip_cases) and all(v == "passed" for v in doip_cases.values())
        and doip_lines >= 90 and doip["tidy_findings"] == 0 and doip["base"] == checks["openbsw_lock"],
        f"format {'clean' if doip['format_clean'] else 'changed'}; unit tests "
        f"{sum(v == 'passed' for v in doip_cases.values())}/{len(doip_cases)}; lines {doip_lines:.1f} %; "
        f"clang-tidy {doip['tidy_findings']}; base {doip['base'][:12]}")
    manual = {"reviewed": ("passed", "Review recorded in the case description"),
              "not-run": ("not run", "Live campaign not executed in this slice"),
              "open": ("open", "Depends on an open item")}
    for case in wp["qtc"]:
        kind, _, key = case["Source"].partition(":")
        if kind == "auto":
            ok, detail = auto[key]
            case["status"], case["detail"] = ("passed" if ok else "failed"), detail
        else:
            case["status"], case["detail"] = manual[key]
    return load, problems


# --------------------------------------------------------------------------------------------
# Evaluation and traceability
# --------------------------------------------------------------------------------------------
def match_cases(pattern_list, cases):
    statuses = []
    for pattern in pattern_list.replace("`", "").split():
        regex = re.compile("^" + re.escape(pattern).replace(r"\*", ".*") + "$")
        found = [s for n, s in cases.items() if regex.match(n)]
        statuses += found if found else ["missing"]
    if not statuses or "missing" in statuses:
        return "missing"
    return "passed" if all(s == "passed" for s in statuses) else "failed"


def evaluate(wp, unit_cases, it, built, findings, gateway_tidy, functions, upstream, board, board_it):
    verifications = {req: [] for req in wp["swr"]}

    def add(level, case_id, verifies, status, detail=""):
        for req in ids(verifies, "SWR"):
            verifications.setdefault(req, []).append({"level": level, "case": case_id, "status": status, "detail": detail})

    for case in wp["utc"]:
        case["status"] = match_cases(case["Executable"], unit_cases)
        add("UT", case["ID"], case["Verifies"], case["status"])
    it_tests = {t["name"]: t for t in (it or {}).get("tests", [])}
    board_tests = {t["name"]: t for t in (board_it or {}).get("tests", [])}
    it_current = bool(it) and it.get("executable_sha256") == built["elf_sha256"]
    board_current = bool(board_it) and board.get("available") and board_it.get("executable_sha256") == board.get("elf_sha256")
    for case in wp["itc"]:
        on_board = case["Check"].startswith("board:")
        name = case["Check"].split(":", 1)[1] if on_board else case["Check"]
        test = (board_tests if on_board else it_tests).get(name)
        status = test["status"] if test else "missing"
        if status == "passed" and not (board_current if on_board else it_current):
            status = "failed"
        case["status"], case["detail"] = status, (f"{test['duration_s']:.2f} s" if test else "not recorded")
        add("IT", case["ID"], case["Verifies"], status)
    for case in wp["qtc"]:
        level = {"Test": "QT", "Analysis": "AN", "Inspection": "RV"}[case["Method"]]
        add(level, case["ID"], case["Verifies"], case["status"], case["Source"])

    justified = {row["ID"] for row in wp["deviations"]}
    for f in findings:
        f["file"] = rel(f["file"])
        f["deviation"] = "DEV-02" if f["id"] == "useStlAlgorithm" and "DEV-02" in justified else None
    open_findings = [f for f in findings if not f["deviation"]]
    for f in functions:
        if f["ccn"] <= CCN_LIMIT:
            f["status"] = "ok"
        elif f["ccn"] <= CCN_JUSTIFIED_LIMIT and "DEV-03" in justified:
            f["status"] = "justified (DEV-03)"
        else:
            f["status"] = "violation"

    allocation, units = {r: [] for r in wp["swr"]}, {r: [] for r in wp["swr"]}
    for element in wp["elements"]:
        for req in ids(element["Satisfies"], "SWR"):
            allocation.setdefault(req, []).append(element["ID"])
    for unit in wp["units"]:
        for req in ids(unit["Implements"], "SWR"):
            units.setdefault(req, []).append(unit["ID"])
    issues, sys_children = [], {sid: [] for sid in wp["sys"]}
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
        elif statuses & {"failed", "missing"}:
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
                   units=units.get(req["id"], []), planned=sorted(planned), missing_levels=sorted(planned - achieved))
        if not req["elements"]:
            issues.append(f"{req['id']} is not allocated to an architecture element")
        if not req["units"]:
            issues.append(f"{req['id']} is not implemented by a software unit")
    for sid, children in sys_children.items():
        if not children:
            issues.append(f"{sid} has no derived software requirement")
    known_elements = {e["ID"] for e in wp["elements"]}
    for unit in wp["units"]:
        for element in ids(unit["Element"], "ARC"):
            if element not in known_elements:
                issues.append(f"{unit['ID']} allocated to unknown {element}")
    for table in ("utc", "itc", "qtc", "elements", "units"):
        for row in wp[table]:
            for req in ids(row.get("Verifies") or row.get("Satisfies") or row.get("Implements"), "SWR"):
                if req not in wp["swr"]:
                    issues.append(f"{row['ID']} references unknown {req}")
    return {"open_findings": open_findings, "issues": issues, "sys_children": sys_children,
            "it_current": it_current, "board_current": board_current, "gateway_tidy": gateway_tidy}


# --------------------------------------------------------------------------------------------
# HTML rendering
# --------------------------------------------------------------------------------------------
def inline_md(text):
    text = html.escape(text or "")
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = text.replace("\\*", "*")
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", text)


def statement_html(text):
    blocks = []
    for line in (text or "").splitlines():
        if line.startswith("- "):
            if not blocks or blocks[-1][0] != "list":
                blocks.append(("list", []))
            blocks[-1][1].append(line[2:])
        elif line.startswith(" ") and blocks and blocks[-1][0] == "list":
            blocks[-1][1][-1] += " " + line.strip()
        elif blocks and blocks[-1][0] == "prose":
            blocks[-1][1].append(line.strip())
        else:
            blocks.append(("prose", [line.strip()]))
    return "".join(inline_md(" ".join(items)) if kind == "prose" else
                   "<ul>" + "".join(f"<li>{inline_md(i)}</li>" for i in items) + "</ul>" for kind, items in blocks)


def badge(status):
    cls = {"passed": "ok", "verified": "ok", "ok": "ok", "failed": "bad", "violation": "bad", "missing": "bad",
           "partially verified": "warn", "open": "warn", "not run": "warn", "not verified": "bad"}.get(
        status, "warn" if "justified" in status else "neutral")
    return f'<span class="badge {cls}">{html.escape(status)}</span>'


def table(headers, rows):
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for row in rows)
    return f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'


def link(path, label=None):
    return f'<a href="{html.escape((Path("../../..") / path).as_posix())}">{html.escape(label or Path(path).name)}</a>'


CSS = """:root{--bg:#f6f7f9;--panel:#fff;--ink:#1d2330;--muted:#5d6675;--line:#e3e6eb;--accent:#2a5bd7;--ok:#1f7a4d;--ok-bg:#e3f4ea;--warn:#8a5a00;--warn-bg:#fdf1d8;--bad:#a62b2b;--bad-bg:#fbe5e5;--neutral-bg:#eceef2;--code:#eef1f6}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#12151b;--panel:#1a1f27;--ink:#e6e9ee;--muted:#9aa3b2;--line:#2b323d;--accent:#7aa2ff;--ok:#6fd39f;--ok-bg:#16301f;--warn:#f0c46b;--warn-bg:#33290f;--bad:#ff8f8f;--bad-bg:#3a1a1a;--neutral-bg:#262c36;--code:#232a35}}
:root[data-theme="dark"]{--bg:#12151b;--panel:#1a1f27;--ink:#e6e9ee;--muted:#9aa3b2;--line:#2b323d;--accent:#7aa2ff;--ok:#6fd39f;--ok-bg:#16301f;--warn:#f0c46b;--warn-bg:#33290f;--bad:#ff8f8f;--bad-bg:#3a1a1a;--neutral-bg:#262c36;--code:#232a35}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
header{background:var(--panel);border-bottom:1px solid var(--line);padding:20px 24px}header h1{margin:0 0 4px;font-size:22px}header p{margin:0;color:var(--muted)}
.layout{display:grid;grid-template-columns:220px minmax(0,1fr);gap:24px;max-width:1440px;margin:0 auto;padding:16px}
nav{position:sticky;top:16px;align-self:start;display:flex;flex-direction:column;gap:2px}nav a{color:var(--ink);text-decoration:none;padding:6px 10px;border-radius:6px}nav a:hover{background:var(--neutral-bg)}
section{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px 22px;margin-bottom:20px}
h2{margin:0 0 6px;font-size:19px}h3{margin:20px 0 8px;font-size:15px}.lead{color:var(--muted);margin:0 0 14px}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}.kpi{border:1px solid var(--line);border-radius:8px;padding:12px}
.kpi-label{color:var(--muted);font-size:12px}.kpi-value{font-size:24px;font-weight:650;font-variant-numeric:tabular-nums}.kpi-sub{color:var(--muted);font-size:12px}
.table-wrap{overflow-x:auto;margin:8px 0}table{border-collapse:collapse;width:100%;font-size:13px}
th,td{text-align:left;vertical-align:top;padding:7px 9px;border-bottom:1px solid var(--line)}th{background:var(--neutral-bg);font-weight:600;white-space:nowrap}
code{background:var(--code);padding:1px 5px;border-radius:4px;font-size:12px;word-break:break-word}.muted{color:var(--muted)}
.id{font-family:ui-monospace,Menlo,monospace;font-weight:600;white-space:nowrap}
.badge{display:inline-block;padding:1px 8px;border-radius:999px;font-size:12px;font-weight:600;white-space:nowrap}
.badge.ok{background:var(--ok-bg);color:var(--ok)}.badge.warn{background:var(--warn-bg);color:var(--warn)}.badge.bad{background:var(--bad-bg);color:var(--bad)}.badge.neutral{background:var(--neutral-bg);color:var(--muted)}
.tc{font-family:ui-monospace,Menlo,monospace;font-size:12px;padding:0 4px;border-radius:4px;white-space:nowrap;display:inline-block;margin:1px 0}
.tc.ok{background:var(--ok-bg);color:var(--ok)}.tc.warn{background:var(--warn-bg);color:var(--warn)}.tc.bad{background:var(--bad-bg);color:var(--bad)}
.diagram{margin:14px 0;border:1px solid var(--line);border-radius:8px;overflow:hidden}.diagram .svg{background:#fff;overflow-x:auto;padding:8px}.diagram svg{max-width:100%;height:auto}
.diagram figcaption{padding:6px 10px;color:var(--muted);font-size:12px;border-top:1px solid var(--line)}
td ul{margin:4px 0;padding-left:18px}a{color:var(--accent)}
@media (max-width:860px){.layout{grid-template-columns:1fr;padding:16px}nav{position:static;flex-direction:row;flex-wrap:wrap}header{padding:16px}}"""


def render(wp, diagrams, ev, unit_cases, cov, built, findings, functions, upstream, it, load, tools, board, board_it,
           doip):
    swr = wp["swr"]
    counts = Counter(r["status"] for r in swr.values())
    m_cov, d_cov, g_cov, p_cov = cov["module"], cov["doip_client"], cov["gateway"], cov["generator"]
    ut_total = len(unit_cases)
    ut_pass = sum(s == "passed" for s in unit_cases.values())
    it_pass = sum(c["status"] == "passed" for c in wp["itc"])
    qt_pass = sum(c["status"] == "passed" for c in wp["qtc"])
    kpis = [
        ("Requirements verified", f"{counts['verified']}/{len(swr)}",
         f"{counts['partially verified']} partial · {counts['failed']} failed · {counts['open'] + counts['not verified']} open"),
        ("Unit tests", f"{ut_pass}/{ut_total}", f"{len(wp['utc'])} cases · gtest, Bazel, pytest"),
        ("Module coverage", f"{m_cov['line_percent']:.0f}% / {d_cov['line_percent']:.0f}%", "transportRouter / doipClient lines"),
        ("Gateway coverage", f"{g_cov['line_percent']:.0f}% / {g_cov['branch_percent']:.0f}%", "gateway units line / branch"),
        ("Static findings open", str(len(ev["open_findings"]) + len(ev["gateway_tidy"])),
         f"{len(findings)} cppcheck · {upstream['tidy_findings'] + doip['tidy_findings']} + {len(ev['gateway_tidy'])} clang-tidy"),
        ("Integration tests", f"{it_pass}/{len(wp['itc'])}",
         f"PC {'current' if ev['it_current'] else 'stale'} · S32K148 {'current' if ev['board_current'] else 'stale'}"),
        ("S32K148 image", f"{board.get('regions', {}).get('Application', {}).get('used', 0) / 1024:.0f} KiB",
         f"MainRAM {board.get('regions', {}).get('MainRAM', {}).get('percent', '—')} %"),
        ("Qualification", f"{qt_pass}/{len(wp['qtc'])}", f"{sum(c['status'] != 'passed' for c in wp['qtc'])} open / not run / failed"),
        ("Trace issues", str(len(ev["issues"])), "bidirectional consistency"),
    ]
    kpi_html = "".join(f'<div class="kpi"><div class="kpi-label">{a}</div><div class="kpi-value">{b}</div>'
                       f'<div class="kpi-sub">{c}</div></div>' for a, b, c in kpis)

    def diagram_block(names):
        return "".join(f'<figure class="diagram"><div class="svg">{diagrams[n]["svg"]}</div><figcaption>{html.escape(n)} — '
                       f'{link(diagrams[n]["source"], diagrams[n]["source"])}</figcaption></figure>' for n in names if n in diagrams)

    sys_rows = [[f'<span class="id">{s["id"]}</span>', inline_md(s["title"]), statement_html(s["text"]),
                 ", ".join(ev["sys_children"].get(s["id"], [])) or badge("not derived")] for s in wp["sys"].values()]
    req_rows = [[f'<span class="id" id="{r["id"]}">{r["id"]}</span>',
                 f'<strong>{inline_md(r["title"])}</strong><div class="muted">{statement_html(r["text"])}</div>',
                 html.escape(r.get("type", "")), ", ".join(r["parents"]), " ".join(r["planned"]),
                 inline_md(r.get("criterion", "")), badge(r["status"])] for r in swr.values()]
    trace_rows = []
    for r in swr.values():
        by_level = {}
        for v in r["verifications"]:
            cls = "ok" if v["status"] == "passed" else "warn" if v["status"] in ("open", "not run") else "bad"
            by_level.setdefault(v["level"], []).append(f'<span class="tc {cls}">{v["case"]}</span>')
        trace_rows.append([f'<a href="#{r["id"]}">{r["id"]}</a>', ", ".join(r["parents"]), ", ".join(r["elements"]),
                           ", ".join(r["units"])] + [" ".join(by_level.get(l, [])) or "—" for l in ("UT", "IT", "QT", "AN", "RV")]
                          + [badge(r["status"])])
    element_rows = [[f'<span class="id">{e["ID"]}</span>', inline_md(e["Element"]), inline_md(e["Responsibility"]), e["Satisfies"]]
                    for e in wp["elements"]]
    interface_rows = [[f'<span class="id">{i["ID"]}</span>', inline_md(i["Interface"]), inline_md(i["Provider → consumer"]),
                       inline_md(i["Type and contract"])] for i in wp["interfaces"]]
    decision_rows = [[f'<span class="id">{d["ID"]}</span>', inline_md(d["Decision"]), inline_md(d["Rationale"])] for d in wp["decisions"]]
    unit_rows = [[f'<span class="id">{u["ID"]}</span>', inline_md(u["Unit"]), inline_md(u["Source / functions"]), u["Element"], u["Implements"]]
                 for u in wp["units"]]
    guideline_rows = [[f'<span class="id">{g["ID"]}</span>', inline_md(g["Rule"]), inline_md(g["Check"])] for g in wp["guidelines"]]
    deviation_rows = [[f'<span class="id">{d["ID"]}</span>', inline_md(d["Tool / rule"]), inline_md(d["Location"]), inline_md(d["Justification"])]
                      for d in wp["deviations"]]
    finding_rows = [[html.escape(f'{f["file"]}:{f["line"]}'), html.escape(f["severity"]), f'<code>{html.escape(f["id"])}</code>',
                     html.escape(f["message"]), badge(f"justified ({f['deviation']})") if f["deviation"] else badge("open")]
                    for f in findings] or [["—", "—", "—", "No findings", badge("ok")]]
    complex_rows = [[html.escape(f["file"]), f'<code>{html.escape(f["function"])}</code>', f["nloc"], f["ccn"], badge(f["status"])]
                    for f in sorted(functions, key=lambda f: -f["ccn"]) if f["ccn"] > 10]
    utc_rows = [[f'<span class="id">{c["ID"]}</span>', inline_md(c["Test case"]), c["Unit"], c["Verifies"], badge(c["status"])] for c in wp["utc"]]
    cov_rows = [["transportRouter (contrib module)", f'{m_cov["line_covered"]}/{m_cov["line_total"]}', f'{m_cov["line_percent"]:.1f}%',
                 f'{m_cov["branch_covered"]}/{m_cov["branch_total"]}', f'{m_cov["branch_percent"]:.1f}%', '<a href="coverage-module/index.html">details</a>'],
                ["doipClient (contrib module)", f'{d_cov["line_covered"]}/{d_cov["line_total"]}', f'{d_cov["line_percent"]:.1f}%',
                 f'{d_cov["branch_covered"]}/{d_cov["branch_total"]}', f'{d_cov["branch_percent"]:.1f}%', '<a href="evidence/doipclient-coverage.txt">txt</a>'],
                ["gateway units (lib + DTC store)", f'{g_cov["line_covered"]}/{g_cov["line_total"]}', f'{g_cov["line_percent"]:.1f}%',
                 f'{g_cov["branch_covered"]}/{g_cov["branch_total"]}', f'{g_cov["branch_percent"]:.1f}%', '<a href="evidence/gateway-coverage.json">json</a>'],
                ["gen_routing.py", f'{p_cov["covered_lines"]}/{p_cov["num_statements"]}', f'{p_cov["percent_covered"]:.1f}%',
                 f'{p_cov["covered_branches"]}/{p_cov["num_branches"]}', f'{100 * p_cov["covered_branches"] / max(1, p_cov["num_branches"]):.1f}%',
                 '<a href="evidence/generator-coverage.json">json</a>']]
    gate_rows = [[html.escape(k), badge(v)] for k, v in upstream["steps"].items()] + \
                [[f"bazel <code>{html.escape(t)}</code>", badge("passed" if s == "PASSED" else "failed")] for t, s in upstream["bazel"]]
    itc_rows = [[f'<span class="id">{c["ID"]}</span>', f'<code>{c["Check"]}</code>', inline_md(c["Test case"]), c["Interfaces"],
                 c["Verifies"], badge(c["status"]), f'<span class="muted">{html.escape(c["detail"])}</span>'] for c in wp["itc"]]
    qtc_rows = [[f'<span class="id">{c["ID"]}</span>', inline_md(c["Test case"]), c["Method"], c["Verifies"], badge(c["status"]),
                 f'<span class="muted">{html.escape(c.get("detail", ""))}</span>'] for c in wp["qtc"]]
    gaps = [f'{r["id"]} {inline_md(r["title"])} — {r["status"]}' + (f' (missing: {", ".join(r["missing_levels"])})' if r["missing_levels"] else "")
            for r in swr.values() if r["status"] != "verified"]
    issues = ev["issues"] or ["None — every SYS has derived SWR; every SWR is allocated, implemented and referenced consistently."]
    evidence_rows = [
        ["SWE.1", link("OpenBSW/aspice/swe1-requirements/software-requirements.md"), "Software requirements"],
        ["SWE.2", link("OpenBSW/aspice/swe2-architecture/architecture.md"), "Architecture, elements, interfaces"],
        ["SWE.3", link("OpenBSW/aspice/swe3-detailed-design/detailed-design.md"), "Units and detailed design"],
        ["SWE.4", '<a href="evidence/module-junit.xml">module-junit.xml</a> · <a href="evidence/doipclient-junit.xml">doipclient-junit.xml</a> · <a href="evidence/gateway-ut.xml">gateway-ut.xml</a> · '
                  '<a href="evidence/generator-ut.xml">generator-ut.xml</a>', "Unit test results"],
        ["SWE.4", '<a href="evidence/cppcheck.txt">cppcheck.txt</a> · <a href="evidence/module-clang-tidy.txt">module-clang-tidy.txt</a> · '
                  '<a href="evidence/clang-tidy-gateway.txt">clang-tidy-gateway.txt</a> · <a href="evidence/complexity.csv">complexity.csv</a>',
         "Static verification"],
        ["SWE.4", '<a href="evidence/module-treefmt.txt">module-treefmt.txt</a> · <a href="evidence/module-copyright.txt">module-copyright.txt</a> · '
                  '<a href="evidence/module-bazel-test.txt">module-bazel-test.txt</a>', "OpenBSW upstream gates"],
        ["SWE.5", link("OpenBSW/evidence/gateway-it/results.json"), "Integration results (recorded)"],
        ["SWE.5", link("OpenBSW/evidence/board-gateway-it/results.json"), "S32K148EVB integration results (recorded)"],
        ["SWE.6", link("OpenBSW/evidence/sil-baseline/manifest.json"), "OpenBSW SIL baseline (Linux)"],
        ["SWE.6", link("OpenBSW/evidence/board-baseline/manifest.json"), "OpenBSW SIL baseline (S32K148EVB)"],
        ["SWE.3", '<a href="evidence/board-build.log">board-build.log</a>', "S32K148 build and memory regions"],
        ["All", '<a href="summary.json">summary.json</a>', "Machine-readable summary"],
    ]
    tool_rows = [[html.escape(k), html.escape(v)] for k, v in tools.items()]
    nav = [("overview", "Overview"), ("swe1", "SWE.1 Requirements"), ("swe2", "SWE.2 Architecture"), ("swe3", "SWE.3 Detailed design"),
           ("swe4", "SWE.4 Unit verification"), ("swe5", "SWE.5 Integration test"), ("swe6", "SWE.6 Qualification test"),
           ("trace", "Traceability"), ("gaps", "Gaps & issues"), ("evidence", "Evidence & tools")]
    generated = time.strftime("%Y-%m-%d %H:%M %Z")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>ASPICE SWE Evidence</title><style>{CSS}</style></head><body>
<header><h1>ASPICE SWE evidence — OpenBSW zonal diagnostic gateway</h1>
<p>Linux executable <code>{built['elf_sha256'][:16]}…</code> · S32K148 image <code>{(board.get('elf_sha256') or '—')[:16]}…</code> · OpenBSW <code>{built['openbsw_lock'][:12]}</code> + contributed <code>transportRouter</code> · generated {generated}. Demonstration of SWE.1–SWE.6 work products; not an assessed ASPICE capability level.</p></header>
<div class="layout"><nav>{"".join(f'<a href="#{a}">{b}</a>' for a, b in nav)}</nav><main>
<section id="overview"><h2>Overview</h2><p class="lead">Indicators are computed from the work products and from tool runs during generation. Integration results are the recorded SWE.5 run; the generator checks it used the current executable.</p><div class="kpis">{kpi_html}</div></section>
<section id="swe1"><h2>SWE.1 Software requirements analysis</h2><p class="lead">{len(swr)} software requirements derived from {len(wp['sys'])} system requirements.</p>
<h3>System requirements (input)</h3>{table(["ID", "Title", "Statement", "Derived SWR"], sys_rows)}
<h3>Software requirements</h3>{table(["ID", "Requirement", "Type", "From", "Planned", "Criterion", "Status"], req_rows)}</section>
<section id="swe2"><h2>SWE.2 Software architectural design</h2><p class="lead">{len(wp['elements'])} elements, {len(wp['interfaces'])} interfaces, {len(wp['decisions'])} decisions.</p>
{diagram_block(["context", "deployment", "components", "physical-routing", "functional-routing", "route-state"])}
<h3>Elements</h3>{table(["ID", "Element", "Responsibility", "Satisfies"], element_rows)}
<h3>Interfaces</h3>{table(["ID", "Interface", "Provider → consumer", "Contract"], interface_rows)}
<h3>Design decisions</h3>{table(["ID", "Decision", "Rationale"], decision_rows)}</section>
<section id="swe3"><h2>SWE.3 Software detailed design and unit construction</h2><p class="lead">{len(wp['units'])} units. Gateway release build: {badge('passed' if built['build_ok'] and not built['warnings'] else 'failed')} ({built['warnings']} warnings); module in the OpenBSW unit-test build: {upstream['build_warnings']} warnings.</p>
{table(["ID", "Unit", "Source / functions", "Element", "Implements"], unit_rows)}
{diagram_block(["classify", "buffer-ownership"])}
<h3>Coding guidelines</h3>{table(["ID", "Rule", "Check"], guideline_rows)}
<h3>Justified deviations</h3>{table(["ID", "Tool / rule", "Location", "Justification"], deviation_rows)}</section>
<section id="swe4"><h2>SWE.4 Software unit verification</h2><p class="lead">{ut_pass}/{ut_total} unit tests passed.</p>
<h3>Unit test cases</h3>{table(["ID", "Test case", "Unit", "Verifies", "Result"], utc_rows)}
<h3>Structural coverage</h3>{table(["Scope", "Lines", "Line %", "Branches", "Branch %", ""], cov_rows)}
<h3>Upstream OpenBSW gates for the contributed module</h3>{table(["Gate", "Result"], gate_rows)}
<h3>cppcheck</h3>{table(["Location", "Severity", "Rule", "Message", "Status"], finding_rows)}
<h3>clang-tidy</h3><p>Modules (OpenBSW <code>.clang-tidy</code>): transportRouter {upstream['tidy_findings']}, doipClient {doip['tidy_findings']} findings. Gateway units: {len(ev['gateway_tidy'])} findings.</p>
<h3>Complexity (CCN &gt; 10)</h3>{table(["File", "Function", "NLOC", "CCN", "Status"], complex_rows)}</section>
<section id="swe5"><h2>SWE.5 Software integration and integration test</h2><p class="lead">PC run <code>{html.escape((it or {}).get('run_id', '—'))}</code>: executable {'identical to the current build' if ev['it_current'] else '<strong>differs from the current build</strong>'}. S32K148EVB run <code>{html.escape((board_it or {}).get('run_id', '—'))}</code>: image {'identical to the current board build' if ev['board_current'] else '<strong>differs from the current board build</strong>'}.</p>
{table(["ID", "Check", "Test case", "Interfaces", "Verifies", "Result", "Duration"], itc_rows)}</section>
<section id="swe6"><h2>SWE.6 Software qualification test</h2><p class="lead">Automated analyses are computed now; live campaigns record their status. Bus load: worst case {load['worst_percent']} %, measured peak {load['measured_percent']} %.</p>
{table(["ID", "Test case", "Method", "Verifies", "Result", "Detail"], qtc_rows)}</section>
<section id="trace"><h2>Traceability</h2><p class="lead">SYS → SWR → ARC → DD → UT/IT/QT/AN/RV.</p>
{table(["SWR", "SYS", "ARC", "DD", "UT", "IT", "QT", "AN", "RV", "Status"], trace_rows)}</section>
<section id="gaps"><h2>Gaps &amp; issues</h2><h3>Requirements not fully verified</h3><ul>{"".join(f"<li>{g}</li>" for g in gaps) or "<li>None</li>"}</ul>
<h3>Traceability issues</h3><ul>{"".join(f"<li>{html.escape(i)}</li>" for i in issues)}</ul></section>
<section id="evidence"><h2>Evidence &amp; tools</h2>{table(["Process", "Artifact", "Content"], evidence_rows)}{table(["Tool", "Version"], tool_rows)}</section>
</main></div></body></html>"""


def tool_version(cmd):
    try:
        out = run(cmd, check=False, timeout=60)
        return ((out.stdout or out.stderr).strip().splitlines() or ["?"])[0]
    except Exception as error:  # noqa: BLE001 - reported, not fatal
        return f"unavailable ({error})"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skip-upstream", action="store_true", help="reuse the last upstream gate run")
    args = parser.parse_args(argv)
    ws = workspace()
    REPORT.mkdir(exist_ok=True)
    shutil.rmtree(EVIDENCE, ignore_errors=True)
    EVIDENCE.mkdir(parents=True)
    os.environ["PATH"] = f"{ws['workspace'] / 'tools' / 'bin'}:{ws['venv'] / 'bin'}:{os.environ['PATH']}"
    wp = load_work_products()
    print("rendering diagrams …", flush=True)
    diagrams = render_diagrams()
    print("upstream gates (OpenBSW unit tests, format, copyright, tidy, bazel) …", flush=True)
    upstream = upstream_gates(ws, args.skip_upstream)
    print("DoIP client module (OpenBSW unit tests, format, tidy) …", flush=True)
    doip = doip_client_gates(args.skip_upstream)
    print("gateway unit tests …", flush=True)
    gw_cases, gw_cov, ut_build = gateway_unit_tests(ws)
    print("generator tests …", flush=True)
    py_cases, py_cov = generator_tests(ws)
    print("static analysis …", flush=True)
    findings, gateway_tidy, functions = static_analysis(ws, ut_build)
    print("build checks …", flush=True)
    built = build_checks(ws)
    print("board build …", flush=True)
    board = board_checks(ws)
    it = json.loads((IT_EVIDENCE / "results.json").read_text()) if (IT_EVIDENCE / "results.json").exists() else None
    board_it = (json.loads((BOARD_IT_EVIDENCE / "results.json").read_text())
                if (BOARD_IT_EVIDENCE / "results.json").exists() else None)
    unit_cases = {**upstream["cases"], **doip["cases"], **gw_cases, **py_cases}
    load, _ = qualification(wp, ws, upstream, built, it, board, board_it, doip)
    ev = evaluate(wp, unit_cases, it, built, findings, gateway_tidy, functions, upstream, board, board_it)
    tools = {"gcc": tool_version(["gcc", "--version"]), "cmake": tool_version([ws["venv"] / "bin" / "cmake", "--version"]),
             "cppcheck": tool_version(["cppcheck", "--version"]), "clang-tidy": tool_version(["clang-tidy", "--version"]),
             "arm-none-eabi-gcc": tool_version([ws["workspace"] / "tools" / ARM_TOOLCHAIN / "bin" / "arm-none-eabi-gcc", "--version"]),
             "clang-format": tool_version(["clang-format-17", "--version"]), "treefmt": tool_version(["treefmt", "--version"]),
             "gcovr": tool_version([ws["venv"] / "bin" / "gcovr", "--version"]), "lizard": tool_version([ws["venv"] / "bin" / "lizard", "--version"]),
             "bazelisk": "1.29.0 (SHA-256 pinned)", "PlantUML": f"{PLANTUML_VERSION} (sha1 {PLANTUML_SHA1[:12]})"}
    cov = {"module": upstream["coverage"], "doip_client": doip["coverage"], "gateway": gw_cov, "generator": py_cov}
    (REPORT / "aspice-swe-report.html").write_text(
        render(wp, diagrams, ev, unit_cases, cov, built, findings, functions, upstream, it, load, tools, board, board_it,
               doip))
    swr = wp["swr"]
    summary = {
        "generated": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "executable_sha256": built["elf_sha256"], "openbsw_revision": built["openbsw_lock"],
        "requirements": {r["id"]: {"status": r["status"], "missing_levels": r["missing_levels"]} for r in swr.values()},
        "requirement_counts": dict(Counter(r["status"] for r in swr.values())),
        "unit_tests": {"total": len(unit_cases), "passed": sum(s == "passed" for s in unit_cases.values())},
        "coverage": {"module": {k: upstream["coverage"][k] for k in ("line_percent", "branch_percent", "function_percent")},
                     "doip_client": {k: doip["coverage"][k] for k in ("line_percent", "branch_percent", "function_percent")},
                     "gateway": {k: gw_cov[k] for k in ("line_percent", "branch_percent")},
                     "generator": {"line_percent": py_cov["percent_covered"]}},
        "upstream_gates": upstream["steps"], "bazel": upstream["bazel"],
        "static": {"cppcheck_open": len(ev["open_findings"]), "cppcheck_total": len(findings),
                   "clang_tidy_module": upstream["tidy_findings"], "clang_tidy_doip_client": doip["tidy_findings"],
                   "clang_tidy_gateway": len(gateway_tidy),
                   "ccn_violations": sum(f["status"] == "violation" for f in functions)},
        "integration": {c["ID"]: c["status"] for c in wp["itc"]}, "integration_current": ev["it_current"],
        "board": {"image_sha256": board.get("elf_sha256"), "regions": board.get("regions"),
                  "integration_current": ev["board_current"], "posix_headers": board.get("posix_headers")},
        "qualification": {c["ID"]: {"status": c["status"], "detail": c.get("detail", "")} for c in wp["qtc"]},
        "bus_load": load, "trace_issues": ev["issues"],
    }
    (REPORT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    c = summary["requirement_counts"]
    print(f"requirements: {c} | unit {summary['unit_tests']} | IT current={ev['it_current']} | "
          f"trace issues {len(ev['issues'])}")
    print(f"report: {REPORT / 'aspice-swe-report.html'}")
    failed_tests = summary["unit_tests"]["passed"] != summary["unit_tests"]["total"]
    return 1 if failed_tests or ev["issues"] and any("unknown" in i for i in ev["issues"]) else 0


if __name__ == "__main__":
    sys.exit(main())
