# Integration campaign CLI and artifact contract
python3 scripts/run_campaign.py --config LOCAL_JSON --scenario core|cleanup-failure|carla --output NEW_DIR
Output: manifest.json, results.json, junit.xml, timeline.jsonl, summary.md, bounded child evidence.
Exit0 means all selected checks passed. Exit1 assertion/runtime/cleanup failure. Exit2 missing
prerequisite blocked. Independent-person reproduction is a separate signoff, not runner output.
Core mode fixture with real receiver/openDuT/native faults. CARLA mode actual simulation with
harness operator commands. Conditional/unselected checks explicitly skipped. Interruptions forward
to child cleanup and produce failed evidence; SIGKILL/power loss cannot guarantee finalization.
