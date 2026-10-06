# SPDX-License-Identifier: Apache-2.0
#
# openDuT container executor for the demo run (see openDuT user manual,
# "Test Execution"): EDGAR starts this container on a peer, it writes its
# evidence to /results and marks it with /results/.results_ready, then EDGAR
# uploads /results as a ZIP to the configured WebDAV results URL.
FROM debian:trixie-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends bash bc ca-certificates curl jq \
    && rm -rf /var/lib/apt/lists/*
COPY run-demo.sh /demo/run-demo.sh
COPY opendut/executor-entrypoint.sh /demo/entrypoint.sh
RUN chmod +x /demo/run-demo.sh /demo/entrypoint.sh && mkdir -p /results
ENTRYPOINT ["/demo/entrypoint.sh"]
