# Prepared draft — human review required

# Improvement

> [!IMPORTANT]
> Use this template only for improvement that do not influence topics covered by contribution requests or bug fixes.

> [!CAUTION]
> Make sure to submit your pull-request as **Draft** until you are ready to have it reviewed by the Committers.

## Description

The three `mw_com_config.json` files duplicate the `LmControlService` service-type
definition. Generate them through a shared Bazel macro with `provider_test`, `client_test`
and `integration` profiles. The existing file labels and consumer paths stay available as
generated outputs, while the repeated service-type definition is maintained in one place.

All original per-profile values are preserved, including QM/ASIL-B, permission checks,
allowed providers, instance specifiers, queue sizes and subscriber limits. The three
checked-in JSON files are replaced by `config/mw_com_config.bzl` and calls from their
existing BUILD packages.

## Related ticket

Closes #704 (improvement ticket)

## Validation

Validated on upstream `7d1d7bec81d96752b5a9a235044d2dfc3ecd259b` using Bazel 8.7.0 on
x86_64 Linux in host mode, with isolated test network namespaces:

- All three Bazel-generated JSON objects equal the pinned original documents after parsing.
- `control_provider_UT`: 3 cases; `ilm_control_UT`: 2; `lm_control_impl_UT`: 36;
  `lifecycle_config_tests`: 71; `switch_run_target`: 1. All 113 cases passed, with no skips.
- Provider/client unit-test runfile payloads preserve their original paths and parsed values.
- The integration tar retains `tests/switch_run_target/etc/mw_com_config.json` with its original parsed values.
- Buildifier 8.5.1 format/lint checks and clean patch application pass.

QNX execution and full native impact/export closure were not measured. This is a
configuration/build cleanup with no C++ source changes; those wider assessments remain
outside these checks.


## AI assistance and review

- DeepSeek V4 Flash (Fabro; recorded model label)

This submission preparation was assisted by OpenAI Codex. Historical model labels above are retained as recorded; unrecorded versions and file-generation extent are not invented. Human review and applicable native/IP gates remain pending. No AI is a human coauthor.
