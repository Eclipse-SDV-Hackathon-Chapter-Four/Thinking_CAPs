# Dashboard implementation decisions

Prepared 4 October 2026; second-contributor reproduction is deferred by the user,
not accepted. AAOS/FOTA remains deferred. ThreadX/AutoSD remain separate proposals.

- Decision: a local Python 3.10+ standard-library HTTP coordinator with static
  HTML/CSS/JavaScript. Rationale: existing native campaigns already use Python;
  no package service/build or new vehicle dependency is necessary. Alternatives:
  React/FastAPI would introduce additional tools without improving this slice.
- Decision: bind only 127.0.0.1, validate Host and Origin, require a same-origin
  session token for mutations, prohibit CORS and arbitrary commands. Rationale:
  this is a local hackathon tool. Private-network access uses SSH forwarding;
  public/production hosting is a separate deployment. Python's HTTP server has
  basic security checks only: [official documentation](https://docs.python.org/3/library/http.server.html).
- Decision: background workers acquire actual OpenSOVD resource links and bounded
  openDuT observations. HTTP handlers return caches, never block vehicle control.
  Preserve service availability, reported freshness and fault query independently;
  controller output is currently unavailable in the upstream observation schema.
- Decision: persist one coordinator run ID, pass it to the campaign CLI, use Linux
  flock for coordinator/bench exclusivity and runner admission, and serialize starts.
  Cancellation signals only the owned runner; native finally performs restoration.
  Reap before final cleanup assessment. Cleanup unknown/failed inhibits subsequent
  starts. Restart cannot infer cleanup from missing processes or kill reused PIDs.
  [Subprocess documentation](https://docs.python.org/3/library/subprocess.html) and
  [flock documentation](https://docs.python.org/3/library/fcntl.html) were checked.
- Decision: offer core (fixture vehicle inputs/native integration), cleanup-failure
  and actual CARLA campaigns; record blocked runs on missing prerequisites.
  Test execution is project orchestration on an openDuT-managed bench, not a
  claimed upstream executor. CLI-created native results remain the acceptance authority.
- Decision: register historical artifacts with hashes and verify byte identity
  independently of original verdict. Allow only explicit reports, observations and
  replay; exclude credentials, arbitrary paths and packet payloads. Downloads preserve
  bytes. Historical mode cannot supply current health.

Read-only research agent inspected the actual pinned source and evidence. No
unresolved technical clarification remains. Source preservation and failure tests
are required before marking the feature implemented.
