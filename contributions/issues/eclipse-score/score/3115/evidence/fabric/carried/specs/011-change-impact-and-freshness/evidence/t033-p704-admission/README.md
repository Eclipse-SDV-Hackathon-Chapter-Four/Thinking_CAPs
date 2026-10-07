# Fresh paired P704 admission draft

Preparation is complete; real execution remains refused. Review
[the concrete scope decisions](review-report.md), [the check matrix](native/check-matrix.json)
and [the admission decision](admission-decision.json). No human gate runs inside a workflow.

Upstream baseline, public issue activity, provider documentation, source bindings,
matched original-source contexts and common output obligations are refreshed. Both
initial request reconstructions exceeded the unchanged 24,000-byte guard. Common
serialization changes reduce them to 23,939 bytes for baseline and 20,697 for optimized.
These are reconstructions using a retained native wrapper, not freshly emitted requests.
The baseline has only 61 bytes of headroom and requires actual native preflight.

The source archive and full contexts retain original source bytes and hashes. Both
prompts compact JSON whitespace, omit duplicate bound hash/accounting/discovery metadata,
and omit descriptive schema metadata. No source file, ordered value, validation constraint,
engineering obligation or operational limit is removed. Only the full versus selected
architecture content differs between arms. See [rendering policy](rendering-policy.json).

The newly documented final-content-chunk SSE usage shape passes the existing local
decoder and usage extractor with synthetic bytes. This phase starts no server, worker,
SDK download, native build or paid request. Actual provider bills and trial savings stay
null. The 11 historical packets, 1,557 packet subjects, 20 reviewed T032 subjects and
305 source/test files retain their exact hashes. Previous tests are carried by unchanged
source bindings, not described as fresh execution. Repository checks are recorded separately.

The owner’s existing DeepSeek budget exception is preserved. The draft does not ask
for another monetary ceiling or silently grant engineering acceptance. Native scope,
QNX/dependency closure, named roles and fresh runtime bindings remain unresolved.
The PR release stays deferred. `manifest.json` seals this packet and current control bytes;
old packet control hashes remain historical.
