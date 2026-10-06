# SPDX-License-Identifier: Apache-2.0
# Runtime for the S-CORE nodes. The binaries are built on the host with Bazel
# (demo/score/build.sh) and mounted at /opt/sdv, so code changes need no image rebuild.
FROM ubuntu:26.04
RUN apt-get update \
 && apt-get install -y --no-install-recommends libatomic1 libstdc++6 iproute2 procps tcpdump \
 && rm -rf /var/lib/apt/lists/*
ENV LD_LIBRARY_PATH=/opt/sdv/lib
