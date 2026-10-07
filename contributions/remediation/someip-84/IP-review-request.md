# Prepared IP review request — SOME/IP #84

Prepared locally; this request has not been sent and has no approval number.

Project: Eclipse S-CORE (`automotive.score`). Destination:
`eclipse-score/inc_someip_gateway`, baseline
`f8a196c3b16d5172d898394ab99b0ed81346d63d`.

The contribution fixes duplicate SOCom server registration when only the minor
version differs. It compares `(instance, service id, major)` consistently with the
service database. It includes regression tests, a narrowly visible test-only BUILD
target, and AI disclosure/licence notices. The wider identifier/discovery design
under issue #84 remains open.

Responsible contributor: Jefferson Nascimento, `jnsagai@gmail.com`, Eclipse
`jnascimento6p0`. The current ECA lookup passes; an eventual native PR still needs
its actual author/committer eligibility checks and the author's DCO certification.

Historical implementation was drafted with OpenAI Codex; native Fabro verification
and repair evidence is retained. Exact historical model revision was not recorded.
This compliance preparation also uses OpenAI Codex. The largely generated new
regression file now identifies AI assistance and separates CC0-1.0 AI portions from
Apache-2.0 copyrightable human modifications/curation. Copied original notices are
preserved. GoogleTest remains an existing dependency and is not vendored by this
patch; its original licence is retained in the disposable verification checkout.

The amended seven-file diff has **3,325 additions and 6 removals**, including the
CC0 licence text and extensive test cases. These are diff statistics, not a final
calculation of net new intellectual property. The original six-file patch had
3,198 additions and 6 removals. No review exemption is inferred from generated or
repeated test code, and the contribution has not been split to avoid review.

Please have a project committer determine the applicable net new IP and initiate
the Eclipse IP Team review before official inclusion as required. Include the
exact prepared patch SHA-256 and native revision from `preparation.json`/the review
packet in that request. Confirm the file-level licence/disclosure treatment and
record the resulting request and decision against the reviewed revision.

Policy source: [Eclipse Project Handbook](https://www.eclipse.org/projects/handbook/).

Assisted-by: OpenAI Codex (model revision unavailable)
