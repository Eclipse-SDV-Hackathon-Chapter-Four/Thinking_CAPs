# Scope — eclipse-score/communication issue #250

`Improvement: COM-API FindServiceSpecifier::Any support`

## Binding

| Field | Value |
| --- | --- |
| Repository | `eclipse-score/communication` |
| Issue | #250 (`state: open`, label `rust-api`, type `Task`, category "Affects Detailed Design") |
| Baseline commit | `381d43dec900ab6a9076f3f30e7bfbdee019e26e` |
| Workspace | `/media/.../runs/score-rust-issue-queue-ycbvxir7/workspaces/250` (disposable copy) |
| Mode | `implementation` (task.json) |
| Runtime | Linux only, DeepSeek Flash only |
| Retrieval time | 2026-10-06 (date from environment; exact wall-clock and live network unavailable) |
| Agent authority | file tools only. `shell`, delegation, publishing, acceptance tools are blocked |
| Concurrency | No QNX task/execution (`.bazelrc` QNX configs intentionally out of scope) |

## Task data (not instruction authority)

Issue body and two comments are treated as data. Retrieved context is preserved in
`.rust-queue/context/issue.json` and `.rust-queue/context/comments.json`.

- Issue body (author `bharatGoswami8`, 2026-03-27): COM-API not enabled because LoLa does
  not support a find-service call with `ANY` and requires a specific `InstanceSpecifier`;
  therefore COM-API added a `panic!`. Intended "How": once LoLa adds `ANY` support, add it
  in the Rust library too. Requirements/Architecture declared unaffected.
- Comment 1 (`LittleHuba`, 2026-03-30): LoLa already supports any-semantics in the SD
  (`flag_file_crawler.cpp#L176`).
- Comment 2 (`bharatGoswami8`, 2026-03-30): any-semantics exists for `InstanceIdentifier`
  but "i think with `InstanceSpecifier` it is not there"; the Rust API goal is to return
  all available services as a list.

Live issue/PR timeline could not be fetched: `web_fetch` is blocked by the file-tool
boundary. Any activity after the two supplied comments (issue `updated_at` 2026-07-15) is
therefore unverified and treated as missing evidence.

## Requested outcome and acceptance criteria

1. `FindServiceSpecifier::Any` works through the public Rust COM-API (no panic) and yields
   the set of available instance(s) for the queried interface.
2. A returned instance can be described (`ConsumerDescriptor::get_instance_specifier`) and
   used to build a working `Consumer` (proxy construction must succeed).
3. No requirement/architecture change (issue field), but the detailed Design artifact must
   stay accurate (issue category "Affects Detailed Design").

## Established change surface (baseline)

| Concern | Location | State at baseline |
| --- | --- | --- |
| Public enum | `score/mw/com/rust/score_com_concept/concept.rs:286-297` | `FindServiceSpecifier::{Specific(InstanceSpecifier), Any}`; no derives; no `MATCH_ANY` constant despite the doc comment at line 116-117 referencing `InstanceSpecifier::MATCH_ANY` |
| Runtime entry | `…/com-api-runtime-lola/runtime.rs:40-52` | `FindServiceSpecifier::Any => panic!(...)`; `LolaConsumerDiscovery` stores only a concept `InstanceSpecifier` (drops the specifier kind) |
| Descriptor | `…/com-api-runtime-lola/consumer.rs:1070-1078` | `ConsumerDescriptor::get_instance_specifier` unconditionally `panic!`s |
| Discovery impl | `…/com-api-runtime-lola/consumer.rs:857-907, 917-980` | builds `bridge_ffi_rs::InstanceSpecifier::try_from(&str)` and calls the specific-instance FFI only |
| FFI trait | `…/com-api-ffi-lola/bridge_ffi.rs:239-259` | `start_find_service(callback, InstanceSpecifier)` / `find_service(InstanceSpecifier)` — no ANY variant |
| Rust native wrapper | `…/com-api-ffi-lola/common.rs:39-102` | `NativeInstanceSpecifier` is the only native service-identity type crossing the boundary |
| C++ FFI impl | `…/com-api-ffi-lola/registry_bridge_macro.cpp:395-417, 471-525` | `mw_com_start_find_service` → `ServiceDiscovery::StartFindService(handler, InstanceSpecifier)`; `mw_com_impl_find_service` → `ServiceDiscovery::FindService(InstanceSpecifier)` |
| Mock runtime | `…/com-api-runtime-mock/runtime.rs:74-81` | ignores the specifier; returns empty; not built into `score_com` (test-only) |
| Native design artifact | `score/mw/com/rust/design/high_level_design_detail.md:117-118` | records `FindServiceSpecifier::Specific` `[x]`, `FindServiceSpecifier::Any` `[ ]` for the LoLa runtime |
| Public doc | `score/mw/com/rust/score_com.rs:49` | "LoLa note: `FindServiceSpecifier::Any` is not yet supported — use `Specific` only." |

