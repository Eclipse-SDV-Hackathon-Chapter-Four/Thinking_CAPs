# Offline contribution review packet

## Scope and provenance

Authorized work: create a Thinking_CAPs branch, collect chatbot contribution evidence,
and identify a suitable S-CORE issue. Writes are confined to this packet and contribution
inventory files. The chatbot source checkout remains clean and unchanged. Fresh checks
use a disposable source archive copy.

Current chatbot commit and archive hashes are in
[source provenance](evidence/source/provenance.json) and
[source manifest](evidence/source/source-manifest.json).
The full tracked source, tests, configs, dependency locks and native CI definition are
included in the archive. Project documents are also exported as readable files under
[evidence/project](evidence/project/).

The S-CORE guidance baseline is recorded in
[score-baseline.json](evidence/upstream/score-baseline.json).
Its contribution guide, improvement PR template, CODEOWNERS, license and notice are
retained. The referenced Markdown improvement issue template returned HTTP 404;
the unavailable record is preserved. Repository format/routing must be checked again
when an actual upstream patch is prepared.

## Architecture and intended contribution

Operator source synchronization resolves documentation commits and records file hashes.
Safe parsers normalize RST/Markdown/needs data without running upstream scripts.
Immutable snapshots hold SQLite FTS5 data and NumPy embedding vectors. Search and exact-ID
lookup return source-bound evidence. Local Ollama generates structured claims; server
validation assembles citations from stored provenance. CLI, FastAPI and React expose
those operations. Explicit comparison retains both snapshot identities.

The proposal reuses pinned ingestion, provenance, exact IDs and snapshot diff for the
retrieval/context part of #2850. A stdlib-only, read-only adapter must consume an authorized
prepared export and emit deterministic context for one task. Chat remains optional
assistance; native coverage/gate/schema tools own assurance verdicts.

The existing chatbot application is not a conforming single-file native harness candidate:
it uses external Python dependencies, can call a loopback model, searches a broader corpus,
and lacks the required consistency rules, trace store and outer loop. Detailed trace:
[acceptance-mapping.md](acceptance-mapping.md).

## Evidence interpretation

Fresh checks bind to current commit 72c1fb2. Older model evaluations and release records
bind to their recorded snapshot/model/review identities and are carried without rerunning.
Original release manifest hashes were verified before copying. Historical reports do not
provide an independently complete source-commit binding for every run and must not be
presented as fresh verification of HEAD.

The retained release report JSON has 43 gates passing and one optional public-hosting
gate not run. The release notes say 44 passing; the packet uses the JSON count and
preserves that original documentation discrepancy.
Its human support/coverage figures are based on blanket owner acceptance, not independent
per-claim measurement. This is local owner evidence, not S-CORE maintainer approval.
The original failed release reports and injection/transient test findings remain in the
project's verification records.

## Licenses and redistribution

The chatbot declares Apache-2.0. LICENSE, NOTICE where present, third-party notices,
locked dependencies, SBOM, source registry and the agent corpus license review are retained.
The fresh license check is the chatbot's allowlist check; Eclipse Dash clearance was not run.

Model identities and license records are retained without model weights. Corpus manifests
are metadata only; corpus bundles and source files are excluded. Three upstream
process-description files have CC-BY-SA-4.0 notices according to the original agent review;
any later corpus redistribution needs separate attribution/license handling.
Embedded evaluation excerpts retain their evidence URLs and original provenance.

The S-CORE contribution guide requires ECA and DCO. Confirm identity/sign-off and the
appropriate native request type when preparing submission. No current ECA lookup or legal
approval is claimed in this packet.

## Checks and offline decisions

See [verification.md](verification.md) for exact results, raw logs, tools, skips and limits.
The environment uses existing locked project dependencies in an isolated source copy.
Current GitHub CI success was not established: the connector's PR-triggered, first-page
workflow lookup for the merge commit returned no runs.

Pending decisions: maintainer agreement on scope and destination, native requirement/tool
management applicability, adapter design, native deterministic benchmarks/CI, and upstream
review. There is no safety qualification or formal S-CORE engineering acceptance.

Concrete next action: present the scoped proposal under #2850, then prepare the agreed
native adapter and tests in an isolated target checkout. The current packet is preparation
and does not close #2850.
