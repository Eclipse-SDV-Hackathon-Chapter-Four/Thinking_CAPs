# Native Rust verification

Use the selected repository revision as the command source. The observations below
guide discovery; they are not a universal target matrix or accepted language profile.

## Build and toolchain discovery

- Inspect Bazel version, MODULE/lock, registries/overrides, crate index, BUILD targets,
  `.bazelrc` imports and local configuration. Follow policy/toolchain repositories at
  the resolved pins and retain their configuration/license hashes. Discover aliases
  and generated targets from rules/query results rather than invent names.
- Resolve the compiler actually selected for each compilation action, including the
  host compiler for procedural macros versus target compilation for generated code.
  Record compiler/LLVM/sysroot/library versions, binary digests, target triples, edition,
  features, optimization/panic flags and policy inputs. Query/analysis itself can fetch
  and execute repository rules: inspect those rules and use the isolated copy first.
- Discover formatting and Clippy wrappers in native CI. Use the pinned Rust policy
  settings rather than a generic lint list or blanket warnings override. Changes to
  allowed/forbidden features, unsafe permissions or lint exceptions need native rationale.
- Cargo is appropriate only when maintained native manifests and instructions exist.
  Its lock, features, target and toolchain must match the native build. An exploratory
  Cargo harness, rustfmt, macro expansion or Miri result is supplementary evidence unless
  native obligations explicitly support that route. Do not install nightly or another
  toolchain merely to obtain an expansion/Miri command.

Shared storage implementation supplies `CARGO_TARGET_DIR`, tool temporary/cache directories
and Bazel cache environment overrides. It deliberately leaves authentication at home.
Do not redirect `CARGO_HOME` or `RUSTUP_HOME` wholesale without separating private state.
Validate the run root before subprocesses; explicitly bind Bazel output/repository/disk
cache paths when the inspected tooling requires them. A new `storage exec` allocates a
new workspace; it is not a resume/guard mechanism for an existing workspace.

## Choose checks from the affected scope

| Change surface | Verification to discover and bind |
| --- | --- |
| Rust library/API | Native build, unit tests, downstream compilation, rustdoc/examples and applicable lint/format checks |
| Macro or dependency | Actual host/target compilation, supported positive/negative invocation cases, generated API compatibility and resolved dependency inventory |
| Unsafe/FFI | Safety invariants, layout/ABI/lifetimes/ownership/threading/error boundaries, Rust and affected C++ integration checks; supported dynamic checks where required |
| Communication behavior | Runtime mock/unit tests plus affected producer/consumer and IPC integration tests; required platform variants |
| Native documentation/qualification | Docs/metamodel/trace checks and complete applicability/qualification artifacts; pending human decisions retained |

Coverage targets/thresholds, sanitizer use, Miri and platform obligations come from
the project's selected verification plan. Compiler availability alone establishes none
of these capabilities. Do not substitute fixture runtime tests for production integration
or claim safety acceptance from line coverage. Preserve unavailable/failed metrics.

Enumerate every expected check with its native source, command/configuration, subject
hashes, execution or omission status and evidence. Broad wildcard success can omit
`manual`, filtered or target-incompatible tests: enumerate them explicitly. Documentation
examples marked `ignore` do not become tested merely because rustdoc runs.

## Inspected communication example (2026-10-05)

At `e3d126c2d7569345cf5f790310702eb00cd86b06`, source declares Bazel 8.7.0,
`rules_rust` 0.68.2-score, `score_toolchains_rust` 0.10.0 and `score_rust_policies` 0.0.5.
`.bazelrc` selects Ferrocene for the Linux configuration; static-analysis config
selects the policy's `clippy_strict` aspect. Recheck at the task baseline before use.

Candidate targets directly observed in `score_com_concept/BUILD` are:

- `//score/mw/com/rust/score_com_concept:score_com_concept-test`
- `//score/mw/com/rust/score_com_concept:score_com_concept-macros-unit-tests`
- `//score/mw/com/rust/score_com_concept:score_com_concept-macros-tests`

The last target has a `manual` tag and documented native-linking limitations. The first
is Linux-only. These are source-discovered candidates, not executed checks or the full
downstream denominator. Discover integration consumers under `basic_rust_api`, examples
and FFI packages before deciding the final scope. Native analysis/build success and tool
qualification for this workflow have not been measured during skill authoring.

## Source anchors

- [S-CORE Rust guideline at the fabric's score pin](https://github.com/eclipse-score/score/blob/e2373d822fc2f6e9a3f8a0538904f3faa39309ea/docs/contribute/development/rust/coding_guidelines.rst): native document `doc__rust_coding_guidelines`, version 1, status `valid`; resolve project applicability separately.
- [Communication MODULE](https://github.com/eclipse-score/communication/blob/e3d126c2d7569345cf5f790310702eb00cd86b06/MODULE.bazel), [build configuration](https://github.com/eclipse-score/communication/blob/e3d126c2d7569345cf5f790310702eb00cd86b06/.bazelrc), [test definitions](https://github.com/eclipse-score/communication/blob/e3d126c2d7569345cf5f790310702eb00cd86b06/score/mw/com/rust/score_com_concept/BUILD), [lint configuration](https://github.com/eclipse-score/communication/blob/e3d126c2d7569345cf5f790310702eb00cd86b06/quality/static_analysis/static_analysis.bazelrc).
