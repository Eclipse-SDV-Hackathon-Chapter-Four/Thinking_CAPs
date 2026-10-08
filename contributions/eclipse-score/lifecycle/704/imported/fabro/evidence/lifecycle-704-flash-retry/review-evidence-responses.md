# Draft responses to Flash advisory findings

The original [latest advisory output](critique-model-output.json) is unchanged.
These responses supply deterministic evidence; they do not accept or dismiss engineering
findings. Human review and full native impact/export closure remain pending.

| Finding | Supplied evidence and remaining boundary |
|---|---|
| High: missing repository-wide deleted-path consumer sweep | [Baseline/current inventory](consumer-inventory.json) scans all baseline tracked text and the current checkout. Known consumers are the two unchanged unit-test labels and shared integration packaging macro; generated filenames preserve them. Dynamic/external consumers and full native impact closure remain unmeasured. |
| Medium: table/array/raw-byte drift | [All-three configuration equivalence](configuration-equivalence.json) compares actual Bazel-generated objects with pinned original Git objects, including list ordering and every field. [Original bytes](original-source/) and [original hashes](original-configuration-hashes.json) are retained. JSON whitespace changes deliberately; raw-byte compatibility for hypothetical external consumers is not established. |
| Medium: unit-test runfiles not measured | [Unit runfiles equivalence](unit-runfiles-equivalence.json) records actual provider/client MANIFEST keys, generated payload paths/hashes and parsed equality. Both native unit targets passed. [Integration package](packaged-configuration-equivalence.json) separately records the exact tar member. |
| Low: integration/logging visibility allegedly narrowed | [Original BUILD](original-source/tests/utils/environments/BUILD) and [final BUILD](final-source/tests/utils/environments/BUILD) preserve the exact logging visibility and both integration subpackage visibility entries. Future visibility/applicability decisions remain human-owned. |
| Low: missing original config digests | [Original hashes](original-configuration-hashes.json), [original bytes](original-source/) and the pinned baseline retain all three removed source documents. |

The [earlier advisory](critique-before-retention-fix-model-output.json) also raised
missing configuration/package measurement concerns. The native output readers, XML and
tar measurements are deterministic evidence, separate from model self-check assertions.
The [final native checker](operator-scripts/verify_native_evidence.py.txt) pins source and
measurement files before the agent stage; [stale-worker replay](native-evidence-checker-negative.json)
rejects changed source. No statement here grants safety, readiness or engineering acceptance.
