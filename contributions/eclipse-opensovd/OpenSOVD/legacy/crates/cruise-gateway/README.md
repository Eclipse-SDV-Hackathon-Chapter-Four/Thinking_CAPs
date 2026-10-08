# cruise-gateway

Standalone Axum prototype exposing the cc-app faults collection.

Run from `eclipse_sdv_hackathon_2026/sovd`:

```bash
cargo run -p cruise-gateway
```

The default bind is `127.0.0.1:7690`. The internal HTTP event-ingestion route is a test bridge only. The architecture's I1/I2 JSON-lines Unix socket, command forwarding, and upstream OpenSOVD server integration are not implemented yet.
