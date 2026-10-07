# Supervisor review — Issue #741: Move the Rust COM API example to the tutorial folder

Independent, read-only review of the scope, proposed patch and measured evidence.
This report **does not modify any other artifact** and adds no source change.

| Field | Value |
| --- | --- |
| Issue / repo | `eclipse-score/communication` #741 (`open`, label `rust-api`, 0 comments) |
| Baseline | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Mode / scope | `implementation`; Linux only (`linux_x64`); DeepSeek Flash only; no QNX |
| Review method | file tools only: `read_file`, `glob`; `shell`/`grep`/`web_fetch` re-probed and independently confirmed blocked |
| Measured subject hash (attempts 0–3) | `bed9d5e017cff81a6adca2dedeca73e106853858834f31ebfc2d5b24180c42ac` (unchanged) |
| Technical completion | **Not implemented** — change fully specified, never applied |
| Engineering acceptance | **pending** (no authorized human decision; no passing native evidence) |

## 1. Verdict

**The issue is NOT fixed in this workspace. Do not treat any report here as an implemented fix.**
The deliverable chain (`scope.md` → `implementation.md` → `correction-1..3.md` → `review-packet.md`)
is a **source-accurate change specification plus a measured blocker report**, which is the correct
outcome given the granted boundary. The measured native results are **failed** and remain failed;
acceptance remains **pending**.

The proposed change specification is, on independent inspection, **correct and minimal**. The
blocker it records is **real and independently reproducible**. The principal defects in the delivered
material are (a) the un-run negative/absence checks and (b) residual unmeasured negative search —
neither of which changes the blocker disposition.

## 2. Independent re-measurement performed in this review

All observations below were made first-hand in this session; none is carried on trust.

| Claim under review | Independent method | Result |
| --- | --- | --- |
| 13 source files still at old path | `glob score/mw/com/example/com-api-example/**` | all 13 present (`BUILD`, `USAGE.md`, `main.rs`, `tests_using_tokio_runtime.rs`, `src/{lib,consumer,producer}.rs`, `com-api-gen/{BUILD,com_api_gen.rs,vehicle_gen.cpp,vehicle_gen.h}`, `etc/{logging.json,mw_com_config.json}`) |
| Destination holds only a placeholder | `glob` + `read_file .../doc/tutorial/com-api-example/BUILD` | single comment-only `BUILD`, defines **no targets** |
| `score/mw/com/example/` has no own BUILD | `glob score/mw/com/example/**` | only the `com-api-example` package; `example/` subtree has no BUILD |
| `shell` blocked | `shell: pwd && git status` | `Bound Rust workspace/file-tool boundary` |
| `grep` blocked | `grep com-api-example score` | `Bound Rust workspace/file-tool boundary` |
| Source `*.json` unreadable | `read_file` on `etc/logging.json`; on a **non-existent** `etc/*.json`; on a non-existent `etc/*.txt` | boundary denial for `.json` (even absent); `File not found` for `.txt` |
| No delete/rename primitive | tool inventory (`read/write/edit/glob` only; `shell` denied) | confirmed — a pure "move" cannot remove the 13 old paths |
| Workflow wildcard claims | `read_file` `.github/workflows/_linter.yml`, `_build_and_test_gcc15.yml` | clippy via `aspect lint ... -- //...` with `--config=clippy`; build/test `bazel build/test --config=ci //...` |
| `CODEOWNERS` has no path entries | `read_file` `.github/CODEOWNERS` | default owners only (`* @castler …`) |
| Config/toolchain binding | `read_file` `.bazelrc` | `common:linux_x64 --config=linux_x64_gcc_15`; Ferrocene `ferrocene_x86_64_unknown_linux_gnu` |

