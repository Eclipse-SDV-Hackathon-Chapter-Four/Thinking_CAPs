# Discovery prerequisites after resume

This is operator source analysis, not an implementation or an accepted architecture decision.

Selected baseline: `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Fresh issue bodies/comments/timelines are in `context/issue-{250,1261}-*-current.json`.
Current upstream head/compare are recorded separately; no rebase or source change occurred.

## #250

The current issue body asks to enable `FindServiceSpecifier::Any` once LoLa supports it. Its 2026-03-30 comments establish two distinct expectations: LoLa already crawls all instances of a specified service through an `InstanceIdentifier` without an instance ID; another commenter asks for all available system services. Existing Rust `find_service<I>` returns a descriptor tied to interface I. A typed same-interface wildcard and a heterogeneous system-wide stream therefore need distinct API semantics; dropping the panic or routing Any to a configured Specific cannot establish the broader behavior.

Native evidence: `flag_file_crawler.cpp` implements per-service wildcard instance crawling; `i_service_discovery.h` offers InstanceIdentifier overloads; `registry_bridge_macro.cpp` FFI start/find paths take only InstanceSpecifier; Rust consumer descriptors retain a concrete InstanceSpecifier and expose no native handle identity. The existing find_any_semantics native client/provider test exercises a configured per-service wildcard, not interface-independent discovery.

A concrete implementation must resolve a wildcard identifier for interface I, expose that discovery path and concrete handle identity across FFI, preserve callback/StopFindService ownership and support proxy construction for each returned instance. A backend plan must explicitly disposition whether the issue's system-wide comment is implemented via #1261 or changes this contract. Two original source correction slots remain; none consumed during resume.

## #1261

Current issue explicitly requires a continuously updating system-wide stream of descriptors from different interfaces, retaining existing scoped APIs. Linked #9 was closed as a transfer/replacement on 2026-10-03; that is not implementation evidence. No new #1261 comments provide a backend or accepted descriptor contract.

The original proposal adds ServiceDescriptor and a provided find_all_services method that returns NotSupported in LoLa. That is partial API scaffolding. Its new error-enum variant can break exhaustive downstream matches; compatibility must not be called non-breaking without a supported compatibility analysis. Rust-only forwarding cannot satisfy cross-interface discovery.

The baseline Configuration exposes service types and instances to C++, but IRuntime.resolve accepts a single InstanceSpecifier. Enumerating configured entries is potentially a backend implementation path, but cannot be called discovery of every system service without an explicit universe/authorization contract. Positive integration coverage needs at least two distinct interfaces, pre-existing and newly offered services, identity, restart/re-offer semantics, error/termination behavior and stream-drop callback quiescence. Native runtime/FFI support and this contract remain unimplemented. Two original source correction slots remain; none consumed during resume.

## Carry policy

Historical failed tests, patches and missing supervisor reports remain in the sealed original packet. No original report is retroactively accepted or overwritten. This triage is freshly retrieved context plus selected source analysis; it supplies no new passing test evidence for #250/#1261 and no engineering acceptance. The Codex correction exception remains scoped to #560; its passing packet stays unchanged.
