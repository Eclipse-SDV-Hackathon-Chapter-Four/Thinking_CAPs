<!-- SPDX-License-Identifier: Apache-2.0 -->

# openDuT: running the demo as a test executor

openDuT executes tests as **container executors**: EDGAR starts a container on a
peer, the container writes its results to `/results` and creates
`/results/.results_ready`, and EDGAR uploads `/results` as a ZIP to a WebDAV URL
(openDuT user manual, *Test Execution*).

| File | What it is |
|---|---|
| `Dockerfile` | Image `sdv-demo-runner`: `dashboard/run-demo.sh` unchanged, plus the results contract |
| `executor-entrypoint.sh` | Runs one demo run into `/results/run`, writes `exit-code`, touches `.results_ready` |
| `peer.yaml` | CLEO `PeerDescriptor` (devices `hvac-ecu`, `flxc1000`, the executor) + `ClusterDescriptor` |

## Status (2026-09-22)

| Step | Status |
|---|---|
| Executor image builds and runs the demo | **Verified** — 12/12 PASS inside the container, `.results_ready` and `exit-code` written |
| `peer.yaml` matches the openDuT schema | Written field by field against `opendut-model/src/specs/peer.rs` (v0.10.2, kebab-case, all `Vec` fields present). **Not yet parsed by CLEO** — that needs a running CARL |
| CARL + EDGAR (THEO testenv) running on the laptop | **Not done** — needs the `/etc/hosts` entries below (sudo) |
| Cluster deployed, results uploaded to WebDAV | **Not done** — follows from the step above |

## Build the executor image

```bash
docker build -t sdv-demo-runner:local -f dashboard/opendut/Dockerfile demo
# check it without openDuT (services from dashboard/start.sh must be up):
docker run --rm --network host -v "$PWD/evidence/opendut:/results" sdv-demo-runner:local
```

## Bring up openDuT (THEO test mode, Docker on the host)

From the openDuT repository (`upstream/opendut`, release v0.10.2), following
`doc/src/development/testenv/setup/theo-setup-docker.md`:

1. **Needs sudo, once:** add to `/etc/hosts`
   ```
   127.0.0.1 opendut.local auth.opendut.local netbird-api.opendut.local netbird-relay.opendut.local
   127.0.0.1 signal.opendut.local nginx-webdav.opendut.local opentelemetry.opendut.local monitoring.opendut.local
   ```
2. Put the v0.10.2 release binaries (CARL, EDGAR, CLEO) into
   `target/ci/distribution/x86_64-unknown-linux-gnu/` — or build them with `cargo ci distribution`.
3. `cargo theo testenv start`, then `cargo theo testenv cluster start` (starts EDGAR peers).
4. Replace `DEMO_HOST` in `peer.yaml` with an address the EDGAR peers can reach, then
   `opendut-cleo apply dashboard/opendut/peer.yaml` and deploy `sdv-demo-cluster`.
5. Results appear as a ZIP under `http://nginx-webdav/sdv-demo/`; `run/verdict.md` inside
   is the same verdict `dashboard/run-demo.sh` prints.

## Known gaps

- The executor image must be present on the peer's Docker engine (it is local, not pushed
  to a registry). In the THEO testenv the EDGAR peers run in containers; whether their
  engine sees the host's images has not been checked.
- If the full testenv cannot be brought up at the event, say so: the executor image and
  its results contract are verified; the CARL/EDGAR deployment is not. Do not claim the
  +0.10 openDuT bonus for more than that.
