<!-- SPDX-License-Identifier: Apache-2.0 -->

# Path B bring-up — findings (2026-09-22)

Upstream `classic-diagnostic-adapter` at `c1a5d8b2`, unmodified, via
`testcontainer/docker-compose.yml`. Host: Ubuntu 26.04.1, Docker 29.1.3.

## Results

| Check | Result | Evidence |
|---|---|---|
| Images build (`cda`, `ecu-sim`) | PASS | `docker-build.log` |
| Upstream `sovd::faults` integration tests | **PASS 7/7** in 124 s | `upstream-faults-tests.log` |
| G1 — `GET :20002/vehicle/v15/components` | PASS — 6 ECUs: tmcc3000, hovr4000, fsnr2000, flxcng1000, jgwt5000, flxc1000 | `path-b-manual-run.md` |
| P2 — inject `0x01E240`/`0x2F` on `:8181`, read `…/flxc1000/faults` on `:20002` | **PASS** — returned `01E240`, "DTC Code 1", mask `2F`; empty again after clear | `path-b-manual-run.md` |
| P2 — same with the planned demo code `0x7001` | **FAIL** — `400 Bad payload: No DTC with code 7001 found in DTC references` | `path-b-manual-run.md` |

Host note: the integration tests need OpenSSL headers. Without sudo, `libssl-dev` was
unpacked with `apt-get download` + `dpkg -x` and passed via `OPENSSL_INCLUDE_DIR` /
`OPENSSL_LIB_DIR`. `sudo apt install libssl-dev` is the permanent fix.

## Finding 1 — the demo DTC must come from the MDD

The CDA decodes UDS `0x19` replies against the DTC table in the ECU's diagnostic
database. The test MDDs define `0x01E240`–`0x01E244` and `0x039447` for `flxc1000`.
`0x7001` is not among them, so the demo must use a defined code. **Proposed demo DTC:
`0x01E240` ("DTC Code 1") with status `0x2F`** — verified above.

## Finding 2 — one unknown DTC fails the whole faults collection (candidate CDA issue)

`cda-core/src/diag_kernel/payload_decode.rs`, `map_dtc_dop_from_uds` (line ~1851):

```rust
let record = dtc_dop.dtcs()
    .and_then(|dtcs| dtcs.iter().find(|dtc| dtc.trouble_code() == code))
    .ok_or(DiagServiceError::BadPayload(format!(
        "No DTC with code {code:X} found in DTC references",
    )))?;
```

If the ECU's fault memory holds a single code the database does not describe, the
`?` aborts decoding of the entire response. `GET …/faults` then returns
`400 bad-request` and **all known, active faults are hidden too**.

Reproduce (stack from `testcontainer/`, token from `/vehicle/v15/authorize`):

```bash
curl -X DELETE localhost:8181/flxc1000/dtc/Standard
curl -X PUT localhost:8181/flxc1000/dtc/Standard -H 'Content-Type: application/json' \
  -d '{"id":"01E240","statusMask":"2F","emissionsRelated":false}'
curl -X PUT localhost:8181/flxc1000/dtc/Standard -H 'Content-Type: application/json' \
  -d '{"id":"007001","statusMask":"2F","emissionsRelated":false}'
curl localhost:20002/vehicle/v15/components/flxc1000/faults -H "Authorization: Bearer $TOKEN"
# -> 400 "No DTC with code 7001 found in DTC references"; 01E240 is not reported either
```

Why it matters: real ECUs report codes missing from the ODX (supplier codes, newer
software than the diagnostic description). A tester should still see the known faults,
and the unknown one as a bare code. Searched open and closed CDA issues on 2026-09-22 —
not filed. **Not searched: discussions and PR comments.**

Suggested behaviour, for the maintainers to decide: return the unknown code with its
status and no name/severity (or skip it and log a warning), instead of failing the
collection. Unverified whether this is intended by the MDD design — ask first.

This is a candidate **second Day-2 contribution** (issue now, fix at the event), in
the same repository as CDA #543.
