<!-- ----------------------------------------------------------------------------
  Copyright (c) 2026 Contributors to the Eclipse Foundation

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
----------------------------------------------------------------------------- -->

# Formatter compatibility

The Apache-2.0 formatter macro and shell wrapper are retained from Eclipse S-CORE
tooling commit `835f219a1121b316c4c7809d983db1b4d31ebbcf`, which this module previously
pinned. Tooling 2.3.1 removes that entry point. Only the local wrapper label and
its source path change; Python, Rust, Starlark and YAML defaults and target names
remain the same. The wrapper still consumes the score_rust_policies configuration selected by the
native dependency graph; the added direct dependency has the same 0.0.2 minimum
as score_tooling 2.3.1. The local Communication override and released dependency
can select different module versions, so the final published pin needs validation.
