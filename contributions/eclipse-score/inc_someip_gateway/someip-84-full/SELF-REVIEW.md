# Agent engineering assessment of full issue #84

This is an agent assessment, not independent human review or project acceptance.

The implementation provides all three identity/request forms in the original
issue. Canonical equality and hashing exclude minor, while full offered-instance
identity includes it. Full connector contracts retain required/offered minor for
compatibility and bridge-request separation. Duplicate registration projects the
contract to ID + major and instance, preserving the earlier regression fix.

Discovery reads enabled local server records under the same mutex used by
registration/removal. It copies actual server minor rather than a historical
index version, ignores client-only/disabled/destroyed records, and performs no
callbacks or heap allocation. The caller owns valid writable optional storage;
the runtime uses the existing SCORE span and writes only within capacity. It
returns total matches, resets remaining slots, and supports null/zero count-only
queries. Its results do not guarantee later availability. String IDs must be
registered during setup to avoid registry allocation in query construction.

Optional minor means minimum compatible minor, preserving existing native
client/server semantics. This interpretation and the synchronous local snapshot
scope are explicit proposals for committer assessment. Major remains exact;
wire sentinel translation and narrowing are unchanged. The native architecture
assigns cross-process/network communication to bridges; this API does not claim
to implement network discovery or subscriptions.

All in-repository consumers of the renamed descriptor and IPC conversion are
migrated. IPC serialized members are preserved. External users must migrate and
rebuild, and other Runtime implementations must implement the added virtual
method. This source API migration is a material compatibility consideration.

Tests exercise identity/hash consistency, minor boundaries, optional filters,
multiple distinct services and majors, actual offered minors, bounded/count-only
output, offer lifecycle/replacement, and concurrent registration snapshots.
Sanitizer instrumentation is checked by binary symbols. Concurrency tests sample
executed interleavings; they do not prove every possible interleaving safe.
The baseline API compilation probe demonstrates missing new API, not a runtime
negative control. Earlier scoped runtime negative-control evidence is preserved
in the historical packet and is not relabelled as a full-model proof.

Native pins, locks, instructions, CI, lint and tool launcher are unchanged. No
external dependencies are added. The existing span dependency is reused; LLVM
and GCC results are measurements, not tool qualification evidence. Existing
`comp__socom` and `feat__someip_gateway` declarations are preserved; no fabricated
requirement IDs or acceptance states are introduced.

Remaining work belongs to actual reviewers and upstream execution: exact-revision
human AI review, public API/semantics/classification acceptance, net-new-IP and
required IP Team disposition, and remaining applicable CI. No native issue is
closed and no PR is published by this packet.
