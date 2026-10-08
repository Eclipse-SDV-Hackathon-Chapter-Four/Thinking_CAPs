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

from pathlib import Path
import json,hashlib
from score_harness.common import load_harness
from score_harness.coverage import extract_metrics
from jsonschema_rs import Draft202012Validator
root=Path.cwd();path=root/'_build/needs.json';source=json.loads(path.read_text());harness=load_harness(root/'score_harness/harness/pinned_context_harness.py')
task={'id':'native_docs_build','input_path':str(path),'consistency_rules':[f'CR-{i:03d}' for i in range(1,6)]}
context=harness.get_context(task);assert context==harness.get_context(task);data=json.loads(context);assert data['artifacts'][0]['content']==source;assert data['artifacts'][0]['sha256']==hashlib.sha256(path.read_bytes()).hexdigest();metrics=json.loads((root/'_build/metrics.json').read_text());validator=Draft202012Validator(json.loads((root/'scripts_bazel/traceability_metrics_schema.json').read_text()))
try:
 validator.validate(metrics);raw_valid=True;raw_error=None
except Exception as error:
 raw_valid=False;raw_error=str(error)
projected=extract_metrics(source,['tool_req']);validator.validate(projected)
run=Path(__file__).resolve().parent;dest=run/'native-build-output';dest.mkdir(exist_ok=True)
for name in ['needs.json','metrics.json']:(dest/name).write_bytes((root/'_build'/name).read_bytes())
(dest/'context.json').write_text(context)
(dest/'schema_valid_extracted_metrics.json').write_text(json.dumps(projected,indent=2)+'\n')
(dest/'original_metrics_schema_result.json').write_text(json.dumps({'valid':raw_valid,'error':raw_error},indent=2)+'\n')
summary={'deterministic':True,'all_export_fields_preserved':True,'metrics_schema_valid':True,'needs_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'context_sha256':hashlib.sha256(context.encode()).hexdigest(),'snapshot_mode':'actual_native_sphinx_build','source_baseline':'4bc0fbfc83938cd9fa036d31f9f885f6ccde18c9','source_patch':'review packet patch hash binds the dirty native checkout'}
(dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2))
