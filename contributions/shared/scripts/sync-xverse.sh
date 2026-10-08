#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Sync demo/X-Verse with the X-Verse baseline (The-Xverse/autoverse).
#
# demo/X-Verse is an exact copy of autoverse's dev/sdv-hackathon-2026 branch.
# It is never edited here: X-Verse changes are made and pushed in autoverse
# (or in a component repository), then brought in with this script, which
# replaces demo/X-Verse with the fetched branch and commits that on the
# current branch. Nothing outside demo/X-Verse is touched; nothing is pushed.
#
#   contributions/shared/scripts/sync-xverse.sh            sync and commit
#   contributions/shared/scripts/sync-xverse.sh --check    report the state only (exit codes below)
#
# Options:
#   --repo <url|path>   autoverse repository (default git@github.com:The-Xverse/autoverse.git,
#                       or $AUTOVERSE_REPO), e.g. ~/autoverse to sync from a local checkout
#   --branch <name>     branch to sync (default dev/sdv-hackathon-2026, or $AUTOVERSE_BRANCH)
#   --check             only report; exit 0 in sync, 1 behind, 2 edited directly
#   --dry-run           show what a sync would change, without committing
#   --force             sync even if demo/X-Verse was edited directly (those edits are replaced)
#
# Each sync commit carries the trailer "X-Verse-Source: <commit>", the
# autoverse commit demo/X-Verse now equals.

set -euo pipefail

if ( return 0 2>/dev/null ); then
    echo "This script is not meant to be sourced." >&2
    return 1
fi

REPO="${AUTOVERSE_REPO:-git@github.com:The-Xverse/autoverse.git}"
BRANCH="${AUTOVERSE_BRANCH:-dev/sdv-hackathon-2026}"
PREFIX="demo/X-Verse"
TMP_REF="refs/xverse-sync/source"
MODE="sync"
FORCE="false"

usage() { sed -n '4,25p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-0}"; }

while [[ $# -gt 0 ]]; do
    case "$1" in
        --repo)    REPO="$2"; shift 2 ;;
        --branch)  BRANCH="$2"; shift 2 ;;
        --check)   MODE="check"; shift ;;
        --dry-run) MODE="dry-run"; shift ;;
        --force)   FORCE="true"; shift ;;
        -h|--help) usage 0 ;;
        *) echo "Unknown option: $1" >&2; usage 1 ;;
    esac
done

cd "$(git rev-parse --show-toplevel)"
log() { echo "[sync-xverse] $*"; }
cleanup() { git update-ref -d "$TMP_REF" 2>/dev/null || true; }
trap cleanup EXIT

# ---------------------------------------------------------------- fetch

log "fetching $BRANCH from $REPO ..."
git fetch -q --no-tags "$REPO" "+refs/heads/$BRANCH:$TMP_REF"
SOURCE="$(git rev-parse "$TMP_REF")"
SOURCE_TREE="$(git rev-parse "$SOURCE^{tree}")"
CURRENT_TREE="$(git rev-parse -q --verify "HEAD:$PREFIX" || true)"

# The autoverse commit demo/X-Verse currently equals: the trailer of the last
# sync commit if it still matches, else a search of the branch history.
current_source() {
    local c
    c="$(git log -1 --format='%(trailers:key=X-Verse-Source,valueonly)' -- "$PREFIX" | tr -d '[:space:]')"
    if [[ -n "$c" ]] && git cat-file -e "$c^{tree}" 2>/dev/null \
            && [[ "$(git rev-parse "$c^{tree}")" == "$CURRENT_TREE" ]]; then
        echo "$c"; return
    fi
    git rev-list "$SOURCE" | while read -r c; do
        if [[ "$(git rev-parse "$c^{tree}")" == "$CURRENT_TREE" ]]; then echo "$c"; break; fi
    done
}

if [[ "$CURRENT_TREE" == "$SOURCE_TREE" ]]; then
    log "$PREFIX is in sync with $BRANCH ($(git rev-parse --short "$SOURCE"))"
    exit 0
fi

PREVIOUS="$(current_source)"
if [[ -n "$PREVIOUS" ]]; then
    log "$PREFIX is behind: it equals $(git rev-parse --short "$PREVIOUS"), $BRANCH is at $(git rev-parse --short "$SOURCE"):"
    git log --format='  %h %s' "$PREVIOUS..$SOURCE"
    STATE=1
else
    log "$PREFIX matches no commit of $BRANCH: it was edited directly in this repository."
    log "Make the change in autoverse instead. Paths that differ from $BRANCH:"
    git diff --name-status "$SOURCE_TREE" "${CURRENT_TREE:-$(git hash-object -t tree /dev/null)}" | sed 's/^/  /' | head -n 30
    STATE=2
fi

[[ "$MODE" == "check" ]] && exit "$STATE"

if [[ "$STATE" == 2 && "$FORCE" != "true" ]]; then
    log "Not syncing: --force would replace these edits with $BRANCH." >&2
    exit 2
fi

# ---------------------------------------------------------------- sync

if [[ -n "$(git status --porcelain -- "$PREFIX")" ]]; then
    log "$PREFIX has uncommitted changes; commit or discard them first." >&2
    exit 1
fi
git symbolic-ref -q HEAD > /dev/null || { log "HEAD is detached; switch to a branch first." >&2; exit 1; }

INDEX="$(mktemp)"; rm -f "$INDEX"
trap 'rm -f "$INDEX"; cleanup' EXIT
export GIT_INDEX_FILE="$INDEX"
git read-tree HEAD
git rm -r -q -f --cached --ignore-unmatch -- "$PREFIX"
git read-tree --prefix="$PREFIX/" "$SOURCE_TREE"
TREE="$(git write-tree)"
unset GIT_INDEX_FILE

SHORT="$(git rev-parse --short "$SOURCE")"
{
    echo "X-Verse: sync $PREFIX to autoverse $SHORT"
    echo
    echo "$PREFIX now equals The-Xverse/autoverse $BRANCH at $SHORT."
    if [[ -n "$PREVIOUS" ]]; then
        echo "Changes since $(git rev-parse --short "$PREVIOUS"):"
        echo
        git log --format='- %h %s' "$PREVIOUS..$SOURCE"
    else
        echo "This replaces direct edits of $PREFIX (synced with --force)."
    fi
    echo
    echo "X-Verse-Source: $SOURCE"
} > "$INDEX.msg"

if [[ "$MODE" == "dry-run" ]]; then
    log "dry run: the sync would commit"
    git diff --stat HEAD "$TREE" | tail -n 1
    sed 's/^/  | /' "$INDEX.msg"
    rm -f "$INDEX.msg"
    exit 0
fi

COMMIT="$(git commit-tree "$TREE" -p HEAD -F "$INDEX.msg")"
rm -f "$INDEX.msg"
git merge -q --ff-only "$COMMIT"
log "committed $(git rev-parse --short HEAD): $PREFIX = autoverse $SHORT ($(git diff --shortstat HEAD~1 HEAD))"
log "review with 'git show --stat', then push as usual"
