# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

import hashlib, json, sys
from pathlib import Path
import jsonschema_rs
from score_harness.common import load_harness
root=Path(sys.argv[1]); native=Path.cwd()
schema=json.loads((native/"scripts_bazel/traceability_metrics_schema.json").read_text())
harness=load_harness(native/"score_harness/harness/pinned_context_harness.py")
context_dir=root/"contexts";context_dir.mkdir(exist_ok=True)
results=[]
for path in sorted((root/"seed-specs").glob("*.json")):
    spec=json.loads(path.read_text())
    metrics=json.loads((native/spec["metrics_json_path"]).read_text())
    jsonschema_rs.validate(schema,metrics)
    context=harness.get_context(spec)
    assert context==harness.get_context(spec)
    parsed=json.loads(context)
    assert parsed["task_id"]==spec["id"]
    assert [rule["id"] for rule in parsed["consistency_rules"]]==sorted(set(spec["consistency_rules"]))
    (context_dir/(spec["id"]+".json")).write_text(context+"\n")
    for candidate in ["base_harness","pinned_context_harness"]:
        trace=root/"runs/iteration_002"/candidate/"traces"/spec["id"]
        assert {p.name for p in trace.iterdir()}=={"gate_output.json","impacted_elements.json","score.json"}
        gate=json.loads((trace/"gate_output.json").read_text())
        score=json.loads((trace/"score.json").read_text())
        impacts=json.loads((trace/"impacted_elements.json").read_text())
        assert isinstance(gate["gate_passed"],bool)
        assert gate["gate_returncode"] == (0 if spec["expected_verdict"]=="pass" else 2)
        assert score["verdict_correct"] is True
        assert score["expected_verdict"]==spec["expected_verdict"]
        assert isinstance(impacts,list)
        assert {"execution_timestamp","python_version","environment_hash","gate_script_version"} <= score["provenance"].keys()
        results.append({"task_id":spec["id"],"candidate":candidate,"expected_verdict":spec["expected_verdict"],"gate_returncode":gate["gate_returncode"],"context_sha256":hashlib.sha256(context.encode()).hexdigest()})
for candidate in ["base_harness","pinned_context_harness"]:
    run=json.loads((root/"runs/iteration_002"/candidate/"score.json").read_text())
    assert run["tasks_total"] == run["tasks_correct"] == 3
print(json.dumps({"status":"pass","metrics_schema":"native v2","trace_validation":"explicit native shape and verdict assertions; no complete native trace JSON schema supplied","results":results},indent=2))
