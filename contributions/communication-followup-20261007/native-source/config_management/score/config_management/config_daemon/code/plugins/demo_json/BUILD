# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

load("@score_baselibs//:bazel/unit_tests.bzl", "cc_unit_test_suites_for_host_and_qnx")

cc_unit_test_suites_for_host_and_qnx(
    name = "unit_tests",
    test_suites_from_sub_packages = [
        "//score/config_management/config_daemon/code/plugins/demo_json/details:unit_tests",
        "//score/config_management/config_daemon/code/plugins/demo_json/parameter_loader/details:unit_tests",
        "//score/config_management/config_daemon/code/plugins/demo_json/plugin_creator:unit_tests",
    ],
    visibility = ["//score/config_management/config_daemon/code/plugins:__pkg__"],
)

filegroup(
    name = "demo_parameters",
    srcs = ["etc/demo_parameters.json"],
    visibility = [
        "//score/config_management/config_daemon/test:__subpackages__",
        "//visibility:public",
    ],
)
