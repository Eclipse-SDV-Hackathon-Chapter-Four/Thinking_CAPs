# sdv_cruise

Cruise control ECU simulator and bridge.

## Files
- `cruise_ecu.cpp` - C++ ECU simulator (SOME/IP publisher)
- `cruise_bridge.rs` - Rust bridge (mw::com → TCP)
- `cruise_api.rs` - Rust API types
- `cruise_api.cpp` - C++ API bindings
- `cruise_types.h` - Shared type definitions
- `BUILD.bazel` - Bazel build rules
- `config/` - SOME/IP configuration files

## Build
```bash
bazel build //sdv_cruise:all
```
