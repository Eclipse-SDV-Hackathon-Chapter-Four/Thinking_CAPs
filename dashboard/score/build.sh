#!/usr/bin/env bash
# SPDX-License-Identifier: Apache-2.0
#
# Builds the S-CORE side of the cruise control demo with Bazel and stages it in
# dashboard/score/out/ for the two containers (docker-compose.yml):
#   gatewayd, someipd              eclipse-score/inc_someip_gateway, unmodified
#   cruise_bridge, cruise_ecu      ours, dashboard/score/sdv_cruise/, built inside that workspace
#                                  so they use the same pinned mw::com as gatewayd
#
# On Apple Silicon (arm64), the build runs inside a --platform linux/amd64 Docker
# container with Rosetta emulation, because the S-CORE toolchains (GCC 12.2, Ferrocene)
# only run on x86_64 Linux.

set -euo pipefail

ROOT=$(cd "$(dirname "$0")/../.." && pwd)
HERE=$ROOT/dashboard/score
GW=$ROOT/upstream/inc_someip_gateway
GW_COMMIT=f8a196c3
OUT=$HERE/out

if [[ ! -d $GW ]]; then
    git clone https://github.com/eclipse-score/inc_someip_gateway.git "$GW"
    git -C "$GW" checkout -q "$GW_COMMIT"
fi
ln -sfn ../../dashboard/score/sdv_cruise "$GW/sdv_cruise"
grep -q "sdv_cruise overlay" "$GW/MODULE.bazel" || cat "$HERE/MODULE.overlay.bazel" >> "$GW/MODULE.bazel"

# Detect if we're on arm64 and need to use Docker for x86_64 build
ARCH=$(uname -m)
if [[ "$ARCH" == "aarch64" || "$ARCH" == "arm64" ]]; then
    echo "Building S-CORE in x86_64 Docker container (Rosetta emulation)..."

    # Run bazel build inside an x86_64 Ubuntu container
    docker run --rm --platform linux/amd64 \
        --device=lima-vm.io/rosetta=cached \
        -v "$ROOT:/workspace" \
        -v sdv-bazel:/root/.cache/bazel \
        -w /workspace/upstream/inc_someip_gateway \
        ubuntu:22.04 bash -c '
            set -ex
            apt-get update && apt-get install -y curl git build-essential libxml2-dev python3
            curl -L https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-amd64 -o /usr/local/bin/bazel
            chmod +x /usr/local/bin/bazel
            bazel build --lockfile_mode=update \
                --extra_toolchains=@ferrocene_x86_64_unknown_linux_gnu_llvm//:rust_ferrocene_toolchain \
                --jobs=2 --local_ram_resources=HOST_RAM*0.5 \
                //score/gatewayd //score/someipd //sdv_cruise:all
        '
else
    # Native x86_64 build
    FLAGS=(--lockfile_mode=update
           --extra_toolchains=@ferrocene_x86_64_unknown_linux_gnu_llvm//:rust_ferrocene_toolchain)
    if ! ldconfig -p | grep -q 'libxml2.so.2 '; then
        X=$HOME/.local/lib/bazel-xml2compat
        mkdir -p "$X"
        ln -sf "$(ldconfig -p | awk '/libxml2.so.[0-9]+ /{print $NF; exit}')" "$X/libxml2.so.2"
        FLAGS+=(--action_env=LD_LIBRARY_PATH="$X" --host_action_env=LD_LIBRARY_PATH="$X")
    fi
    (cd "$GW" && bazel build "${FLAGS[@]}" //score/gatewayd //score/someipd //sdv_cruise:all)
fi

rm -rf "$OUT"
mkdir -p "$OUT/bin" "$OUT/lib" "$OUT/etc"
B=$GW/bazel-bin
cp -L "$B/score/gatewayd/gatewayd" "$B/score/someipd/someipd" \
      "$B/sdv_cruise/cruise_bridge" "$B/sdv_cruise/cruise_ecu" "$OUT/bin/"
find -L "$B/_solib_k8" \( -name 'libvsomeip3*.so.3' -o -name 'score_com_serializer.so' \) -exec cp -L {} "$OUT/lib/" \;
cp "$B/sdv_cruise/vehicle_someip_config.bin" "$HERE/sdv_cruise/config/"*.json "$OUT/etc/"
echo "staged in $OUT:"
ls "$OUT/bin" "$OUT/lib"
