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

import json,sys
from pathlib import Path
from run_check import run
r=Path(__file__).resolve().parent
files=json.loads((r/"changed-files.json").read_text())
code=[p for p in files if p.endswith(".py")]
supported=[p for p in files if p.endswith((".py",".rst",".yml",".yaml")) or Path(p).name=="BUILD"]
commands=[("final-lint",[str(r/"verification-venv/bin/ruff"),"check",*code]),("final-format-check",[str(r/"verification-venv/bin/ruff"),"format","--check",*code]),("final-types",[str(r/"verification-venv/bin/basedpyright"),"--warnings",*code]),("final-copyright",[str(r/"verification-venv/bin/python"),"-B",str(r/"copyright-tool/cr_checker/tool/cr_checker.py"),"--template-file",str(r/"copyright-tool/cr_checker/resources/templates.ini"),"--config-file",str(r/"copyright-tool/cr_checker/resources/config.json"),*supported]),("final-workflow",[str(r/"actionlint/actionlint"),"-shellcheck=","-pyflakes=",".github/workflows/test.yml"])]
for name,cmd in commands:
 if run(name,cmd):sys.exit(1)
