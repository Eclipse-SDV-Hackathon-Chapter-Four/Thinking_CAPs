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

import sys
from run_check import run
prefix=['/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-2850-native-_qjqrtmg/bazel-8.4.2', '--output_user_root=/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-2850-native-_qjqrtmg/draft-bazel-user', '--output_base=/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-2850-native-_qjqrtmg/draft-bazel-output']
options=['--repository_cache=/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-2850-native-_qjqrtmg/cache/repository', '--disk_cache=/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-2850-native-_qjqrtmg/cache/draft-disk', '--lockfile_mode=error']
if __name__=="__main__":
 sys.exit(run(sys.argv[1],prefix+[sys.argv[2]]+options+sys.argv[3:]))
