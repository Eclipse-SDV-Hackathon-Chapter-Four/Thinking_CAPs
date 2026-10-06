#!/bin/bash
# Resolve two root Bazel labels to their workspace-relative Git pathspecs.
# Retain every check argument, config/template and all input paths.
set -euo pipefail
score_copyright_root=/media/jefferson/11c42dee-73a3-4c2b-ab42-a0440011d9e0/.s-core-build/runs/score-fabric-7r64z_kz
score_copyright_program=$1
shift
[[ ${score_copyright_program##*/} == copyright.check ]]
score_copyright_args=()
score_copyright_build_count=0
score_copyright_module_count=0
for score_copyright_argument in "$@"; do
    case "$score_copyright_argument" in
        //:BUILD)
            score_copyright_args+=(BUILD)
            score_copyright_build_count=$((score_copyright_build_count + 1))
            ;;
        //:MODULE.bazel)
            score_copyright_args+=(MODULE.bazel)
            score_copyright_module_count=$((score_copyright_module_count + 1))
            ;;
        *) score_copyright_args+=("$score_copyright_argument") ;;
    esac
done
[[ $score_copyright_build_count == 1 && $score_copyright_module_count == 1 ]]
[[ -f "$score_copyright_root/candidate/BUILD" && -f "$score_copyright_root/candidate/MODULE.bazel" ]]
printf '%s\0' "$score_copyright_program" "$@" > "$score_copyright_root/copyright-argv-before.nul"
printf '%s\0' "$score_copyright_program" "${score_copyright_args[@]}" > "$score_copyright_root/copyright-argv-after.nul"
exec "$score_copyright_program" "${score_copyright_args[@]}"
