# SOVD Layer

SOVD (Service-Oriented Vehicle Diagnostics) Gateway implementation.

## Build
```bash
cargo build --release
```

## Crates
- `cruise-gateway/` - Main SOVD REST API server (port 7690)
- `cruise_diag/` - Fault logic, DTC debounce
- `cruise_sim/` - ECU simulator (fallback mode)

## API Endpoints
```
GET  /sovd/v1/components
GET  /sovd/v1/components/cruise/data/speed
POST /sovd/v1/faults/inject
POST /sovd/v1/faults/clear
```
