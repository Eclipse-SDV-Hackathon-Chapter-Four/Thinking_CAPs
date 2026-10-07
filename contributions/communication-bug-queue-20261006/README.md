# Communication bug queue, 6 October 2026

User-authorized sequential draft/fix queue: **DeepSeek Flash only, $10 total**.
This is a separate budget from the completed #1167 contribution. No publication,
push, PR, issue closure or engineering acceptance is authorized by this queue.

Selected current open typed bugs, in execution order:

1. [#1236](https://github.com/eclipse-score/communication/issues/1236): enforcing buildifier lint in CI.
2. [#1031](https://github.com/eclipse-score/communication/issues/1031): external AoU visibility and forwarding traceability.
3. [#751](https://github.com/eclipse-score/communication/issues/751): production-source completeness of CodeQL evidence.
4. [#1104](https://github.com/eclipse-score/communication/issues/1104): lost CodeQL SARIF file locations.

The other nine bugs are excluded with source/ownership, platform or reproduction
reasons in `selection.json`. This is suitability for this bounded queue, not a
claim that those bugs cannot be handled by the fabric in a separately scoped run.

The stable fabric commit is `b2aa9a7a49a054621f38e59f3aef6d6e5daf3cce`.
The communication baseline is `381d43dec900ab6a9076f3f30e7bfbdee019e26e`.
Each item has an independent branch and disposable source copy on the admitted
ext4 image, currently `/dev/loop1`, UUID `11c42dee-73a3-4c2b-ab42-a0440011d9e0`.
The optimization checkout and existing queues are not modified. An immutable
native source archive, license notices, baseline hashes and frozen workflow
inputs accompany the contribution. Tooling AoU context is pinned to tooling
2.3.1, commit `37043e82df0fdc374caf499cb340abc0d4732302`.

Fabro owns the whole queue as one sequential workflow: admit, draft, apply,
native verification, export, then the next item. There is no host scheduler,
automatic model supervisor, human approval node, automatic acceptance, fallback,
output repair or workflow retry. Admission/export control failures stop the
queue. A failed draft, apply or native verification exports its original failure
before the next independent item. An empty or malformed draft remains unresolved.

Each of four prompt stages permanently reserves $2.359296; the conservative
queue reservation is $9.437184. The reservation covers the full published model
context/output ceiling at peak provider prices and all three pinned transport
attempts. The graph additionally requests `max_tokens=32000`; the reservation
does not assume that attribute enforces a provider output ceiling. Actual
provider cost remains unknown unless reported, and is never replaced by an
estimate or a zero. The explicit native RunIntent title suppresses Fabro's
otherwise implicit paid title generation. No model smoke call is made.

Native measurements run fresh against each bound candidate, with full stdout,
stderr, exact commands, return codes, source hashes and time limits retained.
Baseline and candidate focused checks are separate. Full native build/tests and
the contribution guideline's copyright/format checks are attempted. Download,
platform, analyzer and test failures remain visible. No previous #1167 pass is
carried into this changed baseline. QNX validation is unavailable on this host.
The pinned local Ubuntu 24.04 build image and Bazel 8.7.0 identities are recorded;
availability of that local Docker image is a reproduction prerequisite.

For #751, findings in SARIF do not prove extraction completeness; the compiler
database coverage audit remains explicit pending native/offline review. For
#1031, real external Config Management consumption and non-duplicated FMEA/LOBSTER
traceability remain pending cross-repository review. Unit fixtures cannot resolve
these obligations. Invalid or absent real SARIF locations prevent #1104 from
being described as verified. Every result remains a draft for offline review.

All contribution records live in this directory. Per-item patches, changed
source, model response, native state, analyzer products and logs are exported to
`items/<number>/`. `state.json` is a rebuildable dashboard projection of the run;
native Fabro events remain authoritative for execution. Inspect `native-run-id`,
`queue-record.json`, `budget-ledger.json`, and each item's result before resuming.
Never rerun `prepare.py`, reset reservations or create a replacement paid run to
bypass the total cap. The script refuses preparation after native registration.
Storage identity changes stop execution instead of moving active work.

The Eclipse ECA declaration for `jnascimento6p0` was verified during #1167;
eligibility of a future commit identity and all upstream submission reviews are
still pending. `CONTRIBUTING.md` is retained at the selected source pin.

Dashboard: use the existing `fabro_dashboard` on port 8787. The dashboard's
queue glob points at this contribution directory; no fabric source changes are
required for display. See `handoff.md` for the concrete registered run and status.
