"""Audit every tracked code file and repair project headers without changing ownership."""

import datetime
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
INFO = json.loads((HERE / "workspace.json").read_text())
WORKSPACE = Path(INFO["workspace"])
CHECKER = HERE.parent / "non-qnx-verification/copyright/pinned-cr_checker.py"
CODE_EXTENSIONS = {
    ".cpp", ".h", ".rs", ".py", ".sh", ".bzl", ".bazel", ".js", ".mjs",
    ".BUILD", ".MODULE", ".build", ".tpl", ".j2", ".in", ".fbs", ".css", ".html",
    ".trlc", ".rsl", ".yml", ".yaml", ".toml", ".bazelrc",
}


def digest(text):
    return hashlib.sha256(text.encode()).hexdigest()


def leading_comments(text):
    """Read comments before executable code, retaining shebang/doctype handling."""
    rest = text.lstrip("\ufeff\n \t")
    consumed = ""
    while rest:
        rest = rest.lstrip()
        match = re.match(r"(?:#![^\n]*\n|<!DOCTYPE[^>]*>\s*|/\*.*?\*/\s*|"
                         r"<!--.*?-->\s*|\{#.*?#\}\s*|(?://|#)[^\n]*(?:\n|$)\s*)", rest, re.S)
        if not match:
            break
        consumed += match[0]
        rest = rest[match.end():]
    return consumed


def creation_year(name):
    dates = subprocess.check_output([
        "git", "log", "--follow", "--diff-filter=A", "--format=%aI", "--", name,
    ], cwd=WORKSPACE, text=True).splitlines()
    if not dates:
        raise ValueError(f"No creation history for {name}")
    return dates[-1][:4]


def remove_comments(text, style):
    # Keep quoted strings intact: comment markers inside literals are data.
    if style == "html":
        return re.sub(r"<!--.*?-->|\{#.*?#\}", "", text, flags=re.S)
    quoted = r'''"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*' '''.rstrip()
    comments = r"/\*.*?\*/|//[^\n]*" if style == "c" else r"\#[^\n]*"
    return re.sub(f"({quoted})|({comments})", lambda m: m[1] or "", text, flags=re.S)


def main():
    spec = importlib.util.spec_from_file_location("pinned_cr_checker", CHECKER)
    checker = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = checker
    spec.loader.exec_module(checker)
    templates = checker.load_templates(WORKSPACE / "third_party/cr_checker/templates.ini")
    config = WORKSPACE / "third_party/cr_checker/config.json"
    names = subprocess.check_output(["git", "ls-files", "-z"], cwd=WORKSPACE).decode().split("\0")[:-1]
    code = [n for n in names if Path(n).suffix in CODE_EXTENSIONS or Path(n).name in {"BUILD", "WORKSPACE"}]
    changes = []
    audit = []
    for name in code:
        path = WORKSPACE / name
        if path.is_symlink():
            target = path.resolve().relative_to(WORKSPACE)
            audit.append({"path": name, "status": "tracked_link_to_audited_file", "target": str(target)})
            continue
        original = subprocess.check_output(["git", "show", INFO["baseline"] + ":" + name],
                                           cwd=WORKSPACE).decode()
        text = original
        if not text.strip():
            audit.append({"path": name, "status": "empty_marker_no_code_content"})
            continue
        ext = path.suffix.lstrip(".") or path.name
        style = "html" if ext in {"html", "j2"} else "c" if ext in {"cpp", "h", "rs", "js", "mjs", "css", "fbs", "trlc", "rsl"} else "hash"
        prefix = leading_comments(text)
        has_copyright = bool(re.search(r"Copyright\s*(?:\(c\)|©)?\s*\d{4}", prefix, re.I))
        has_license = bool(re.search(r"SPDX-License-Identifier:|licensed under|terms of the .*License", prefix, re.I))
        template = templates.get(ext)
        if template:
            layout = checker.locate_header(text)
            status, _ = checker.classify(layout, template, config)
            if status.name in {"WRONG_FORMAT", "MISPLACED", "MISPLACED_AND_WRONG_FORMAT"}:
                years = re.findall(r"Copyright\s*(?:\(c\)|©)?\s*(\d{4}(?:-\d{4})?)", prefix, re.I)
                if len(years) != 1 or "Contributors to the Eclipse Foundation" not in prefix or "SPDX-License-Identifier: Apache-2.0" not in prefix:
                    raise ValueError(f"Nonstandard ownership/license needs individual review: {name}")
                rendered = template.replace("{year}", years[0])
                text = checker.normalize_header(text, layout, rendered, config)
            elif status.name not in {"COMPLIANT", "MISSING", "LICENSE_MISMATCH"}:
                raise ValueError(f"Unexpected header status {status.name}: {name}")
        if not (has_copyright and has_license):
            year_match = re.search(r"Copyright\s*(?:\(c\)|©)?\s*(\d{4}(?:-\d{4})?)", prefix, re.I)
            year = year_match[1] if year_match else creation_year(name)
            if has_copyright:
                raise ValueError(f"Existing owner without license must be reviewed individually: {name}")
            block = templates["cpp" if style == "c" else "py"].format(year=year)
            if style == "html":
                plain = "\n".join(line[2:] if line.startswith("# ") else "" for line in block.splitlines())
                block = "<!--\n" + plain.strip() + "\n-->\n"
            # Replace a lone existing Apache SPDX comment with the full same-license header.
            text = re.sub(r"^(?://|#) SPDX-License-Identifier: Apache-2\.0\n", "", text)
            prefix_match = re.match(r"(?:#![^\n]*\n|<!DOCTYPE[^>]*>\s*)", text, re.I)
            offset = prefix_match.end() if prefix_match else 0
            text = text[:offset] + block + "\n" + text[offset:]
        if text != original:
            before = re.sub(r"\s+", "", remove_comments(original, style))
            after = re.sub(r"\s+", "", remove_comments(text, style))
            if before != after:
                raise ValueError(f"Non-comment content changed: {name}")
            changes.append({"path": name, "before_sha256": digest(original), "after_sha256": digest(text),
                            "non_comment_content_unchanged": True})
        if path.read_text() != text:
            path.write_text(text)
        prefix = leading_comments(text)
        assert re.search(r"Copyright\s*(?:\(c\)|©)?\s*\d{4}", prefix, re.I), name
        assert re.search(r"SPDX-License-Identifier:|licensed under|terms of the .*License", prefix, re.I), name
        audit.append({"path": name, "status": "copyright_and_license_in_leading_comments",
                      "sha256": digest(text), "changed": text != original})
    report = {"time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "baseline": INFO["baseline"], "code_file_count": len(code),
              "changed_file_count": len(changes), "code_extensions": sorted(CODE_EXTENSIONS),
              "changes": changes, "files": audit,
              "template_sha256": digest((WORKSPACE / "third_party/cr_checker/templates.ini").read_text()),
              "scope": "all tracked code; JSON/data/docs excluded; existing foreign licenses and original years retained"}
    (HERE / "code-header-audit.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"code_files": len(code), "repaired": len(changes)}))


if __name__ == "__main__":
    main()
