/*******************************************************************************
 * Copyright (c) 2026 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 *******************************************************************************/

#include "score/mw/com/test/basic_rust_api/bigdata_com_api_gen.h"
#include "score/mw/com/rust/score_com_cpp_bridge/register_interface.h"

// Register the BigData interface with the com-api FFI bridge.
// The explicit find-any selector points at a configured instance entry without a Lola instance
// id, enabling typed `FindServiceSpecifier::Any` discovery for BigDataInterface.
BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER(BigDataInterface,
                                                 ::score::mw::com::test::BigDataProxy,
                                                 ::score::mw::com::test::BigDataSkeleton,
                                                 "/score/cp60/MapApiLanesStampedAny")
EXPORT_MW_COM_EVENT(::score::mw::com::test::MapApiLanesStamped, map_api_lanes_stamped_)
EXPORT_MW_COM_EVENT(::score::mw::com::test::DummyDataStamped, dummy_data_stamped_)
END_EXPORT_MW_COM_INTERFACE()

// Export data types so that the Rust-side CommData::ID can resolve them.
EXPORT_MW_COM_TYPE(MapApiLanesStamped, ::score::mw::com::test::MapApiLanesStamped)
EXPORT_MW_COM_TYPE(DummyDataStamped, ::score::mw::com::test::DummyDataStamped)

// Test for primitive and complex data types, used in the com-api integration tests.
BEGIN_EXPORT_MW_COM_INTERFACE(MixedPrimitivesInterface,
                              ::score::mw::com::test::MixedPrimitivesProxy,
                              ::score::mw::com::test::MixedPrimitivesSkeleton)
EXPORT_MW_COM_EVENT(::score::mw::com::test::MixedPrimitivesPayload, mixed_event)
END_EXPORT_MW_COM_INTERFACE()

BEGIN_EXPORT_MW_COM_INTERFACE(ComplexStructInterface,
                              ::score::mw::com::test::ComplexStructProxy,
                              ::score::mw::com::test::ComplexStructSkeleton)
EXPORT_MW_COM_EVENT(::score::mw::com::test::ComplexStruct, complex_event)
END_EXPORT_MW_COM_INTERFACE()

// Export all types
EXPORT_MW_COM_TYPE(MixedPrimitivesPayload, ::score::mw::com::test::MixedPrimitivesPayload)
EXPORT_MW_COM_TYPE(ComplexStruct, ::score::mw::com::test::ComplexStruct)

// Test-only registrations used solely to prove that the typed Any path rejects selectors that do
// not resolve to a genuine LoLa wildcard. These reuse the BigData proxy/skeleton types because the
// rejection happens before any proxy is created; no consumer is ever built for them.
//
// ConcreteSelectorInterface maps to a configured instance specifier that HAS an instance id
// (/score/cp60/MapApiLanesStamped -> instanceId 1), so a wildcard query must be rejected rather
// than silently returning that Specific instance.
BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER(ConcreteSelectorInterface,
                                                 ::score::mw::com::test::BigDataProxy,
                                                 ::score::mw::com::test::BigDataSkeleton,
                                                 "/score/cp60/MapApiLanesStamped")
END_EXPORT_MW_COM_INTERFACE()

// MalformedSelectorInterface maps to a syntactically invalid instance specifier (consecutive
// slashes), so creating/resolving the selector must fail and the wildcard query must be rejected.
BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER(MalformedSelectorInterface,
                                                 ::score::mw::com::test::BigDataProxy,
                                                 ::score::mw::com::test::BigDataSkeleton,
                                                 "/bad//selector")
END_EXPORT_MW_COM_INTERFACE()

// EmptySelectorInterface maps to a valid find-any selector for a service type that no provider
// ever offers in these tests, so the documented no-offer (empty) native outcome can be asserted
// deterministically.
BEGIN_EXPORT_MW_COM_INTERFACE_WITH_ANY_SPECIFIER(EmptySelectorInterface,
                                                 ::score::mw::com::test::BigDataProxy,
                                                 ::score::mw::com::test::BigDataSkeleton,
                                                 "/score/test/DummyAny")
END_EXPORT_MW_COM_INTERFACE()
