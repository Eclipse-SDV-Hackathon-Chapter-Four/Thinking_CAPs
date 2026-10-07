# Lifecycle #704 implementation and guarded comparison preparation

Date: 2026-10-04. Owner instruction: `go` after the proposed local implementation and
comparison-preparation next step. [Summary](summary.json) records measured results.

## Change and portable review subject

[lifecycle-704.patch](lifecycle-704.patch) applies cleanly to upstream lifecycle commit
`7d1d7bec81d96752b5a9a235044d2dfc3ecd259b`, verified in a second clean disposable checkout.
It replaces three checked-in JSON files with one `config/mw_com_config.bzl` generator
and three explicit profiles. Existing output labels, filenames, test runfiles and integration
package paths are retained. Common service and method definitions occur once; distinct
provider-test, client-test and integration settings remain explicit.

The two unit-test BUILD files and environment BUILD file load this generator. No C++,
requirements, native architecture or global fabric policy was changed. Source license/notice,
module/lock and hook snapshots are retained under [upstream/](upstream/). The generator carries
the upstream Apache-2.0 notice. [Storage selection](storage-selection.json) binds scratch,
native builds and caches to the mounted external SSD's registered Linux build image.
The source copy is named in summary.json; no reference repository was written or built.

## Measured checks

- Actual Bazel 8.7.0 outputs match all three untouched baseline JSON objects exactly:
  [configuration equivalence](configuration-equivalence.json).
- The integration tar retains `tests/switch_run_target/etc/mw_com_config.json` with the
  original effective JSON: [package check](packaged-configuration-equivalence.json).
- Five native targets pass, covering **113 test cases**, zero failures/errors/skips:
  `control_provider_UT`, `ilm_control_UT`, `lm_control_impl_UT`, `lifecycle_config_tests`
  and `switch_run_target`. XML/logs are retained in [logs/test-results/](logs/test-results/).
- Buildifier 8.5.1 format/lint checks pass for all four changed Starlark/BUILD files;
  its executable hash was verified against release metadata.
- [Portable patch check](portable-patch-check.json) confirms clean application and exact
  changed-source equality in a second checkout.

Initial tests compiled but two aborted with `Address already in use` at `LoLa_2_12_QM`.
The host already exposed that abstract Unix socket. Serial execution alone did not resolve
it. Isolating test network namespaces using `--sandbox_default_allow_network=false` resolved
the conflict; native IDs/configurations were not modified. Failed attempts and the passing
isolated run remain in [logs/](logs/). Existing upstream tooling-version/deprecation warnings
remain visible; analyzer cleanliness or MISRA compliance is not claimed.

Every native command uses pinned disposable Bazelisk 1.29.0, storage-bound environment and
explicit output/cache root. [run-bazel.py.txt](run-bazel.py.txt) retains the executed wrapper.
JSON command records under logs/ contain exact arguments, exit codes, durations and raw log
destinations. `--lockfile_mode=error` was used. Reproduction requires fresh storage selection
and path rebinding; retained disposable absolute paths are provenance.

## Guarded comparison preparation

[Comparison summary](comparison/preparation-summary.json) binds the patch/source, review
output schema, policy and explicitly rendered `score-verification` Skill. Exact source declares
`feat_arc_sta__lifecycle__cfg_params_static`, version 1, status `valid`, ASIL_B/security;
this citation is context, not native-export validation or acceptance. Source/consumer inventory
does not claim complete native transitive impact or applicability closure.

The deterministic classifier conservatively selects **S3** because the configuration includes
safety/security settings. Both candidates have identical task instructions, constraints,
required checks and pending human review. The baseline includes complete original configurations;
the optimized candidate uses exact current source and checksum-bound original/equivalence
evidence. Prepared input bodies are 22,017 and 19,593 UTF-8 bytes. These offline sizes are not
tokenizer counts, full native request sizes or live savings. Runtime overhead needs measurement.

Both workflow packages passed pinned real Fabro native validation. Embedded Sphinx `{{…}}`
initially triggered template evaluation; raw blocks inside the prompt attribute preserve that
literal source and pass validation. Initial failures remain retained. A duplicated full patch
was replaced by an immutable reference to fit the baseline body within the context ceiling.

The candidate governor refuses admission: no new paid instruction or protected admission
exists. The local stage guard reports `STAGE_ADMISSION_REFUSED`; **zero provider calls** were
made. Validation is conformance only, not real agent-stage execution. Both previous Flash
experiments and ledgers remain closed and untouched.

T033 needs exact target engineering review, native impact/applicability closure, fresh private
activation/transport bindings and bounded Flash observations. This is one real cleanup case,
not every B1–B5 scenario. QNX execution was not measured. Future use must rebind paths/hashes
and enforce the full serialized request ceiling, including overhead.

Final fabric checks: **97 tests passed**, frozen sync, Ruff format/lint, mypy (148 files),
foundation consistency and package build passed. The initial pytest base directory was outside
the selected TMPDIR, causing the transport storage guard to refuse one fixture; a fresh base
inside the selected temporary area passes. Both attempts remain in logs/. No runtime/source
storage rule was weakened. Full-suite validation and engineering acceptance are not claimed.

[manifest.json](manifest.json) pins the retained artifacts. Human-owned markers and all 20 T032
subjects remain unchanged. No upstream comment, assignment, PR, commit, push, publication,
merge, release or deployment was performed.
