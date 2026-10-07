#!/usr/bin/env bash
# Unit-test the contributed module doipClient (OpenBSW/contrib/libs/bsw/doipClient) inside
# the pinned OpenBSW tree, as OpenBSW CI would: the module is added to a git worktree of the
# pinned base on the build volume, formatted with OpenBSW's treefmt (changes are copied back
# to contrib/), built with the tests-posix-debug preset and run with ctest; gcovr measures
# coverage and clang-tidy checks the sources with the repository .clang-tidy.
#
#   OpenBSW/scripts/doip-client-test.sh            # format, test, tidy; records evidence
#
# Needs the tools of scripts/openbsw-pr.sh tools (treefmt, clang-format 17, cmake-format).
# Results: <volume>/openbsw-sil/runs/doipclient-<timestamp>/ and OpenBSW/evidence/doip-client-ut/
set -euo pipefail
source "$(dirname "$0")/storage.sh"

MODULE_SRC="$OBSW_DIR/contrib/libs/bsw/doipClient"
EVIDENCE="$OBSW_DIR/evidence/doip-client-ut"
WT="$OBSW_WORKSPACE/openbsw-doip-client"
BASE="$(lock "['openbsw']['revision']")"
RUN="${RUN:-$OBSW_WORKSPACE/runs/doipclient-$(date +%Y%m%d-%H%M%S)}"
export PATH="$OBSW_WORKSPACE/tools/bin:$OBSW_VENV/bin:$PATH"
mkdir -p "$RUN" "$EVIDENCE"

# --- sync: pinned base + module + registration lines ------------------------------------------
if [[ ! -d "$WT/.git" && ! -f "$WT/.git" ]]; then
  git -C "$OBSW_SRC" worktree add -q "$WT" -B feature/doip-client "$BASE"
fi
git -C "$WT" checkout -q -B feature/doip-client "$BASE"
git -C "$WT" reset -q --hard "$BASE"
git -C "$WT" clean -qfdx -e build
rsync -a --delete "$MODULE_SRC/" "$WT/libs/bsw/doipClient/"
python3 - "$WT" <<'EOF'
import sys, pathlib
wt = pathlib.Path(sys.argv[1])
def insert_after(path, anchor, line):
    p = wt / path; s = p.read_text()
    if line in s: return
    assert anchor in s, f"{anchor!r} not in {path}"
    p.write_text(s.replace(anchor, anchor + line, 1))
insert_after("libs/bsw/CMakeLists.txt", "    add_subdirectory(doip)\n", "    add_subdirectory(doipClient)\n")
insert_after("CMakeLists.txt", "        add_subdirectory(libs/bsw/doip/test)\n",
             "        add_subdirectory(libs/bsw/doipClient/test)\n")
EOF

# --- format: OpenBSW treefmt; formatted module files go back to contrib/ ----------------------
git -C "$WT" add -A
(cd "$WT" && treefmt --no-cache) > "$RUN/treefmt.txt" 2>&1 || { cat "$RUN/treefmt.txt"; exit 1; }
git -C "$WT" add -A
rsync -a --delete --exclude build "$WT/libs/bsw/doipClient/" "$MODULE_SRC/"
(cd "$WT" && treefmt --no-cache) >> "$RUN/treefmt.txt" 2>&1
if git -C "$WT" diff --exit-code > "$RUN/format-diff.txt"; then
  echo "format: clean" | tee -a "$RUN/treefmt.txt"
else
  echo "format: second pass changed files" >&2; exit 1
fi

# --- test: tests-posix-debug, ctest, coverage --------------------------------------------------
(cd "$WT" && cmake --preset tests-posix-debug > "$RUN/configure.log" 2>&1) || { tail -30 "$RUN/configure.log"; exit 1; }
build="$WT/build/tests/posix/Debug"
find "$build" -name '*.gcda' -delete 2>/dev/null || true
cmake --build "$build" --target doipClientTest --config Debug --parallel "$(nproc)" \
  > "$RUN/build.log" 2>&1 || { grep -E "error|Error" "$RUN/build.log" | head -40; exit 1; }
grep -c "warning:" "$RUN/build.log" > "$RUN/build-warnings.txt" || true
set +e
(cd "$build" && ctest -C Debug -L "doipClient" --output-junit "$RUN/junit.xml" --output-on-failure) \
  2>&1 | tee "$RUN/ctest.txt"
status=${PIPESTATUS[0]}
set -e
gcovr -r "$WT" --filter "$WT/libs/bsw/doipClient/src/" \
  --exclude "$WT/libs/bsw/doipClient/src/doip/client/DoIpClientLogger.cpp" \
  --exclude-throw-branches --exclude-unreachable-branches \
  --json-summary-pretty --json-summary "$RUN/coverage-summary.json" \
  --html-details "$RUN/coverage.html" --txt "$RUN/coverage.txt" "$build" > /dev/null
cat "$RUN/coverage.txt"

# --- tidy ---------------------------------------------------------------------------------------
clang-tidy --version | head -2 > "$RUN/clang-tidy.txt"
clang-tidy -p "$build" --quiet \
  "$WT/libs/bsw/doipClient/src/doip/client/DoIpClientConnection.cpp" \
  "$WT/libs/bsw/doipClient/src/doip/client/DoIpClientTransportLayer.cpp" \
  "$WT/libs/bsw/doipClient/src/doip/client/DoIpClientLogger.cpp" >> "$RUN/clang-tidy.txt" 2>&1 || true
findings=$(grep -cE "(warning|error): .*\[" "$RUN/clang-tidy.txt" || true)
echo "clang-tidy findings in module: $findings" | tee -a "$RUN/clang-tidy.txt"

cp "$RUN/junit.xml" "$RUN/ctest.txt" "$RUN/coverage.txt" "$RUN/coverage-summary.json" \
   "$RUN/clang-tidy.txt" "$RUN/treefmt.txt" "$RUN/build-warnings.txt" "$EVIDENCE/"
echo "$BASE" > "$EVIDENCE/openbsw-base.txt"
echo "results: $RUN (ctest exit $status)"
exit "$status"
