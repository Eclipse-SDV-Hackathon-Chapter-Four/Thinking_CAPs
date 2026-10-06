# F001 quickstart

From repository root:
```bash
python3 -m unittest discover -s tests -p 'test_baseline_audit.py' -v
python3 scripts/audit_baseline.py --workspace-root "$HOME" --output evidence/f001-local-preflight
python3 scripts/verify_contributions.py
```
A blocked preflight exits 2 and writes the missing prerequisites. Reports distinguish available
builds from live CARLA/S-CORE/openDuT readiness. Never use README's historical demo result as evidence.
