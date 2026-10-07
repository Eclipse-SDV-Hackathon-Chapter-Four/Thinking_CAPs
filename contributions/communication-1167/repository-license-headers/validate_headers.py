"""Verify the whole-code header inventory and the durable bundle banner."""

import ast
import hashlib
import json
import re
import subprocess
from pathlib import Path

import repair_headers as repair


HERE = Path(__file__).resolve().parent
INFO = repair.INFO
WORKSPACE = repair.WORKSPACE


def main():
    audit = json.loads((HERE / "code-header-audit.json").read_text())
    results = {"baseline": INFO["baseline"], "code_file_count": audit["code_file_count"],
               "missing_headers": [], "python_ast_unchanged": [], "node_syntax_pass": [],
               "shell_syntax_pass": [], "comment_only_changes": [], "links": [], "empty_markers": []}
    generator = ".github/actions/00_infrastructure/setup_bazel_cache/build.mjs"
    for item in audit["files"]:
        name = item["path"]
        path = WORKSPACE / name
        if path.is_symlink():
            target = path.resolve().relative_to(WORKSPACE)
            assert str(target) in {f["path"] for f in audit["files"]}
            results["links"].append({"path": name, "target": str(target)})
            continue
        text = path.read_text()
        item["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        if not text.strip():
            results["empty_markers"].append(name)
            continue
        prefix = repair.leading_comments(text)
        assert re.search(r"Copyright\s*(?:\(c\)|©)?\s*\d{4}", prefix, re.I), name
        assert re.search(r"SPDX-License-Identifier:|licensed under|terms of the .*License", prefix, re.I), name
        assert prefix.count("SPDX-License-Identifier:") == 1, name
        if path.suffix == ".py":
            old = subprocess.check_output(["git", "show", INFO["baseline"] + ":" + name], cwd=WORKSPACE).decode()
            assert ast.dump(ast.parse(old)) == ast.dump(ast.parse(text)), name
            results["python_ast_unchanged"].append(name)
        if path.suffix in {".js", ".mjs"}:
            subprocess.run(["node", "--check", str(path)], check=True, capture_output=True)
            results["node_syntax_pass"].append(name)
        if path.suffix == ".sh" or name.endswith(".sh.tpl"):
            subprocess.run(["bash", "-n", str(path)], check=True, capture_output=True)
            results["shell_syntax_pass"].append(name)
    changed = subprocess.check_output(["git", "diff", INFO["baseline"], "--name-only"], cwd=WORKSPACE, text=True).splitlines()
    for name in changed:
        if name == generator:
            continue
        old = subprocess.check_output(["git", "show", INFO["baseline"] + ":" + name], cwd=WORKSPACE).decode()
        text = (WORKSPACE / name).read_text()
        ext = Path(name).suffix.lstrip(".")
        style = "html" if ext in {"html", "j2"} else "c" if ext in {"cpp", "h", "rs", "js", "mjs", "css", "fbs", "trlc", "rsl"} else "hash"
        assert re.sub(r"\s+", "", repair.remove_comments(old, style)) == re.sub(r"\s+", "", repair.remove_comments(text, style)), name
        results["comment_only_changes"].append(name)
    # Execute the real old/new build script with only esbuild's output side effect captured.
    # Verify that both generated programs differ solely by the legal comment banner.
    source = (WORKSPACE / generator).read_text()
    old_source = subprocess.check_output(["git", "show", INFO["baseline"] + ":" + generator], cwd=WORKSPACE).decode()
    capture = 'const captured = []; const esbuild = {build: async (options) => captured.push(options)};'
    options = []
    for content in [old_source, source]:
        content = content.replace('import * as esbuild from "esbuild";', capture)
        content += '\nconsole.log(JSON.stringify(captured));\n'
        run = subprocess.run(["node", "--input-type=module"], input=content, text=True, capture_output=True, check=True)
        options.append(json.loads(run.stdout))
    assert len(options[0]) == len(options[1]) == 2
    for before, after in zip(*options):
        old_banner = before["banner"]["js"]
        new_banner = after["banner"]["js"]
        assert "Copyright (c)" in new_banner and "SPDX-License-Identifier: Apache-2.0" in new_banner
        assert repair.remove_comments(new_banner, "c").strip() == old_banner
        before["banner"]["js"] = after["banner"]["js"]
        assert before == after
    results["bundle_banner"] = {"two_output_configurations_pass": True, "non_comment_banner_unchanged": True,
                               "all_other_build_options_unchanged": True}
    results["changed_file_count"] = len(changed)
    for change in audit["changes"]:
        change["after_sha256"] = hashlib.sha256((WORKSPACE / change["path"]).read_bytes()).hexdigest()
        if change["path"] == generator:
            change["non_comment_content_unchanged"] = False
            change["bundle_output_non_comment_content_unchanged"] = True
            change["reason"] = "durable generated license banner; all other output options preserved"
    (HERE / "final-code-header-audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")
    (HERE / "validation.json").write_text(json.dumps(results, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: len(v) if isinstance(v, list) else v for k, v in results.items()}))


if __name__ == "__main__":
    main()
