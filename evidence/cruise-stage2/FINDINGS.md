<!-- SPDX-License-Identifier: Apache-2.0 -->

# Cruise control over the full S-CORE path

Date: 2026-09-25. Host: Ubuntu 26.04, Bazel 9.2 (bazelisk), 16 cores.
Upstream: `eclipse-score/inc_someip_gateway` @ `f8a196c3`, `eclipse-score/communication` @ `4f56985`.

| Link | Question | Result | Log |
|---|---|---|---|
| ⑤ | Do gatewayd and someipd build and connect? | **Yes.** Both example daemons build; gatewayd logs `IPC connection to someipd established`, creates its local and remote service instances; someipd (vsomeip 3.6.1) offers them over SOME/IP-SD | `gatewayd.log`, `someipd.log` |
| ④ | Does the mw::com **Rust** API build and run? | **Yes, in the communication repo.** `bigdata-producer` offers, `bigdata-consumer` retries until the service appears, subscribes and receives 5/5 samples over shared memory | `mwcom-rust-*.log` |
| ④ | Can it be built from another workspace? | **Not as is.** From the gateway workspace `score_com` fails: `score_baselibs` needs a newer Rust (`NonNull::from_ref` as const fn) than the default `rules_rust` toolchain. S-CORE's Ferrocene toolchain (`score_toolchains_rust`) is a dev dependency, so it is only active in S-CORE's own repos. inc_diagnostics registers the same toolchain family | `../../upstream/score-com-rust.log` (not tracked) |

## Host workaround needed for every S-CORE Bazel build here

The hermetic LLVM `ld.lld` needs `libxml2.so.2`; Ubuntu 26.04 ships only `libxml2.so.16`.
A private symlink, passed to Bazel actions only, is enough (`ld.lld` prints a harmless
"no version information" warning):

```bash
mkdir -p ~/.local/lib/bazel-xml2compat
ln -sf /usr/lib/x86_64-linux-gnu/libxml2.so.16 ~/.local/lib/bazel-xml2compat/libxml2.so.2
X=~/.local/lib/bazel-xml2compat
bazel build --action_env=LD_LIBRARY_PATH=$X --host_action_env=LD_LIBRARY_PATH=$X <targets>
```

## Result: the full architecture runs (2026-09-25)

`DEMO=score demo/start.sh`, then `demo/run-demo.sh`: **13/13 PASS**, three runs in a row
(`evidence/runs/20260925T155109Z`, `…155133Z`, `…155143Z`), after a cold start.

```
SOVD client ─①─ opensovd_server ─②─ sovd_adapter ─③─ cruise diag ─TCP :7700─ cruise_bridge
   (host, Cargo build)                                                   (container sdv-vehicle, 172.28.0.2)
cruise_bridge ─④ mw::com─ gatewayd ─⑤ IPC─ someipd ─⑥ SOME/IP over the Docker network─ cruise_ecu
                                                                       (container sdv-cruise-ecu, 172.28.0.3)
```

| Hop | What runs | Proof |
|---|---|---|
| ⑥ | `cruise_ecu` (vsomeip, stand-in for the other team) offers 0x4300 `cruise_status` every 100 ms and subscribes 0x4301 `inject_fault` | `full-cruise_ecu.log`, `full-cruise-ecu-stats.json` |
| ⑤ | gatewayd ↔ someipd with our two services | `full-gatewayd.log`, `full-someipd.log` |
| ④ | `cruise_bridge` (Rust, `score_com`) subscribes `/sdv/cruise_status`, offers `/sdv/diag_injection` | `full-cruise_bridge.log`, `full-bridge-stats.json` |
| TCP | the Cargo-built SOVD gateway reads the bridge's status lines and sends `inject 1/0` | `demo/gateway/crates/cruise-gateway/src/bridge_link.rs` |

Measured on the bench: an injection over SOVD reaches the ECU, which freezes its speed and
turns `unavailable` 5.1 s later; after release it goes to `standby`, then `active` 3 s later.

## What it took (each is worth knowing for the event)

1. **Same mw::com version on both sides of ④.** LoLa's shared-memory layout must match, so the
   bridge is built inside the gateway's workspace (pinned `score_communication` d609be9), with
   S-CORE's Ferrocene Rust toolchain added to that module (`demo/score/MODULE.overlay.bazel`).
2. **Payload layout.** gatewayd moves SOME/IP payloads unchanged in a `PreSerializedData<N>`:
   `size_t size`, then the bytes aligned to 16. The Rust mirror needs explicit padding;
   `cruise_api.rs` has a test and `cruise_api.cpp` static_asserts for it.
3. **Rust instance specifiers must start with `/`** (`/sdv/cruise_status`); C++ accepts both.
4. **SOME/IP interface major version.** Our first stand-in subscribed with major 0; someipd
   rejected it (`Requested major version:[0] … does not match … [1]`). The other team's app
   must use **major 1**.
5. **SOME/IP-SD needs an explicit multicast route.** vsomeip starts discovery only once a route
   to 224.244.224.245 exists; Docker's default route is not enough (`node/*.sh` adds it).
6. **Upstream gatewayd bug:** when a watched mw::com service disappears, gatewayd's find-service
   handler gets an empty handle list and asserts (`std::vector::front()` on empty,
   `LocalServiceInstance::CreateAsyncLocalServices`). Triggered by a stale LoLa discovery file
   after `docker compose restart`. Workaround: fresh LoLa state on every start. Worth an issue
   on `eclipse-score/inc_someip_gateway`.
7. **glibc.** The vsomeip libraries built here need glibc 2.42, so the runtime image is
   Ubuntu 26.04 (same as the host).

## What this means for the design

- ④ ⑤ are real and work on this laptop; the handshakes on page 1 of
  `docs/architecture/sdv-hackathon-final.drawio` match what the logs show.
- Our gateway builds with Cargo (its Bazel build is blocked, `evidence/pr6-gateway/FINDINGS.md`),
  and `score_com` needs S-CORE's Bazel + Ferrocene. So the mw::com side of cruise diag goes into a
  **small Bazel-built bridge process**, not into the gateway binary. It talks mw::com to gatewayd
  and hands the values to the gateway's `CruiseLink` over a local socket: one extra local hop.
- Done: the cruise services in gatewayd's config, the bridge, and a SOME/IP stand-in for the
  cruise control app (⑥). Still open: the other team's real app on ⑥.
