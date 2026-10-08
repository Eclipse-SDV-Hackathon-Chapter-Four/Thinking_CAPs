FROM ubuntu:22.04 AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential cmake git ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /src
COPY CMakeLists.txt ./
COPY src ./src
COPY tests/test_protocol.c ./tests/test_protocol.c
# Host tests of the AZ3166 port's portable SLCAN codec (CMakeLists.txt, BUILD_TESTING)
COPY az3166/src/slcan.c az3166/src/slcan.h ./az3166/src/
COPY az3166/tests/test_slcan.c az3166/tests/test_slcan_edge.c ./az3166/tests/
RUN cmake -S . -B build -DCMAKE_BUILD_TYPE=Release \
    && cmake --build build -j 4 && ctest --test-dir build --output-on-failure

FROM ubuntu:22.04
RUN apt-get update && apt-get install -y --no-install-recommends \
    iproute2 can-utils python3 python3-pip ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /opt/threadx
COPY requirements.txt ./
RUN python3 -m pip install --no-cache-dir -r requirements.txt
ARG WITH_CARLA=0
RUN if [ "$WITH_CARLA" = 1 ]; then \
    python3 -m pip install --no-cache-dir carla==0.9.15 pygame==2.6.1 numpy==2.2.6; fi
COPY --from=build /src/build/threadx-zonal-lights /usr/local/bin/threadx-zonal-lights
COPY LICENSE /usr/share/licenses/threadx-zonal-lights/LICENSE
COPY THREADX-LICENSE.txt /usr/share/licenses/threadx/LICENSE.txt
COPY scripts ./scripts
COPY tests ./tests
CMD ["threadx-zonal-lights", "--interface", "vcan0"]