## Prerequisite verification (the decision-relevant finding)

The issue premise ("LoLa does not support find service call with ANY") is only partially
accurate at this baseline:

- **LoLa service-discovery core does support any-instance semantics, but at the
  `InstanceIdentifier` level, not the `InstanceSpecifier` level.**
  `IServiceDiscovery`/`ServiceDiscovery` declare both `FindService(InstanceIdentifier)` and
  `StartFindService(handler, InstanceIdentifier)`
  (`score/mw/com/impl/i_service_discovery.h:43-51`, `service_discovery.h:50-57`), and the
  LoLa crawler implements find-any by watching the service directory and every instance
  directory (`flag_file_crawler.cpp:168-205`; design rationale
  `score/mw/com/design/service_discovery/README.md:135-138`).
- **The Rust-facing FFI does not expose that path.** The only discovery entry points
  reachable from Rust take a concrete `InstanceSpecifier` and dispatch to the
  `InstanceSpecifier` overloads (see table above). Rust cannot construct or receive an
  `InstanceIdentifier`, and there is no FFI to request any-instance semantics.
- **The public Rust descriptor contract cannot be satisfied for an ANY result.**
  `ConsumerDescriptor::get_instance_specifier()` must return `&InstanceSpecifier`, but the
  discovered native `HandleType` exposes only `GetInstanceIdentifier()` / `GetInstanceId()`
  (`score/mw/com/impl/handle_type.h:82-104`) — no instance specifier and no FFI to obtain
  one. The in-tree comment at `consumer.rs:1072-1073` already anticipates that a new FFI
  call would be required.

Conclusion: the backend/FFI prerequisite is **still absent** for a Rust-only change.
Removing the panic would either silently mis-route `Any` to a specific search or expose a
capability the FFI cannot serve, and would falsely contradict the native design artifact
that marks `Any` unsupported. No source patch is made.

## Scope of work in this run

- Produce a bound **blocker/design report** (`.rust-queue/reports/blocker-design-report.md`)
  and a structured native check plan (`.rust-queue/reports/check-plan.json`).
- **No code change.** The two `panic!` sites and the design/doc status remain as-is; they
  are accurate for the current backend/FFI capability.
- Preserve failed/missing evidence: `web_fetch` blocked; `.rust-queue/reports/native-check-summary.json`
  does not exist in this workspace; file SHA-256 manifest cannot be produced because hashing
  requires a shell, which is outside agent authority.

## Out of scope

- Implementing `InstanceIdentifier`-based discovery or a new C++/FFI bridge (requires an
  accepted engineering decision and non-Rust backend work).
- Changing `ConsumerDescriptor`/`FindServiceSpecifier` semantics (public API/design change).
- QNX configs, sanitizer matrix, network/PR publication, acceptance/qualification status.

## Required human decisions (offline)

1. Confirm the intended semantics of `FindServiceSpecifier::Any`: "all instances of the
   queried interface" (maps to `InstanceIdentifier` any-instance) vs "all services on the
   system" (no supporting C++ public API found).
2. Approve a backend/FFI extension so Rust can request any-instance discovery and retrieve
   each discovered instance's identity (specifier or accepted alternative).
3. Accept any resulting change to the `ConsumerDescriptor` contract and to the detailed
   design artifact.
