# Offline human review — pending

Review the candidate patch and `subjects-<issue>.json`, exact baseline, tool/lock
identities, `verification.json` and `artifact-manifest.json`. A decision must name
the issue, candidate patch SHA-256, source manifest SHA-256 and packet manifest
SHA-256, plus authenticated reviewer identity, authorized role, date, disposition
and rationale. Any source/contract change needs affected checks and a new binding.
These instructions are a review proposal, not a new native approval mechanism.

| Decision | Concrete review subject | Role to establish | Current state |
| --- | --- | --- | --- |
| #1261 D1 | Accept configured LoLa types as system-wide scope, or require unconfigured-type/other-binding enumeration and revise the acceptance/design | Communication API/design owner | Pending |
| #1261 D6 | Permit and bound callback allocation, or require a design satisfying an adopted operating-phase allocation constraint | Allocation/safety authority for the adopted profile | Pending; applicability unknown |
| #1261 ABI | Confirm coordinated rebuild/migration after appended `IRuntime` virtual and Rust/FFI additions; identify affected external implementers | Native API/ABI owner and integrators | Historical local D4 recorded; upstream approval pending |
| #250 scope | Accept typed Any as a scoped improvement and assign heterogeneous discovery to #1261; retain latest-snapshot/no-offer async semantics | Communication API owner / issue owner | Pending |
| #250 errors/warnings | Choose a typed bridge error and source migration, or explicitly justify a native warning disposition for new Any `Result<_, ()>` | Rust API/policy owner | Pending; no exception approved |
| #560 contract | Reconcile native state/get/set/unset requirements, fallible Rust unset, callback false, replacement, drop, reentrancy, errors and allocation | Native event API/FFI owner | Pending |
| Native trace | Accept requirement/design/safety impact and Rust applicability for the TRLC anchors; identify missing detailed-design/work-product instances | Requirements/design/safety roles under actual project tailoring | Pending |
| Verification | Resolve each failed/unrun/ignored/unknown applicable check, including downstream/platform and qualified-tool scope | Verification owner | Pending |
| Independent engineering review | Review full implementation/unsafe invariants, not only the warning patches; agree findings and residual risks | Authorized reviewer with required independence | Pending; agent reports are advisory |
| Contributor and IP review | Verify original authors and contribution rights, AI provenance, notices/dependencies and valid ECA for each contributor | Contributors and Eclipse project committer/IP authority | Pending |

The existing #1167 record declares Eclipse username `jnascimento6p0` and retains a
successful official ECA username lookup. That evidence is carried here and a fresh
read-only lookup is recorded. The original three patches name author
`jnsagai <jnsagai@gmail.com>`; username lookup does not establish that this commit
email/linkage is eligible or that the complete contribution has IP clearance.
The [official API](https://webdev.eclipse.org/docs/api/git-eca-rest-api/) distinguishes
user lookup from commit validation. #1167's engineering decision applies to its
own subjects and is not transferred to these proposals.

Native `CONTRIBUTING.md`, `LICENSE`, `NOTICE`, `MODULE.bazel` and lock are retained
as exact inputs. No dependency/policy/toolchain pin or license text changes are
proposed by the warning corrections. This does not replace reviewing the complete
earlier implementations or their generated code and third-party provenance.

Native `.github/CODEOWNERS` lists `@castler`, `@hoe-jo`, `@LittleHuba`, `@crimson11`,
`@bemerybmw` and `@limdor` as default owners at this baseline. Applicable roles,
independence and availability remain unverified. No notification has been sent.
The native review-checklists configuration is empty; it supplies no completed
review checklist or permission to synthesize approval.

Reviewer identity / authenticated decision reference: pending.

Review subjects / hashes: pending reviewer binding to the final packet.

Disposition / rationale / date: pending.
