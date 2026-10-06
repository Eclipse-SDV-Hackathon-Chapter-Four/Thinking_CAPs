# Local dashboard API

Loopback HTTP; exact bound Host, same-origin mutation Origin and X-SDV-Token.
GET / serves static UI; GET /api/state returns targets, acquired diagnosis/bench,
capabilities, fixed campaigns, persisted active run and historical summaries.
Read caches are available with services stopped; missing observations stay unknown.

POST /api/runs JSON {scenario: core|cleanup-failure|carla}: creates UUID once under
mutex; 202 accepted, 409 active/unresolved cleanup, 400 unsupported input.
Runner receives --run-id; missing native prerequisites produce a persisted blocked
runner result. Browsers must never retry POST automatically on network errors.
POST /api/runs/<id>/cancel requests SIGTERM of the owned Popen child once;
202 pending, 200 already terminal, 404 unknown. Cleanup is determined after reap
from mandatory native restore/container/capture/private-owner checks, never merely
signal delivery. Browser disconnect does not cancel; graceful service shutdown does.

GET /api/runs/<id>: original results/manifest, bounded timeline/observation summaries,
artifact inventory and independent integrity state. Authoritative live lifecycle is
separate from runner verdict. Missing evidence does not create a pass.
GET /api/runs/<id>/artifacts/<encoded-explicit-name>: byte-exact download only if
allowlisted, regular file, scoped and expected hash matches; 409 integrity failure,
404 missing/unregistered. Replay route has sandboxed CSP and historical label.

Unsafe Host/Origin/token =>403. Bounded JSON body, no arbitrary commands, no
credential/capture downloads, no CORS, no external browser dependencies.
