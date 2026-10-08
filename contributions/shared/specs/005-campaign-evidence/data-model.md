# Campaign data
LocalInputs: explicit paths to native feature binary, Score source/baseline/bridge, Bazel volume,
flatc executable/schema, expected immutable images, openDuT state; optional CARLA assets.
Scenario: stable id, preconditions, expectations, required assertion ids/prefixes.
Run: schema_version, run_id, seed, mode, prepared classification, clocks, revisions/dirty hashes,
input hashes, target/build/network identity, started/finished, child exit, scenario verdicts.
Verdict enum passed/failed/blocked/skipped. Exit precedence failed1 > blocked2 > passed0; skipped
never counted as passed. JUnit maps failed→failure, blocked/skipped→skipped.
