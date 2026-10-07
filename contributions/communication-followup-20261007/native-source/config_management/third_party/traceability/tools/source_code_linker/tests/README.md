<!-- ----------------------------------------------------------------------------
  Copyright (c) 2026 Contributors to the Eclipse Foundation

  See the NOTICE file(s) distributed with this work for additional
  information regarding copyright ownership.

  This program and the accompanying materials are made available under the
  terms of the Apache License Version 2.0 which is available at
  https://www.apache.org/licenses/LICENSE-2.0

  SPDX-License-Identifier: Apache-2.0
----------------------------------------------------------------------------- -->

# Source Code Linker Tests

This directory contains comprehensive test suites for the source_code_linker package using external test data files.

## Test Structure

### test_data/
Contains external test input and expected output files:
- **input/**: Test input files (C++, Python, PlantUML files)
- **expected/**: Expected JSON output files for comparison

#### Input Files:

**Valid Input Files:**
- `sample_cpp.cpp`: C++ file with trace comments
- `sample_python.py`: Python file with trace comments
- `interface_sample.puml`: PlantUML interface with methods
- `component_sample.puml`: PlantUML components
- `fta_sample.puml`: PlantUML FTA events ($TopEvent, $BasicEvent)

**Negative Test Input Files:**
- `no_traces.cpp`: C++ file with no trace comments
- `invalid_traces.cpp`: C++ file with malformed trace comments
- `empty_plantuml.puml`: PlantUML file with no parseable elements
- `invalid_fta.puml`: PlantUML file with invalid FTA syntax

#### Expected Output Files:
- `cpp_code_expected.json`: Expected lobster format output for C++ parsing
- `python_code_expected.json`: Expected output for Python parsing
- `interface_plantuml_expected.json`: Expected output for interface parsing
- `component_plantuml_expected.json`: Expected output for component parsing
- `fta_plantuml_expected.json`: Expected output for FTA event parsing
