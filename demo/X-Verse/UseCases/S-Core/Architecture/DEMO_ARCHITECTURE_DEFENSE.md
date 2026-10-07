# Cruise Control Signal-Loss Demo — Architecture Gaps & Defense

Scope: `third_party/cruise_diag/patches/demo_enable_dtc_set_and_disable_cruise_control/`
(the demo built on top of the PR #16 `sovd_adapter` contribution).

The PR #16 contribution is unchanged throughout: its patches still reproduce `3ab687b`
exactly on upstream `b975ed4`, and the platform `opensovd-gateway` builds unmodified.

## Fixed gaps

| # | Gap | What fixed it |
|---|---|---|
| 1 | **App-specific code inside the platform gateway** | The cruise diagnostics now live in their own package, `score/examples/cruise_control_diag`, as the `cruise-control-diag` server. It uses only PR16's public API. The platform `opensovd-gateway` and `sovd_adapter` are unchanged; the demo adds only new files. |
| 2 | **Two sources of truth for the threshold** | `entrypoint.sh` declares the values once for the app and the server. Neither has defaults, and the app won't engage cruise if they're missing. |
| 3 | **Coding conventions** | No allocation or exceptions in the 50 ms loop, Eclipse headers, the `score::cruise_control` namespace (old classes too), and the magic-index hack removed. |
| 4 | **Docs-as-code traceability** | 8 requirements, architecture views, FMEA/DFA using S-CORE's official fault IDs, and 4 decision records. The official S-CORE docs build passes: 8/8 requirements and 15/15 tests fully linked. |
| 5 | **Docs build broken** | The root `BUILD` is fixed, so `//:docs` and `//:needs_json` run. |
| 6 | **Doc claimed a FaultProvider** | Corrected; the DTC is described as a data resource. |
| 7 | **Corrupted speed value (MF_01_05)** — partly | A plausibility check means implausible values count as lost, so the cancel and the DTC both react. Corruption that still looks plausible is the documented remainder (see D). |

## Defense statements for what remains

### A. "Why isn't the app → diagnostics link `mw::com`?"

> "S-CORE's IPC standard is `mw::com`, and we tried exactly that. Its Rust API only builds with
> S-CORE's `rules_rust` fork, which adds QNX platforms; the newest fork is 0.68.2. The OpenSOVD
> server needs `rules_rust` 0.70 or newer. We verified both directions: with the fork, `mw::com`
> builds and OpenSOVD doesn't; with 0.70, it's the other way round. No published toolchain builds
> both, so it's an ecosystem limitation, not a design choice. Until it's resolved, we use a
> versioned, validated, non-blocking datagram: schema version, boot ID, monotonic clock and
> ordering checks, and it can never block the control loop. Its fields map one-to-one to a
> `mw::com` event type, so migrating is a transport swap once the toolchains align."

Recorded as decision record `dec_rec__cruise_control__observation_link`.

### B. "Why is the DTC a data resource, not an SOVD fault?"

> "OpenSOVD core 0.1.1 has no faults API: only data and discovery providers, and no `/faults`
> routes. We chose to stay within the standard API instead of adding a non-standard route. Our
> DTC model already carries what a faults entry needs (status, test-failed, confirmed). Once
> OpenSOVD adds a fault provider, which is a natural follow-up contribution, it's an adapter, not
> a redesign."

Recorded as decision record `dec_rec__cruise_control__dtc_as_data`.

### C. "Why does the app detect the loss itself instead of reacting to the DTC?"

Strongest point — lead with it.

> "The function owns its safe reaction; diagnostics own the evidence. If the cancel depended on
> the DTC, a QM, asynchronous diagnostics service would sit in the control path. Our cancel never
> depends on it: diagnostics can crash or restart without affecting control. Both sides use one
> declared threshold, so the cancel and the DTC coincide, measured at 1.06 s against a 1.1 s
> threshold. The setup also covers more: the DTC still sets if the app itself dies."

Backed by DFA entries CO_01_07 and SR_01_07 and decision record
`dec_rec__cruise_control__app_local_reaction`.

### D. "Corrupted values that still look plausible aren't detected."

> "Correct, and our FMEA says so (MF_01_05, marked insufficient). Wrong-size, non-finite,
> out-of-range and physically impossible values are rejected and treated as signal loss. Catching
> plausible-looking corruption needs end-to-end protection (CRC and counter) from the sender,
> which is outside the S-CORE application. That's what a safety-relevant variant would add."

### E. "There are two copies of the debounce logic."

> "One copy belongs to the HVAC example in the upstream PR, which we deliberately don't touch; the
> other is in our app package. Moving a shared debounce into `diag_api` is the next upstream
> contribution."

Recorded in decision record `dec_rec__cruise_control__app_diag_server`.

### F. "Everything is QM."

> "Yes, deliberately, for a demo on a simulator. What we can show is that the architecture is
> ready for a safety argument: S-CORE-conform requirements, FMEA and DFA, decision records, full
> requirement → code → test traceability, and a control path that doesn't depend on QM
> diagnostics."

## Where to find the evidence

- Decision records, requirements, architecture, FMEA/DFA:
  `cc_s-core/score/cruise_control/docs/{decisions,requirements,architecture,safety_analysis}.rst`
- Patch series and apply order:
  `third_party/cruise_diag/patches/demo_enable_dtc_set_and_disable_cruise_control/README.md`
- Headless E2E of the final architecture (cancel 1.06 s, DTC `failed` → `passed`):
  `OpenSOVD/evidence/f008-headless-app-owned-diag-20261006T232700/`
- E2E DTC set with CARLA (earlier build): `OpenSOVD/evidence/f005-e2e-sovd-ipress-20261006T200230/`
