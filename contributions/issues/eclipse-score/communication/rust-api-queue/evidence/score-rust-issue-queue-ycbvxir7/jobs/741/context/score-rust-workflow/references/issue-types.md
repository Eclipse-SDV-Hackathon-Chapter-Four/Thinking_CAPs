# Choose checks for the Rust issue

Use only relevant branches below. An issue can span several surfaces; derive check
obligations from its native scope and process, rather than running this entire list.
The repository's existing framework and permitted execution determine the test method.

## Defect or behavior correction

Reproduce the reported failure on the selected baseline and identify the native
requirement/contract that defines correct behavior. Where a regression test is useful,
show it detects the original defect and verifies the corrected case plus relevant
boundaries. A build/setup failure is not a reproduced product failure. For intermittent
failures, retain the observed frequency, seeds, timing and reproduction limitations;
do not turn an unobserved outcome into a passing regression.

## Feature, API or refactoring

Bind intended semantics and compatibility constraints before implementation. Discover
public re-exports, downstream users, feature flags and trait/type/lifetime relationships.
Preserve observable behavior for a refactor; evidence a required behavior change for
a feature. Validate error contracts and representative downstream compilation, native
examples and documentation. Generated APIs additionally use the dependency/macro guide.
Update native requirement/design/verification artifacts only where impact requires it.

## Unsafe, memory or FFI boundary

Record each affected unsafe invariant and its callers: validity, initialization,
alignment/layout, ownership, aliasing, lifetimes, pinning, thread transfer and destruction.
For FFI, bind representation/ABI, allocation/deallocation owner, C++ object lifetime,
callbacks, errors and panic/unwind boundaries. Include relevant Rust and C++ consumers.
Use supported dynamic checks where supplied obligations require them; unavailable Miri
or sanitizers stay unavailable. Avoid declaring code sound from compile success or from
the absence of `unsafe` in the changed lines while callers/generated code remain affected.

## Concurrency or asynchronous behavior

Trace shared-state synchronization, `Send`/`Sync` obligations, atomic ordering, lock
ordering, callback reentrancy, cancellation/drop, task shutdown and resource ownership.
Choose deterministic schedules or controlled reproduction when native tooling supports
them; supplement with required stress/integration checks. Verify error, timeout and
cleanup paths as well as success. Sleeps and a short passing stress run do not establish
absence of races/deadlocks. Record residual nondeterminism and actual coverage.

## Platform, build or performance

Bind the affected targets, host/target compiler separation, features, architecture,
sysroot/native libraries and deployment assumptions. Preserve supported platform
obligations and report missing variants. For performance changes, bind the native
requirement, workload, baseline/candidate environments, repeated measurements and
variability; a one-off timing or synthetic fixture is not production acceptance.
Keep dependency/lock updates explicitly scoped and reproducible.

## Documentation, compliance or dependency-only work

Identify the native artifact and source-backed claim being corrected. Validate relevant
docs/metamodel/trace and example compilation. A prose-only issue may end with an
assessment rather than a source patch. For crate/tool qualification or substitution,
read the dependency/macro reference and preserve every unaccepted classification.
Do not impose dependency option comparisons on unrelated defects or documentation edits.

## Review packet

All branches finish through the common packet: issue acceptance mapping, native trace,
patch/assessment, expected checks and complete evidence bindings, failures/gaps and
pending offline decisions. Unresolved scope prevents a readiness claim, while authorized
implementation and evidence collection can proceed within the known scope.
