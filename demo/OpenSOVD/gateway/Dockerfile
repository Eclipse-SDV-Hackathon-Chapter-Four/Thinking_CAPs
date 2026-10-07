# Eclipse SDV Hackathon 2026 (Chapter Four) · Demo Console v2.1
# Goal: the real opensovd-gateway of inc_diagnostics PR #40 (feature/16-sovd-adapter-dataprovider, d388985)
#       in a container, serving component `cruise` on :7690 for the demo console.
#
#   docker compose -f docker/opensovd-gateway/docker-compose.yml up -d --build
#
# Bazel cannot build the binary yet (review finding CR-13), so the upstream sources are compiled
# in place by a Cargo workspace (harness/) that mirrors the Bazel targets; opensovd-core at 29e806f.

ARG RUST_IMAGE=rust:1-bookworm
FROM ${RUST_IMAGE} AS build
ARG INC_DIAGNOSTICS_REPO=https://github.com/eclipse-score/inc_diagnostics.git
ARG INC_DIAGNOSTICS_COMMIT=d388985e578e850cc17c4ac091f5d6be49c730ce
WORKDIR /build
RUN git init -q inc \
 && git -C inc fetch -q --depth 1 "$INC_DIAGNOSTICS_REPO" "$INC_DIAGNOSTICS_COMMIT" \
 && git -C inc checkout -q FETCH_HEAD
COPY harness/ harness/
RUN --mount=type=cache,target=/usr/local/cargo/registry \
    --mount=type=cache,target=/usr/local/cargo/git \
    --mount=type=cache,target=/build/harness/target \
    cd harness \
 && cargo build --locked --release -p opensovd-gateway \
 && cp target/release/opensovd-gateway /opensovd-gateway

FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=build /opensovd-gateway /usr/local/bin/opensovd-gateway
# Same environment variables as the Rust code; demo debounce values as in run.sh (Rust defaults 5000/2000).
ENV SCORE_GATEWAY_ADDRESS=127.0.0.1:7690 \
    CRUISE_DEBOUNCE_FAILED_MS=1500 \
    CRUISE_DEBOUNCE_PASSED_MS=1000 \
    RUST_LOG=info
EXPOSE 7690
HEALTHCHECK --interval=5s --timeout=2s --retries=3 \
  CMD curl -fsS "http://${SCORE_GATEWAY_ADDRESS}/sovd/version-info" >/dev/null || exit 1
ENTRYPOINT ["/usr/local/bin/opensovd-gateway"]
