#!/usr/bin/env bash
# Prepare and verify the upstream OpenBSW contribution "transportRouter".
#
# The module source lives in OpenBSW/contrib/libs/bsw/transportRouter (the gateway builds
# from it). This script rebuilds the PR branch from the pinned OpenBSW base in a git worktree
# on the external build volume and runs the checks OpenBSW CI runs on a pull request:
#
#   tools      treefmt 2.1.0, buildifier 8.5.1 (SHA-256 from OpenBSW's Dockerfile), cmakelang 0.6.13
#   sync       branch reset to the pinned base; module copied; registration lines added
#   format     treefmt --no-cache + git diff --exit-code (OpenBSW .ci/format.py); formatted
#              files are copied back to contrib/
#   copyright  tools/cr_checker on the changed files
#   test       tests-posix-debug preset: transportRouterTest via ctest, gcovr coverage
#   tidy       clang-tidy with the repository .clang-tidy on the module sources
#   bazel      bazel test of the new and the existing router module (bazelisk 1.29.0, pinned)
#   patch      commit (gitlint rules) and git format-patch into contributions/
#   all        everything above, in order
#
# Results: <volume>/openbsw-sil/runs/pr-<timestamp>/ and contributions/openbsw-transport-router/
set -euo pipefail
source "$(dirname "$0")/storage.sh"

REPO="$(cd "$OBSW_DIR/.." && pwd)"
MODULE_SRC="$OBSW_DIR/contrib/libs/bsw/transportRouter"
PACKET="$REPO/contributions/openbsw-transport-router"
WT="$OBSW_WORKSPACE/openbsw-pr"
TOOLS="$OBSW_WORKSPACE/tools/bin"
BASE="$(lock "['openbsw']['revision']")"
BRANCH="feature/transport-router"
RUN="${RUN:-$OBSW_WORKSPACE/runs/pr-$(date +%Y%m%d-%H%M%S)}"
export PATH="$TOOLS:$OBSW_VENV/bin:$PATH"
mkdir -p "$TOOLS" "$RUN"

fetch() { # url sha256 dest
  if [[ -x "$3" ]] && echo "$2  $3" | sha256sum -c --quiet 2>/dev/null; then return; fi
  curl -fsSL -o "$3.tmp" "$1"
  echo "$2  $3.tmp" | sha256sum -c --quiet
  mv "$3.tmp" "$3"; chmod +x "$3"
}

cmd_tools() {
  fetch https://github.com/bazelbuild/buildtools/releases/download/v8.5.1/buildifier-linux-amd64 \
    887377fc64d23a850f4d18a077b5db05b19913f4b99b270d193f3c7334b5a9a7 "$TOOLS/buildifier"
  if [[ ! -x "$TOOLS/treefmt" ]]; then
    curl -fsSL -o "$RUN/treefmt.tar.gz" \
      https://github.com/numtide/treefmt/releases/download/v2.1.0/treefmt_2.1.0_linux_amd64.tar.gz
    echo "ce0863a3a9d73707eb8cb9887c7f97ad3fd4ed506ad0429a6ab67a6290905966  $RUN/treefmt.tar.gz" | sha256sum -c --quiet
    tar -xzf "$RUN/treefmt.tar.gz" -C "$TOOLS" treefmt
  fi
  "$OBSW_VENV/bin/pip" install -q "cmakelang==0.6.13" "clang-format==17.0.6" "gitlint==0.19.1"
  # tools/clang-format-wrapper prefers clang-format-17; the wheel's --version ends in a hash
  ln -sf "$OBSW_VENV/bin/clang-format" "$TOOLS/clang-format-17"
  { treefmt --version; buildifier --version 2>&1 | head -1; cmake-format --version; clang-format --version; } | tee "$RUN/tools.txt"
}

cmd_sync() {
  if [[ ! -d "$WT/.git" && ! -f "$WT/.git" ]]; then
    git -C "$OBSW_SRC" worktree add -q "$WT" -B "$BRANCH" "$BASE"
  fi
  git -C "$WT" checkout -q -B "$BRANCH" "$BASE"
  git -C "$WT" reset -q --hard "$BASE"
  git -C "$WT" clean -qfdx -e build
  rsync -a --delete "$MODULE_SRC/" "$WT/libs/bsw/transportRouter/"
  python3 - "$WT" <<'EOF'
import sys, pathlib
wt = pathlib.Path(sys.argv[1])
def insert_after(path, anchor, line):
    p = wt / path; s = p.read_text()
    if line in s: return
    assert anchor in s, f"{anchor!r} not in {path}"
    p.write_text(s.replace(anchor, anchor + line, 1))
insert_after("libs/bsw/CMakeLists.txt", "    add_subdirectory(transportRouterSimple)\n",
             "    add_subdirectory(transportRouter)\n")
insert_after("CMakeLists.txt", "        add_subdirectory(libs/bsw/transportRouterSimple/test)\n",
             "        add_subdirectory(libs/bsw/transportRouter/test)\n")
EOF
  git -C "$WT" status --short | tee "$RUN/changed-files.txt"
}

