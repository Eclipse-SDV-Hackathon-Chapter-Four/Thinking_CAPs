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

"""Audit current code and export the notice change independently of feature fixes."""
import ast
import json
import os
from pathlib import Path
import re
import subprocess

from fix_license_headers import PACKET, ROOT, code_kind, sha


def body(text):
    """Remove the leading notice while retaining every nonblank program line."""
    if text.startswith("/*\n * MIT License\n"):
        text = text[text.index(" */\n") + len(" */\n"):]
    elif text.startswith("/**\n * MIT License\n"):
        text = "/**\n" + text[text.index(" * @id"):]
    if "SPDX-License-Identifier:" in text[:4096]:
        copyright = re.search(r"^.*Copyright \(c\).*$", text[:4096], re.MULTILINE)
        if copyright:
            start = copyright.start()
            # Include the opening border / comment marker on the preceding line.
            previous = text[:start].rstrip("\n").rsplit("\n", 1)[-1]
            if previous and re.fullmatch(r"[ /*#'=-]+", previous):
                start -= len(previous) + 1
            end = text.index("\n", text.index("SPDX-License-Identifier:", copyright.start())) + 1
            following = text[end:].split("\n", 1)[0]
            if following and re.fullmatch(r"[ /*#'=-]+", following):
                end += len(following) + 1
            text = text[:start] + text[end:]
        else:
            text = re.sub(r"^(?://|#) SPDX-License-Identifier: Apache-2\.0\n", "", text)
    text = text.replace("/* This header covers project-owned portions. Bundled third-party notices\n * and their license terms are retained below. */\n", "")
    return "\n".join(line for line in text.splitlines() if line.strip()).encode()


def audit():
    result = {"scope": "All current repository code files, including empty packages, generated bundles, fixtures and templates; packet-owned Python helpers. Immutable historical exports and external dependencies retain their original evidence bytes.",
              "policy": "https://www.eclipse.org/projects/handbook/#ip-copyright-headers",
              "repositories": {}, "failures": [], "changes": []}
    allowed_behavior_changes = {"BUILD", "third_party/cr_checker/BUILD", "third_party/cr_checker/templates.ini", ".github/actions/00_infrastructure/setup_bazel_cache/build.mjs", "MODULE.bazel"}
    for name, label in [("communication", "candidate"), ("config_management", "config-management-consumer-candidate")]:
        source = ROOT / label
        files = sorted(set(subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=source, text=True).splitlines()))
        checked = {}
        for item in files:
            path = source / item
            if not path.is_file() or code_kind(path) is None:
                continue
            content = path.read_bytes()
            prefix = content.decode()[:4096]
            license_id = re.search(r"SPDX-License-Identifier:\s*([A-Za-z0-9.-]+)", prefix)
            if not license_id or not re.search(r"Copyright \(c\) \d", prefix):
                result["failures"].append(name + "/" + item)
            checked[item] = {"sha256": sha(content), "license": license_id[1] if license_id else None}
        result["repositories"][name] = {"code_files": len(checked), "files": checked}
        index = ROOT / (name + "-license-before.index")
        index.unlink(missing_ok=True)
        env = {**os.environ, "GIT_INDEX_FILE": str(index)}

        def git(*args):
            return subprocess.check_output(["git", *args], cwd=source, env=env)

        git("read-tree", "HEAD")
        git("apply", "--cached", str(PACKET / "patches" / (name + "-before-license-headers.patch")))
        before_tree = git("write-tree").decode().strip()
        git("add", "--all", ".")
        after_tree = git("write-tree").decode().strip()
        patch = PACKET / "patches" / (name + "-license-headers.patch")
        patch.write_bytes(git("diff", "--binary", before_tree, after_tree))
        for item in git("diff", "--name-only", before_tree, after_tree).decode().splitlines():
            new = git("show", after_tree + ":" + item)
            original = subprocess.run(["git", "show", before_tree + ":" + item], cwd=source, env=env, capture_output=True)
            row = {"repository": name, "path": item, "before_sha256": sha(original.stdout) if original.returncode == 0 else None, "after_sha256": sha(new)}
            if original.returncode == 0 and code_kind(Path(item)):
                same = body(original.stdout.decode()) == body(new.decode())
                row.update(nonblank_program_lines_retained=same, program_body_sha256=sha(body(new.decode())))
                if not same and item == "score/config_management/dependability/BUILD":
                    trees = [ast.parse(body(value.decode()).decode()) for value in [original.stdout, new]]
                    for tree in trees:
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Call):
                                node.keywords.sort(key=lambda keyword: keyword.arg)
                    order_only = ast.dump(trees[0]) == ast.dump(trees[1])
                    row["buildifier_keyword_order_only"] = order_only
                    same = order_only
                if not same and item not in allowed_behavior_changes:
                    result["failures"].append("unexpected body change: " + name + "/" + item)
            result["changes"].append(row)
        index.unlink()
    helpers = sorted(PACKET.glob("*.py"))
    result["packet_helpers"] = {f.name: sha(f.read_bytes()) for f in helpers}
    for f in helpers:
        if not re.search(r"Copyright \(c\) \d+ Contributors to the Eclipse Foundation", f.read_text()[:1000]) or "SPDX-License-Identifier: Apache-2.0" not in f.read_text()[:1000]:
            result["failures"].append(f.name)
    # The imported query retains the exact upstream notice and has a MIT identifier.
    query = (ROOT / "candidate/quality/static_analysis/query_overrides/TypeAliasesDeclaration.ql").read_text()
    license_text = (ROOT / "candidate/quality/static_analysis/query_overrides/LICENSE.md").read_text()
    for line in license_text.rstrip().splitlines():
        if line and " * " + line not in query:
            result["failures"].append("MIT license text not retained: " + line)
    result["modified_vendor_helpers"] = 6
    patch = (ROOT / "candidate/third_party/rules_build_error/bash-interpreters.patch").read_text()
    if patch.count("+# SPDX-License-Identifier: CC0-1.0") != 6:
        result["failures"].append("CC0 helper notices")
    result["summary"] = {"code_files": sum(v["code_files"] for v in result["repositories"].values()), "packet_helpers": len(helpers), "failures": len(result["failures"])}
    (PACKET / "license-header-audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"summary": result["summary"], "failures": result["failures"]}, indent=2))
    return bool(result["failures"])


if __name__ == "__main__":
    raise SystemExit(audit())
