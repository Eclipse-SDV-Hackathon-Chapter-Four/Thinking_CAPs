# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

"""Repair project notices, preserving existing years, bodies and imported licenses."""
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

PACKET = Path(__file__).resolve().parent
ROOT = Path(json.loads((PACKET / "workspace.json").read_text())["root"])
HASH_EXTENSIONS = {".py", ".sh", ".bash", ".bzl", ".bazel", ".yml", ".yaml", ".qls"}
BLOCK_EXTENSIONS = {".c", ".cc", ".cpp", ".cxx", ".h", ".hh", ".hpp", ".hxx", ".rs", ".trlc", ".rsl", ".js", ".mjs", ".ts", ".ql"}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def template_map():
    templates = {}
    current = []
    lines = []
    source = ROOT / "candidate/third_party/cr_checker/templates.ini"
    for line in source.read_text().splitlines(keepends=True):
        if re.fullmatch(r"\[[^\n]+\]\n?", line):
            for extension in current:
                templates[extension] = "".join(lines).rstrip() + "\n"
            current = line.strip()[1:-1].split(",")
            lines = []
        else:
            lines.append(line)
    for extension in current:
        templates[extension] = "".join(lines).rstrip() + "\n"
    return templates


def code_kind(path):
    if path.name in {"BUILD", "BUILD.bazel", "MODULE.bazel"} or path.suffix in HASH_EXTENSIONS or path.name.endswith((".sh.tpl", ".bzl.txt")):
        return "py"
    if path.suffix in BLOCK_EXTENSIONS:
        return "cpp"
    if path.suffix == ".puml":
        return "puml"
    return None


def split_notice(text):
    """Split a leading project header only; reject unrelated copyright owners."""
    prefix = ""
    if text.startswith("#!"):
        prefix, _, text = text.partition("\n")
        prefix += "\n"
    match = re.search(r"Copyright \(c\) ([0-9{},year -]+) Contributors to the Eclipse Foundation", text[:1500])
    if not match:
        assert not re.search(r"Copyright \(c\)", text[:1000]), "Review foreign copyright before editing"
        minimal = re.match(r"(?://|#) SPDX-License-Identifier: Apache-2\.0\n", text)
        return prefix, "2026", text[minimal.end():] if minimal else text
    spdx = text.index("SPDX-License-Identifier:", match.start())
    assert "Apache-2.0" in text[spdx:text.index("\n", spdx)], "Never rewrite a foreign license"
    end = text.index("\n", spdx) + 1
    following = text[end:].split("\n", 1)[0]
    if re.fullmatch(r"[ /*#'=-]+", following) and following.strip():
        end += len(following) + 1
    # Only comments may precede this leading notice.
    assert all(not line.strip() or re.fullmatch(r"[ /*#'=-]+", line) for line in text[:match.start()].splitlines()[:-1])
    year = match[1] if "{year}" not in match[1] else "2026"
    return prefix, year, text[end:]


def repair(path, template, records, label):
    old = path.read_bytes()
    text = old.decode()
    prefix, year, body = split_notice(text)
    new = (prefix + template.replace("{year}", year) + ("\n" if body and not body.startswith("\n") else "") + body).encode()
    if new != old:
        path.write_bytes(new)
        records.append({"repository": label, "path": str(path.relative_to(ROOT / label)) if label != "packet" else path.name,
                        "before_sha256": sha(old), "after_sha256": sha(new), "year": year,
                        "program_body_sha256": sha(body.encode()), "program_body_retained": True})


def main():
    if (PACKET / "license-header-audit.json").exists():
        raise RuntimeError("Notice cleanup already applied. Review or reproduce the exported license patches; audit_license_headers.py verifies the final files.")
    history = PACKET / "license-header-history"
    history.mkdir(exist_ok=True)
    for name in ["communication-subject.json", "config_management-subject.json", "copyright-current-disposition.json", "artifact-manifest.json"]:
        destination = history / ("packet-manifest-before.json" if name == "artifact-manifest.json" else name)
        if not destination.exists():
            shutil.copy2(PACKET / name, destination)
    for repo in ["communication", "config_management"]:
        destination = PACKET / "patches" / (repo + "-before-license-headers.patch")
        if not destination.exists():
            shutil.copy2(PACKET / "patches" / (repo + ".patch"), destination)
    templates = template_map()
    errors = json.loads((history / "copyright-current-disposition.json").read_text())["errors"]
    wrong = {e["path"] for e in errors if e["kind"] == "Wrong copyright format"}
    missing = {e["path"] for e in errors if e["kind"] == "Missing copyright header"}
    records = []
    for label in ["candidate", "config-management-consumer-candidate"]:
        source = ROOT / label
        files = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=source, text=True).splitlines()
        for name in sorted(set(files)):
            path = source / name
            kind = code_kind(path)
            if not path.is_file() or (kind is None and name not in missing):
                continue
            if name.endswith("TypeAliasesDeclaration.ql"):
                continue  # MIT source is handled separately with its original notice.
            text = path.read_text()
            if (label == "candidate" and name in wrong) or "SPDX-License-Identifier:" not in text[:4096] or "Copyright" not in text[:4096] or "Copyright (c) {year}" in text[:4096]:
                if path.suffix == ".rst":
                    kind = "rst"
                repair(path, templates[kind], records, label)
    for path in sorted(PACKET.glob("*.py")):
        if "SPDX-License-Identifier:" not in path.read_text()[:1000]:
            repair(path, templates["py"], records, "packet")
    (PACKET / "license-header-adjustments.json").write_text(json.dumps(records, indent=2) + "\n")
    print("Notice-only corrections:", len(records))


if __name__ == "__main__":
    main()