cmd_format() {
  # treefmt walks git-tracked files: stage first, as CI runs on a committed tree
  git -C "$WT" add -A
  (cd "$WT" && treefmt --no-cache) > "$RUN/treefmt.txt" 2>&1 || { cat "$RUN/treefmt.txt"; exit 1; }
  git -C "$WT" add -A
  rsync -a --delete --exclude build "$WT/libs/bsw/transportRouter/" "$MODULE_SRC/"
  # OpenBSW .ci/format.py: treefmt --no-cache, then git diff --exit-code
  (cd "$WT" && treefmt --no-cache) >> "$RUN/treefmt.txt" 2>&1
  if git -C "$WT" diff --exit-code > "$RUN/format-diff.txt"; then
    echo "format: clean" | tee -a "$RUN/treefmt.txt"
  else
    echo "format: second pass changed files" >&2; exit 1
  fi
}

cmd_copyright() {
  local files
  files=$(git -C "$WT" diff --cached --name-only --diff-filter=AM "$BASE"; git -C "$WT" diff --name-only "$BASE")
  (cd "$WT" && python3 tools/cr_checker/cr_checker.py -t tools/cr_checker/templates.ini \
      -c tools/cr_checker/config.json --exclusion-file tools/cr_checker/exclusions.txt \
      $(echo "$files" | sort -u)) > "$RUN/copyright.txt" 2>&1 \
    && echo "copyright: ok" | tee -a "$RUN/copyright.txt" \
    || { cat "$RUN/copyright.txt"; exit 1; }
}

cmd_test() {
  (cd "$WT" && cmake --preset tests-posix-debug > "$RUN/configure.log" 2>&1)
  local build="$WT/build/tests/posix/Debug"
  find "$build" -name '*.gcda' -delete 2>/dev/null || true
  cmake --build "$build" --target transportRouterTest transportRouterSimpleTest --config Debug \
    --parallel "$(nproc)" > "$RUN/build.log" 2>&1 || { tail -40 "$RUN/build.log"; exit 1; }
  grep -c "warning:" "$RUN/build.log" > "$RUN/build-warnings.txt" || true
  (cd "$build" && ctest -C Debug -L "transportRouter" --output-junit "$RUN/junit.xml" \
     --output-on-failure) 2>&1 | tee "$RUN/ctest.txt"
  gcovr -r "$WT" --filter "$WT/libs/bsw/transportRouter/src/" \
    --exclude "$WT/libs/bsw/transportRouter/src/transport/TpGatewayLogger.cpp" \
    --exclude-throw-branches --exclude-unreachable-branches \
    --json-summary-pretty --json-summary "$RUN/coverage-summary.json" \
    --html-details "$RUN/coverage.html" --txt "$RUN/coverage.txt" "$build" > /dev/null
  cat "$RUN/coverage.txt"
}

cmd_tidy() {
  local build="$WT/build/tests/posix/Debug"
  clang-tidy --version | head -2 > "$RUN/clang-tidy.txt"
  clang-tidy -p "$build" --quiet \
    "$WT/libs/bsw/transportRouter/src/transport/routing/TransportRouter.cpp" \
    "$WT/libs/bsw/transportRouter/src/transport/routing/TransportRouterStatistics.cpp" \
    "$WT/libs/bsw/transportRouter/src/transport/TpGatewayLogger.cpp" \
    >> "$RUN/clang-tidy.txt" 2>&1 || true
  local findings
  findings=$(grep -cE "(warning|error): .*\[" "$RUN/clang-tidy.txt" || true)
  echo "clang-tidy findings in module: $findings" | tee -a "$RUN/clang-tidy.txt"
}

cmd_bazel() {
  fetch https://github.com/bazelbuild/bazelisk/releases/download/v1.29.0/bazelisk-linux-amd64 \
    5a408715e932c0250d28bd84555f12edbf70117de42f9181691c736eacc4a992 "$TOOLS/bazelisk"
  ln -sf bazelisk "$TOOLS/bazel"
  (cd "$WT" && BAZELISK_HOME="$OBSW_WORKSPACE/bazelisk" bazel --output_user_root="$OBSW_WORKSPACE/bazel-root" \
     test //libs/bsw/transportRouter/... //libs/bsw/transportRouterSimple/... --test_output=errors) \
    > "$RUN/bazel-test.txt" 2>&1 || { tail -30 "$RUN/bazel-test.txt"; exit 1; }
  grep -E "PASSED|FAILED|Executed" "$RUN/bazel-test.txt"
}

cmd_patch() {
  mkdir -p "$PACKET"
  git -C "$WT" add -A
  git -C "$WT" -c user.name="Jefferson Nascimento" -c user.email="jnsagai@gmail.com" \
    commit -q -s -F "$PACKET/commit-message.txt"
  gitlint --target "$WT" --config "$WT/.gitlint" > "$RUN/gitlint.txt" 2>&1 \
    && echo "gitlint: ok" | tee -a "$RUN/gitlint.txt" || { cat "$RUN/gitlint.txt"; exit 1; }
  git -C "$WT" format-patch -1 --stdout > "$PACKET/0001-transport-router.patch"
  git -C "$WT" rev-parse HEAD > "$RUN/commit.txt"
  echo "patch: $PACKET/0001-transport-router.patch"
}

case "${1:-all}" in
  tools) cmd_tools ;;
  sync) cmd_sync ;;
  format) cmd_format ;;
  copyright) cmd_copyright ;;
  test) cmd_test ;;
  tidy) cmd_tidy ;;
  bazel) cmd_bazel ;;
  patch) cmd_patch ;;
  all) cmd_tools; cmd_sync; cmd_format; cmd_copyright; cmd_test; cmd_tidy; cmd_bazel; cmd_patch ;;
  *) echo "usage: $0 [tools|sync|format|copyright|test|tidy|bazel|patch|all]" >&2; exit 2 ;;
esac
echo "results: $RUN"
