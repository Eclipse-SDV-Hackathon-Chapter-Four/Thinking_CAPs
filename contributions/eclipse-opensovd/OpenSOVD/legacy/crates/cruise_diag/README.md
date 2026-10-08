# cruise_diag

FaultProvider prototype for producer-confirmed cc-app DTC events.

## Features

- Full 8-bit UDS status preservation and six-hex-digit 24-bit DTC identifiers.
- Source timestamps, severity, and freeze-frame/environment data.
- Status-mask filtering and configurable max-age checks.
- No local fault detection or debounce; those belong to the cc-app DTC backend.

See `docs/hackathon/FAULT_PROVIDER_DESIGN.md` for the I1/I2 handover gap and vehicle-integration requirements.
