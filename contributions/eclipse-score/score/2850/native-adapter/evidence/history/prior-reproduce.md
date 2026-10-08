# Verify and reproduce

From the Thinking_CAPs root:

```bash
python3 contributions/eclipse-score/score/2850/verify_packet.py
python3 contributions/shared/scripts/verify_contributions.py
```

The first command checks the packet SHA-256 manifest, every file inside the source
archive, and the original historical release manifest. The second checks all contributions
registered in this repository. Neither reruns native tests or establishes acceptance.

Fresh command arguments, working directories, source/archive hashes, timestamps, exit codes
and log hashes are in [commands.json](evidence/checks/commands.json). Python and Node/tool
versions and a Python environment inventory are retained beside it. The collector reused
the existing project virtualenv and frontend node_modules, imported backend code from the
disposable copy, and removed all SCORE_ASSISTANT_* overrides. Source-after records verify
that tracked scratch inputs and the original source remained unchanged.

To reproduce on a prepared machine, extract the archive into a new directory with Python
3.12, uv and Node/npm available. Install only the included lock versions (preparation may
need internet if packages are not cached):

```bash
work=$(mktemp -d)
tar -xzf contributions/eclipse-score/score/2850/evidence/source/s-core-bot-source.tar.gz -C "$work"
cd "$work"
uv sync --locked --all-groups --offline
uv run --no-sync ruff format --check .
uv run --no-sync ruff check .
uv run --no-sync mypy src
uv run --no-sync pytest -q -ra --junitxml=pytest.xml
cd frontend
npm ci --offline
npm run lint
npm run typecheck
npm test
npm run build
npm run check-no-third-party-assets
npm run check-no-telemetry
cd ..
uv run --no-sync python scripts/check_licenses.py
uv run --no-sync python scripts/check_traceability.py
```

Do not enable real-runtime/network opt-ins for the deterministic run. Missing cached
packages are a preparation blocker; an offline install failure is not a product failure.
Node 20.20.2 was available for this capture; the README recommends Node 22. The frontend
results establish the captured environment only.

Historical model benchmarks require the original model digests, corpus revisions,
snapshot and prepared hardware documented in the reports. Model weights and corpus
bundles are not included. No fresh model, GPU, browser, container, accessibility,
blocked-egress or native S-CORE harness qualification run is claimed.

