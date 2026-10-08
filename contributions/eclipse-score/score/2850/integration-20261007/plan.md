# Integration plan

1. Inspect both native packages, upstream #628 and current main.
2. Prefer extending the already proposed native interface when the adapter is compatible; avoid combining competing loaders/corpora in one contribution.
3. Prepare a disposable `contrib/score-2850-native-mvp` branch on the observed upstream `harness` head, stage the adapter patch and verify its exact source identity.
4. Check direct main applicability to identify the correct submission base.
5. Export a decision, source/command bindings, selected PR body and reproducible branch instructions. Update only #2850 routing and regenerate the parent packet manifest.
6. Verify the existing native packet and the combined parent packet. Leave native tests as carried evidence when source is byte-identical; do not transfer results to current main.