Note on the `.json` guard: `read_file` of `.rust-queue/context/comments.json` **succeeds**, so the
guard is path+extension scoped (workspace source `.json` blocked), not purely extension-based as
`correction-2.md` §4.2 phrases it. This is a wording imprecision only; the material conclusion
(the example's two configs cannot be read) is verified and stands.

## 3. Scope review

- Baseline reconciliation is **correct**: the move has not been performed; the tutorial tree
  contains only `BUILD`, `README.md`, `README.rst` and the C++ `chapter_*` packages.
- The issue text was treated as data. The issue's only request is a relocation; `How` is empty and
  the estimate is `0`. The scope report did not over-reach (no docs registration, no rename of the
  C include guard, no logic edits) — all justified as minimal/out-of-scope.
- Requirements/architecture impact: the template checkbox is task data, not proof. Independent
  inspection of the package finds no requirement/design/safety/qualification identifier. The
  assessment "location-only plus self-referential path strings" is corroborated by the files.
- **Gap (carried):** an exhaustive cross-repo text search was not performed (`grep` blocked). The
  claim that no other package references the old label is **reasoned, not measured**. See §6.1.

## 4. Patch / change-specification review

The specification in `implementation.md` §4 was checked against the actual baseline files; every
edit is accurate and sufficient for a pure relocation:

| Claimed edit | Verified against | Verdict |
| --- | --- | --- |
| `BUILD` deps label ×3 (L22 lib, L43 binary, L69 test) | `score/mw/com/example/com-api-example/BUILD` | accurate |
| `BUILD` `env MW_LOG_CONFIG_FILE` L38 | same BUILD | accurate |
| `data = ["etc/*.json"]` package-relative, unchanged | same BUILD | correct — no edit needed |
| `main.rs` L72 clap `default_value` | `main.rs` line 72 | accurate |
| `tests…rs` L26 doc comment, L44 `TEST_CONFIG_PATH` | `tests_using_tokio_runtime.rs` | accurate |
| `USAGE.md` 11 occurrences (L55,67,74,77,80,83,86,89,104,107,111) | `USAGE.md` | all 11 confirmed |
| `USAGE.md` L124 relative-link rebase `../../` → `../../../` | path arithmetic | correct for the deeper location |
| L124 target `score/mw/com/impl/rust/com-api/README.md` absent | `glob score/mw/com/impl/rust/com-api/**` | absent — pre-existing dangling link; correctly not "fixed" by inventing a file |
| `com-api-gen/BUILD` visibility `//score/mw/com:__subpackages__` still valid | `com-api-gen/BUILD` | correct — new path is still under `score/mw/com` |
| `crate_name = "com_api_gen"` unchanged ⇒ `Exhaust` ID unaffected | `com-api-gen/BUILD` | correct |

The refusal to apply a partial/duplicate tree is **endorsed**: writing the readable files without
the two unreadable `etc/*.json` configs would leave the old package alive (a copy/duplicate, not a
move) and produce a broken destination whose `data`, `MW_LOG_CONFIG_FILE` and test path reference
missing files — i.e. it would trade a *query* failure for a *build/test* failure while fabricating
completeness. That is exactly what the workflow's "do not change code merely to make a check
succeed" prohibits.

### Process/cleanliness observation

Two probe artifacts exist outside the intended change and cannot be removed by the agent:
`score/mw/com/doc/tutorial/com-api-example/BUILD` (comment-only placeholder) and
`.rust-queue/reports/boundary-test.txt`. The placeholder defines no targets, so it is build-safe,
but it **is** a source-tree write and must be removed/overwritten by the privileged stage. It is
disclosed in the reports; noted here as a minor hygiene gap, not a correctness defect.

## 5. Measured-evidence review

`native-check-summary.json` (operator/collector-supplied) and the four stage outputs agree:

| Attempt | Native result sha256 | kind | query exit | passed | infra error |
| --- | --- | --- | --- | --- | --- |
| 0 | `f1ee60ee494c0f6d2131e3310d4a972ffafbcb6af9202aa81b67eca3653ea9d9` | measured_native_command | 7 | false | null |
| 1 | `77a10769d8a3b5ff1f653b383a3831df1faadf44480c7ea547f8b9f2c4ac041b` | measured_native_command | 7 | false | null |
| 2 | `078ca7b7e2106870656228080f03329a71b4033cc878d83eee4d98e5493b2b8b` | measured_native_command | 7 | false | null |
| 3 | `d19d180aaabdd9aa50e0be98e2c6c9f6910c3d76d0ba382c3c938a1c02bcc189` | measured_native_command | 7 | false | null |

Findings:

- The failure is **genuine source state**, not infrastructure: `infrastructure_error: null`, exit 7,
  `timed_out: false`, and the message names the missing package
  `score/mw/com/doc/tutorial/com-api-example/com-api-gen`.
- **No subject change was ever measured**: `measured_subject_hashes_sha256` is identical across all
  four attempts, consistent with "the move was never applied".
- The first query target (`.../com-api-example:all`) resolves only because of the probe placeholder;
  the `com-api-gen` subpackage is absent. This matches the actual workspace state in §2.
- Attempts 0–3 are a **repeated unchanged failure**; the correction budget (3) is exhausted, so
  terminating with a blocker is the correct protocol outcome.
- `native-check-summary.json` currently holds **attempt 3**; attempts 0–2 are preserved as history in
  the check-0..2 job outputs and in `correction-1..3.md`. Failed evidence is preserved, not erased.
- `engineering_acceptance: "pending"` is present in the summary and is preserved by this review.

## 6. Gap register

### 6.1 Correctness / acceptance-trace gaps (material)

1. **No negative/absence assertion.** The issue's primary acceptance criterion — "the example no
   longer lives under `score/mw/com/example/`" — is **not checked**. `check-plan.json` only queries
   the *new* labels. Re-running that plan against a duplicate (old package still present, new package
   added) would still **pass**, even though the move did not happen. A `query` on the old labels
   `//score/mw/com/example/com-api-example:all` and `.../com-api-example/com-api-gen:all` (expected
   to fail/return nothing) should be added by the deterministic stage that applies the change.
2. **Exhaustive reference search not measured.** The negative "no other BUILD/doc/workflow references
   the old label" is reasoned, not measured (`grep` blocked). Corroborated but not proven by
   leaf-target reasoning and by `CODEOWNERS`/CI wildcards. Residual risk remains.
3. **Docs check does not exercise the moved docs.** `//score/mw/com/doc/tutorial:tutorial_rst` lists
   only `chapter_*` packages, and the moved `USAGE.md` is in no `sphinx_docs_library`. The `docs`
   check can therefore pass while the relocated usage documentation remains unregistered. This is
   consistent with the deliberate "docs registration OPEN" decision, but it means the "docs/usage
   references valid" criterion is **not** covered by the current plan.

### 6.2 FFI / concurrency / trace / qualification

- **FFI:** the moved `com-api-gen` links C++ (`vehicle_gen_cpp`, `register_interface`) through
  `link_std_cpp_lib`. A path relocation changes no ABI/layout/ownership/panic boundary; the C include
  guard is cosmetic and left unchanged. No FFI regression is introduced by the intended change —
  **but no FFI evidence exists**, because the move was never compiled. This is a qualification gap
  only in the sense that nothing has been built/tested; no FFI defect is asserted.
- **Concurrency:** the only concurrency-relevant artifact is the Linux-only Tokio multi-thread
  integration test (BE issue #794 sanitizer findings; BE issue #1278 QNX build). It is unchanged by
  the move; the plan correctly excludes sanitizer configs and QNX. No concurrency evidence was
  measured (no test executed).
- **Trace:** no native requirement/design/safety ID was sourced inside the package; the reports keep
  such IDs **unknown rather than invented** — correct. `api_surface.lock.json` and other locks/pins
  are untouched by the move.
- **Qualification:** no tool/compiler qualification claim is made. Ferrocene's presence in
  `.bazelrc` does not establish qualification; the reports correctly make no such claim.

## 7. Disposition

- **Engineering disposition: BLOCKER (unchanged).** The intended change cannot be performed with the
  granted boundary (no delete/rename; source `.json` unreadable; `shell`/`grep`/`web_fetch` blocked —
  all independently re-confirmed here).
- **Technical status: NOT IMPLEMENTED.** This chain is a change specification + blocker report, not a
  delivered fix. Do not describe #741 as fixed.
- **Acceptance: PENDING.** Failed evidence is preserved; no passing evidence is asserted, and none
  can be manufactured by tests or workflow success.

## 8. Required next actions (privileged stage / humans)

1. Provide an actor with filesystem authority (or add a delete/rename capability and read access to
   source `etc/*.json`). Apply `implementation.md` §4 exactly: the 13 byte-preserving renames, the 6
   reference-edit groups, removal of the emptied `score/mw/com/example/` tree, and removal/overwrite
   of the probe placeholder `score/mw/com/doc/tutorial/com-api-example/BUILD` plus
   `.rust-queue/reports/boundary-test.txt`.
2. **Strengthen the plan before re-running** (recommendation, not a change to existing artifacts):
   add a negative `query` on the old labels and a workspace-wide reference search; and either register
   the moved `USAGE.md` in a `sphinx_docs_library` or record an explicit, human-approved decision that
   the sample stays unregistered.
3. Re-run `check-plan.json` on `config=linux_x64` and write a fresh `native-check-summary.json`.
4. Human reviewers decide offline: target leaf name (`com-api-example` vs a Rust-specific name);
   docs registration; and whether a competing upstream PR already performs the move (network was
   blocked, so this is unverified).

Preserve the existing `scope.md`, `implementation.md`, `correction-1..3.md`, `review-packet.md`,
`check-plan.json` and the failed `native-check-summary.json` as history. Acceptance remains pending.
