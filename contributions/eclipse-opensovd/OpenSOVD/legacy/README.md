# SOVD Layer

SOVD (Service-Oriented Vehicle Diagnostics) Gateway implementation for the cruise-control demo.

## Build and Test

```bash
cargo test
cargo build --release
cargo run -p cruise-gateway
```

The gateway listens on `127.0.0.1:7690` by default. Set `SOVD_BIND_ADDR` to override the address.

## Crates

- `crates/cruise-gateway/` - Axum API adapter and local development server.
- `crates/cruise_diag/` - Fault models, provider trait, status filtering, source timestamps, and max-age checks. Detection/debounce belong to `cc-app`.
- `crates/cruise_sim/` - Planned ECU simulator (not part of this fault-provider workspace yet).

## Fault API

```text
POST   /internal/fault-observations
GET    /sovd/v1/apps/cc-app/faults
GET    /sovd/v1/apps/cc-app/faults/{code}
DELETE /sovd/v1/apps/cc-app/faults/{code}
DELETE /sovd/v1/apps/cc-app/faults
```

The internal POST endpoint is a development bridge contract and must be authenticated or disabled in deployment. The `DELETE` semantics are provisional pending confirmation against ISO 17978-3. See [Fault Provider Design](../docs/hackathon/FAULT_PROVIDER_DESIGN.md) for cc-app integration and upstream OpenSOVD work.
