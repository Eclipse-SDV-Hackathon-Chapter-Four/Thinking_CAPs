# SPDX-License-Identifier: Apache-2.0
#
# Digital twin of the ThreadX zonal lighting ECU on AutoSD.
# Build stage: the unchanged ThreadX controller sources (staged by ctl.sh from
# X-Verse external_hackathon_ecus/ThreadX) on CentOS Stream 9, the base of the AutoSD container image.
# Runtime stage: the CentOS Automotive SIG's AutoSD container image (Stream 9
# with the AutoSD automotive repositories, pinned by digest) with the
# controller, the pinned Zenoh2CAN bridge and the unchanged bridge profile.

ARG AUTOSD_IMAGE=quay.io/centos-sig-automotive/autosd@sha256:85b5718d7fc05c11794b379883578f0eaa59e5cf7ace1d0329ff332fbd0b3d2a

FROM quay.io/centos/centos:stream9 AS build
RUN dnf -y install gcc make cmake git && dnf clean all
WORKDIR /src
COPY threadx/CMakeLists.txt ./
COPY threadx/src ./src
COPY threadx/tests/test_protocol.c ./tests/test_protocol.c
COPY threadx/az3166 ./az3166
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build -j 4 && ctest --test-dir build --output-on-failure

FROM ${AUTOSD_IMAGE}
RUN dnf -y install python3 python3-pip iproute && dnf clean all
COPY threadx/requirements.txt /opt/twin/requirements.txt
RUN python3 -m pip install --no-cache-dir -r /opt/twin/requirements.txt
COPY --from=build /src/build/threadx-zonal-lights /usr/local/bin/threadx-zonal-lights
COPY threadx/LICENSE /usr/share/licenses/threadx-zonal-lights/LICENSE
COPY threadx/THREADX-LICENSE.txt /usr/share/licenses/threadx/LICENSE.txt
COPY threadx/scripts/configure_bridge.py /opt/twin/configure_bridge.py
COPY bridge/bridge.py /opt/twin/bridge.py
COPY entrypoint.sh /opt/twin/entrypoint.sh
ENTRYPOINT ["/opt/twin/entrypoint.sh"]
