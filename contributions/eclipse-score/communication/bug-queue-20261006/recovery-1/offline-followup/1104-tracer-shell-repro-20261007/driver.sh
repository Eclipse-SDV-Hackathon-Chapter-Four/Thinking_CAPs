#!/bin/bash
# Mirrors rules_build_error run_shell: bash -c '"$@"' '' <script-without-shebang>
cd "$1"
echo "case: bash -c exec of shebang-less script"
bash -c '"$@"' '' ./noshebang.sh; echo "exit=$?"
g++ -c t.cpp -o t.o; echo "g++ exit=$?"
