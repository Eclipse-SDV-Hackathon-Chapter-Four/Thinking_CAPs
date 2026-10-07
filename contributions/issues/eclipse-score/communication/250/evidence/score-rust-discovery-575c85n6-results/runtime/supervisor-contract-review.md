# Communication #250 — independent contract and control review

The operator contract is substantially source-grounded and bounded to a proposed Linux typed-wildcard implementation. Two material review points were identified and refined by the operator before implementation entry: deployment ownership must extend beyond discovery to retained handles/proxies, and absence of a required positive regression plan must fail the check stage. Source correctness and actual positive coverage still require independent review. No implementation correctness, passing native measurement, complete #250 semantics or engineering acceptance is asserted here.

Read-only review of task, graph, hooks, guard, driver, launcher, native source and preflight was performed. No source/control/ledger edits, native execution, retry, model call or dispatch was performed by this supervisor. Only this report was written. `plan.md` was absent at the final preparation check, so its design and mappings remain unreviewed; inspect it and the final patch when supplied.

## Authority and execution boundaries

Selected baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`; native run: `01M49GR67QSRKDPRYJVE91W04G`. Shared storage validation succeeds for the selected SSD root. Preflight records 2,878 verified baseline subjects and the private rootless daemon with DockerRootDir on this root. Source hooks inspection reports none and hooksPath `/dev/null`; credentials/private state remain outside the model workspace.

The graph has exactly three agent nodes: plan, implementation and supervisor. They explicitly select DeepSeek Flash, disable project memory, set zero retries and one visit, and supply no engineering acceptance node. Descriptive metadata claiming four agent nodes is a bookkeeping discrepancy; it cannot establish four actual invocations. Terminal events/usage will establish actual calls.

`tool_guard.py:14–20` charges the original #250 correction on implementation entry, blocks duplicate implementation entry and preserves the maximum of three. At this review's observation the ledger is still 1/3 used with no started implementation; entry is intended to move it to 2/3 with one remaining. This is an implementation allowance, not acceptance or a new budget. #1261 remains 1/3, #173 2/3, and the distinct #560 Codex allowance 1/3. No transfer or extension is authorized.

File tools are constrained to the resolved workspace, `.git` is denied, reads are bounded to 200 lines, and the supervisor/plan can write only their reports. Only implementation can write the allowed source paths and regression plan. Protected filenames, source checks and report-only export remain in place. Wide allowed prefixes necessarily permit meaningful BUILD/API changes; final review must still check that no lint suppression, licensing removal, incompatible policy or unintended source change is introduced within those paths. Prompt assertions alone are not proof of preserved semantics.

## Semantic and ownership findings

**C1 — retained-result ownership is essential.** The initial prompt required copied deployments to survive a synchronous call and the async StopFindService lifetime. That minimum is insufficient if returned results outlive discovery. Native `score/mw/com/impl/bindings/lola/service_discovery/known_instances_container.cpp:84–85` builds each wildcard HandleType from the query's InstanceIdentifier plus the concrete instance ID. `handle_type.cpp:52–53` stores that identifier by value. `instance_identifier.h:179–181` describes its nonowning pointers into deployment records. Copying the identifier does not copy/own those records.

Disposition: the implementation must retain stable deployment ownership with every emitted native handle, retained Rust builder and constructed proxy, or use equivalent runtime-owned stable storage. Destroying a local synchronous owner on return, or an async owner at stream/discovery drop while a builder or proxy survives, is not safe. Ownership must also survive callback quiescence, stop/error paths and vector/map relocation. Require a regression that retains a result, drops discovery, then constructs/uses the proxy, with multiple instances distinguished by concrete IDs. Do not regard passing discovery-only tests as this proof. The refreshed task now contains `mandatory_lifetime_refinement` with this obligation; retained `steering-response.json` records successful delivery to the live plan stage. This refines the contract, not the implementation evidence.

**C2 — typed Any is not system-wide heterogeneous discovery.** `find_service<I>(Any)` can cover all instances of interface I; it cannot report arbitrary interfaces through the same typed descriptor. The #250 comments expose both expectations, and #1261 expressly asks for an interface-independent updating stream. Contract prompts correctly preserve this distinction. Typed implementation must not claim #250's broader comment, #1261 completion or discovery of every system service without a separate accepted universe/API contract.

**C3 — mapping and deployment universe require explicit errors.** An interface string UID is not a native service short-name. The contract correctly rejects inventing a name conversion, concrete Runtime downcasts and enumeration of only configured Specific identities as wildcard discovery. Review explicit interface-to-native metadata registration, duplicate/conflicting mappings, unmapped interfaces, version/quality/binding selection and snapshot behavior when AddConfiguration extends the runtime. No matching service, unsupported mapping, configuration failure and successful empty discovery must remain distinguishable where the API promises errors. Genuine LoLa wildcard deployment must clear the instance ID; native concrete identities, not the wildcard query or a fabricated producer InstanceSpecifier, must identify results.

Specific behavior and inherited mock compatibility must remain intact. Required bridge review includes ABI/layout, callback ownership and Send/Sync assumptions, no unwind across FFI, no panic substituting Any, propagation of native start/find/stop errors, safe callback cancellation and proxy creation for actual results. Public API/error additions require downstream compatibility analysis; the #560 allowance does not authorize fixes here.

## Measurement and control dispositions

**C4 — required regression presence and semantic coverage are separate.** The initially inspected driver recorded a missing regression plan but returned the native collector's exit code. The operator preserved the former control as `driver-before-coverage-refinement.py` and refined the active driver: line 46 now exits 1 when native checks succeed but the regression plan is absent; lines 44 and 53 record plan presence, and export states actual positive coverage requires independent review. This resolves the absent-plan stage-exit defect. The native `passed` field continues to describe measured command outcomes rather than accepted completeness. Final review must mark implementation incomplete if the dedicated regression is absent, unexecuted, skipped, merely a renamed existing target, or fails to exercise genuine positive Any behavior. Graph terminal success must not erase the gap.

The guard validates regression-plan structure, native label prefix, kind and config, not semantic content. Independently inspect source assertions and raw child cases. Required positive obligations from the contract are: multiple offered same-interface instances; exclusion of another interface; empty/no offer; initial discovery and later offering where supported; identity and working proxy construction; discovery/drop callback lifetime; retained-result lifetime from C1; Specific compatibility; error propagation. Stub-only or always-empty/NotSupported cases do not satisfy this inventory.

The native compatibility plan covers runtime tests, concept/macro units, existing sync/async integration and two-library Clippy. `linux_launcher.py:81–82` correctly normalizes kind=lint to the Clippy configuration despite the plan's linux_x64 config field. Tests disable cached test results. Final evidence must prove actual aspect execution, raw analyzer findings, native child counts and all expected integration cases. Wrapper XML counts are not Rust child counts. These selected checks do not cover all changed FFI/native runtime code analysis, all examples/downstream dependents, manual doctests, sanitizer, QNX or qualification; omissions require dispositions.

Source boundary checks run before and after measurement, preserve protected subjects and compare measured hashes against exported final subjects. Retain missing/deleted subjects and additions explicitly, full patch and raw failures. No automatic repair or extra attempt follows from failed implementation/check/supervisor stages. Export/exit routing can reach a terminal lifecycle even on failure; technical verification and engineering acceptance must remain separate.

## Input bindings

| Input | SHA-256 |
| --- | --- |
| `jobs/250/task.json` | `a685c8988b69280d3bbedba6f0cafa7c3cf252943d55102908e6713d2800b545` |
| `jobs/250/workflow.fabro` | `a2692e68da89688f6d05c01edfce6dc4d4a25b43d2261cf1a176c07e4abf1139` |
| `jobs/250/workflow.toml` | `4633c67fc7c8e7cff2235c1f7d1900d039b11a2db1a98411e1546717ee272da8` |
| `tool_guard.py` | `416ebb5847c2687461943c2b69e33abd238ccede7499c896718e492ae38ee5fd` |
| `driver.py` | `329ec0289fee7b090745a42439c130eec9a99dd5c8ecc30d2932276649a7186e` |
| `linux_launcher.py` | `b530ccceff2bce44b3760478142dc6a85efa0c8f013fe79639ba976abdb6e59d` |
| `check-plan.json` | `511e9f908b21047fc8e8c21831c6e9b8443bf72865c4b9d07d18ea9f469b6374` |
| `source-subjects.json` | `0ef301a348a177d1615221543a6cc4573c838c75ae8f72e6616dd504d73f9b11` |

Recommendation: carry C1–C4 into the upcoming plan/patch review and use measured native evidence for dispositions. Do not approve engineering acceptance or claim issue closure from this contract review. Await the authorized implementation and terminal evidence without additional source edits or runs by this supervisor.
