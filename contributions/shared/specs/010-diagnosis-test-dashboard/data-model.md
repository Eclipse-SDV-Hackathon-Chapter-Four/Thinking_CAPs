# Dashboard entities

- Target: configured id/name/OpenSOVD base URI. Discovery accepts only resource
  links at that configured origin/path. Observation and history each retain value,
  acquired UTC/monotonic timestamp, last failure and available/unavailable status.
  Snapshot age expires current availability; unavailable means last-observed values.
- Bench: configured campaign inputs/state path; observed peers/devices/interfaces,
  profile and timestamp. Stored deployment phase is not management reachability.
- Campaign: fixed scenario name, mode, prerequisite list and selected bench.
- Run: UUID, scenario, mode, created/finished timestamps, lifecycle, owned PID/start
  identity, cancellation request, cleanup result, immutable runner results, progress
  journal, output directory and artifact identities. queued -> running -> finished
  (passed/failed/blocked), or cancelling -> cancelled after reaping. Missing final
  evidence is failed with unknown cleanup. Cleanup unknown/failed locks admission.
- Ledger: persisted run records and active run; atomic replace under coordinator
  mutex. A prior nonterminal run on startup is unresolved; no automatic new execution.
- Artifact: explicit relative report name, bytes and expected SHA256. Missing,
  unrecorded and mismatched identities are distinct; do not change original verdict.
  Symlinks and paths outside registered directories are rejected.
- Historical run: explicit id/label/directory and artifact hashes, optionally sandboxed
  replay. Always historical; fixtures/physical source mode preserved from manifest.

All browser-supplied strings are rendered as text. IDs/scenarios use fixed validation;
paths and commands come only from operator configuration, never HTTP input.
