# Eclipse license-header audit — #2850

**Passed:** the selected native checkout and all maintained/exported packet Python scripts now carry the applicable Eclipse S-CORE Apache-2.0 headers. Existing notices and years were preserved; missing headers use the project's `Contributors to the Eclipse Foundation` / 2026 template.

The source of the rule is the native `.pre-commit-config.yaml`, which pins `eclipse-score/tooling` at `31ff8eee214e4e97ef8f5cb46e443273515b63ec`. The checker, exact `templates.ini` and author `config.json` are retained in the adapter packet. This audit used those inputs without exclusions or policy changes.

- All **164** native tracked files supported by the checker passed, including **85 Python files**, the shell script, YAML/workflows, Bazel files and RST documents.
- All **15** packet Python scripts passed the same checker, including the verifiers, exported collectors and audit scripts.
- Six native files received headers: `prepare_commit.sh`, `copier.yml`, `.github/score/.copier-answers.yml`, and three empty Python package `__init__.py` files. The checker exempts empty files, but these now have explicit headers too.
- Eleven existing packet scripts received headers. Their pre-header bytes are retained in an archive; Python ASTs match after the comment insertion. Earlier collectors remain recorded execution snapshots.
- JSON, Markdown and other formats without a native template are explicitly inventoried rather than counted as checked. No comments were inserted into JSON evidence, schemas or fixed contracts. The independent, unselected contribution and archived upstream sources were preserved.

[Final raw checks and exact inventories](evidence/checks.json), [native log](evidence/native-after.log), [packet-script log](evidence/packet-scripts-after.log), [change proof](evidence/header-changes.json), and [refreshed patch proof](evidence/patch-refresh.json) record the result.

The initial broader check found three inherited nonempty native files missing headers. Its failure is retained. A first whitespace check found a trailing blank line in the three new header-only Python package files; it was corrected, and the failing log is retained. Final copyright, shell syntax, Python syntax, patch whitespace and clean application checks pass. The three header-only Python package files also pass the native pinned Ruff lint and format checks; see `evidence/python-header-lint.json`.

The final native patch has **191** changed files: the original **185** implementation files remain byte-identical, plus six proven license-comment insertions into baseline files. The earlier 274-case runtime evidence is retained as **pre-header-follow-up evidence**; runtime tests were not rerun for this low-impact comment change. The current patch/tree/hash bindings and manifests were refreshed. No runtime result is falsely attributed to the newer byte revision.

The integration choice remains the adapter stacked on #628's `harness` branch. Its conflict/integration, typing and human acceptance gates remain pending. Copyright-check success supplies no project or contributor approval.
