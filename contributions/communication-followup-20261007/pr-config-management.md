Title: Draft: consume Communication AoUs in Config Management provider requirements

Config Management cannot consume Communication's restricted AoU target. This
companion proposal consumes the new public alias and adds the Communication
dependable element as a dependency of Config Management's native aggregation.

Safety decisions are explicitly deferred to a separate follow-up. This draft
provides a reviewable integration proposal and records the passing provider
build/TRLC checks; it does not establish production safety acceptance or complete
#1031. The deferred work covers shared-memory adequacy, QM/ASIL classification,
applicability/satisfaction/forwarding of every received AoU, and replacement or
formal disposition of placeholder safety records with valid root-cause and real
implementation/verification links. Existing classifications and safety records
remain as proposed pending that review.

`ConfigManagement.AdditionalProxyNeedsRegistration` becomes version 2 because
its derivation changes. It retains its existing feature link, description and
QM classification and adds `Communication.MonotonicSemiDynamicMemoryAllocation@1`.
The deferred native review must determine whether this derivation satisfies the
AoU and whether its classification is appropriate.

The current root's score_tooling 1.2.0 git override lacks the safety API needed
by Communication. The proposal aligns score_tooling to Communication's native
2.3.1 pin, preserves LLVM 19.1.0, adapts libclang to its native cc_toolchain API,
and maps the existing `:fmea` label to `safety_analysis`. Existing records,
labels and maturity remain intact. The dependency migration requires approval.

Provider build and TRLC validation pass with a real module override. The full
native traceability index fails on legacy placeholder safety records, including
the obsolete `mitigates` field and `ConfigDaemon.SampleAoU`, whose description
explicitly says the sample must never end up anywhere. The complete imported
AoU set still needs assessed satisfaction/applicability/forwarding dispositions.
No blanket forwarding, fabricated root causes or maturity reduction is used.

This companion remains a draft while the deferred safety work is outstanding.
The follow-up must correct/disposition those work products and validate the
complete native index, duplicate processing and forwarding behavior. Keep #1031
open; this proposal does not complete its production integration acceptance.

Dependency gate: the current Communication 0.5.0 release does not contain the
new public alias. Local verification uses `--override_module=score_communication`
against the patched checkout. Before publication, agree a native release or
approved commit pin containing that API; do not invent a release version or
commit the machine-local override. Run the final consumer checks on that pin.

Related: eclipse-score/communication#1031.

All current code has license notices, and the complete-repository copyright
check passes. The previous tooling formatter macro and Rust policy wrapper are
retained locally to preserve format target names, languages and policies after
the proposed upgrade. Prior raw checks remain source-bound historical evidence.
