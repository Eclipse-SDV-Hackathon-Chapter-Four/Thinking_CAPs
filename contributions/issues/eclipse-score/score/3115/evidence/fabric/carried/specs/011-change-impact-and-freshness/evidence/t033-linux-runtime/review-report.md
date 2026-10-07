# Compatible Linux runtime and real B2/B3 oracle checkpoint

Increment 011 remains incomplete. No paid provider request or engineering acceptance is recorded.

## Measured outcomes

- All 32 historical packets / 8,753 sealed files, 310 fabric source/test files, 20 reviewed T032 subjects, original/candidate native sources and the 3,484-file runtime match the saved checkpoint. [Verification](resume-verification.json) binds counts and fresh storage capabilities.
- Cached Debian provides glibc 2.36 and is incompatible with the pinned Ferrocene driver. A checksum-bound [Canonical Ubuntu Noble root image](https://partner-images.canonical.com/oci/noble/current/) supplies glibc 2.39 and libstdc++ 14.2.0. [Acquisition](runtime-acquisition.json), [provenance](runtime-provenance.json), [inventory/notices](runtime-inventory.json), [namespace libraries](runtime-overlays.json) and [actual preflight](runtime-execution-preflight.json) distinguish source verification from runtime execution. The checksum signature was not verified because the local cloud-image keyring is absent; no signature claim is made. Host libraries remain untouched.
- The exact original B3 target completes LLVM coverage in 82.955 seconds: 3 cases pass, 0 fail/error/skip. `control_provider.cpp` has 92/182 covered lines, 30/56 covered branches and 8/12 functions. [Raw baseline packet](B3-baseline-coverage/) and [metrics](B3-baseline-coverage.json) are retained.
- The [B2 witness](B2-allocation-witness.json) calls the actual unchanged public getter/setter 16 times each after warmup: each makes 32 C++ allocations and preserves its result. Only C++ new/new[], including aligned allocation, on the calling thread is counted. A test peer supplies queue responses; production Graph handling/concurrency is not qualified. [Held-out changes](held-out-oracles/B2.patch) include only a test target, observer and friend access for queue setup/consumption. Native execution takes 95.089 seconds. Zero-allocation behavior remains unmet; no correction is supplied to a model.
- The [B3 held-out test](held-out-oracles/B3.patch) executes the previously uncovered real query handler and checks exact available status/target. Correct LLVM coverage completes in 103.140 seconds with 4 passing cases: 98/182 lines, 31/56 branches and 9/12 functions. [Raw packet](B3-gap-coverage/) and [metrics](B3-gap-coverage.json) remain distinct from baseline. The [wrong-status mutant](held-out-oracles/B3-mutant.patch) fails exactly the new test while all three old tests pass. [Failure witness](B3-mutant-witness.json) retains native exit 3 and actual XML/logs. This is a direct handler oracle, not RPC coverage or completion of issue #685's full 100% request.
- [Native mapping inventory](native-mapping-inventory.json) measures 4 source-code annotations, 2 component/build associations and 44 documents realizing work products in the unchanged 144-record Lifecycle export. Placeholder/unknown remote source links and native statuses remain explicit. Complete accepted source-to-Need and required-work-product denominators remain unavailable.
- Fresh original `//:needs_json` fails at the exact Aspect rules_py v1.4.0 unpack binary. [Readiness](next-prerequisite/readiness.json) binds the native SHA, declaration/license sources and cache presence; [successor limits](next-prerequisite/proposed-limits.json) remain unstarted. Continue cache/provenance acquisition without another go. Full reverse closure remains QNX-blocked and QNX stays skipped.

## Preserved unsuccessful evidence

The image's absolute symlink triggers a safe initial tar extraction refusal. A fresh extraction converts only image-absolute links to rootfs-relative equivalents under Python's data filter; the original inventory and 20 normalizations are retained. Initial buffered metadata hashes were measured before stream close; that erroneous record is retained separately, and complete closed-file hashes are recorded in acquisition/provenance. A runner option-order mistake selected GCC for stage030: all four tests ran, but no profraw was emitted and a reporter dependency failed at a compiler warning. [Correction](coverage-operator-correction.json) retains both scripts and the raw failure; stage032 restores the exact original native profile ordering without changing native policy or scope.

## Boundaries and continuation

The existing and fresh workspaces stay bound to image UUID `11c42dee-73a3-4c2b-ab42-a0440011d9e0`, device 1819, backed by SSD UUID `002B-CE31`; image registration remains 1 TiB. Credentials/private state stay internal. No Docker/Fabro/provider server, scheduler, global storage change, reference build, publication, push, merge, release, deployment or increment 012 is started. Each native stage has one finite attempt, network isolation, exact-only local transport, QNX denial and captured actual process closure. Historical 113-case checks per arm and 223 fabric tests/Ruff/mypy are carried only through unchanged hashes; no fresh equivalent claims are made.

B1 remains unselected. B2 production correction and native behavioral/concurrency applicability, complete B3 scope, accepted B4 requirements/interfaces, accepted B5 coupling/applicability/reviewer roles, complete native expected sets, fresh explicit paid budgets, real paired provider usage/savings and offline T033 acceptance remain open. T154/T156 and human markers remain unchecked. Keep evaluator patches outside future agent inputs. The session checkpoint follows the owner's context/credit-efficiency preference; no context percentage or actual billed credits are exposed.

## Checkpoint verification

Fresh frozen foundation, Spec Kit prerequisites, package build, diff and trace audit pass.
All 32 historical packets / 8,753 sealed files and unchanged source/runtime subjects
match again; 16 operator snapshots compile. Original host library hashes match.
Owned native processes are absent, mirrors closed and the previous workspace stage
limits restored. The report scanner's initial KeyError/AttributeError is preserved;
its first v2 invocation omitted PTY metadata, an explicit capture gap with no output
reconstruction. The final typed scanner and captured validation complete successfully.
See [verification](preservation-final.json), [process closure](process-closure.json)
and [validation](validation-results.json).
