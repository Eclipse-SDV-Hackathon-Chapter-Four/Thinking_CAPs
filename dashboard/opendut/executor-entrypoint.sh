#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
# Runs one demo run into /results and signals EDGAR that the results are complete.
set -u
OUT=/results/run /demo/run-demo.sh
status=$?
echo "$status" > /results/exit-code
touch /results/.results_ready
exit "$status"
