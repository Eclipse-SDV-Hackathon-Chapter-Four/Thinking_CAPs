load("@rules_pkg//pkg:mappings.bzl", "pkg_filegroup")
load("//quality/integration_testing:integration_testing.bzl", "integration_test")

pkg_filegroup(
    name = "filesystem",
    srcs = [
        "//score/mw/com/test/api_idempotency:main_api_idempotency-pkg",
    ],
)

integration_test(
    name = "api_idempotency_test",
    timeout = "moderate",
    srcs = ["api_idempotency_test.py"],
    filesystem = ":filesystem",
)
