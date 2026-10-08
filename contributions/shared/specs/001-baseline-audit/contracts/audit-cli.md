# Baseline audit CLI

`python3 contributions/shared/scripts/audit_baseline.py --workspace-root "$HOME" --output evidence/<new-run-id>`
Reads selected repositories and runtime prerequisites. Writes new manifest.json/results.json only;
refuses an existing output directory. Does not start/stop containers or edit external checkouts.
Exit 0: all required live checks available. Exit 1: a failed check. Exit 2: blocked prerequisites.
This establishes readiness only, never closed-loop vehicle acceptance. Secrets are not inspected.
