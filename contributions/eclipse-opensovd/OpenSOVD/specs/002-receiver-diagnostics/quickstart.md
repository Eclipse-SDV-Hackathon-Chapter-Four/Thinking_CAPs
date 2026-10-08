# F002 validation

Build/test native provider with pinned Cargo dependencies:
```bash
cargo test --locked --manifest-path OpenSOVD/integration/diagnostics/Cargo.toml
```
Start the diagnostic server with explicit socket, base URI and provisional budgets via
`OpenSOVD/scripts/run_diagnostics.sh`. For a real controller, apply the isolated patch and rebuild with its
existing Bazel toolchain; enable socket/build identity in deployment environment.
Run `python3 OpenSOVD/tests/diagnostic_http_smoke.py` for explicitly labelled fixture/native HTTP evidence.
The fixture does not prove real CARLA/receiver integration. See completion report for achieved levels.
