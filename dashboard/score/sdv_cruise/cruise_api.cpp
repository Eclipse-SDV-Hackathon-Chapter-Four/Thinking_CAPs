// SPDX-License-Identifier: Apache-2.0
// Makes the C++ mw::com interfaces in cruise_types.h usable from Rust (score_com).

#include "sdv_cruise/cruise_types.h"

#include <cstddef>

#include "score/mw/com/rust/score_com_cpp_bridge/register_interface.h"

BEGIN_EXPORT_MW_COM_INTERFACE(SdvCruiseStatus, ::sdv_cruise::CruiseStatusProxy,
                              ::sdv_cruise::CruiseStatusSkeleton)
EXPORT_MW_COM_EVENT(::sdv_cruise::CruiseStatusSample, cruise_status_)
END_EXPORT_MW_COM_INTERFACE()

BEGIN_EXPORT_MW_COM_INTERFACE(SdvDiagInjection, ::sdv_cruise::DiagInjectionProxy,
                              ::sdv_cruise::DiagInjectionSkeleton)
EXPORT_MW_COM_EVENT(::sdv_cruise::InjectFaultSample, inject_fault_)
END_EXPORT_MW_COM_INTERFACE()

EXPORT_MW_COM_TYPE(CruiseStatusSample, ::sdv_cruise::CruiseStatusSample)
EXPORT_MW_COM_TYPE(InjectFaultSample, ::sdv_cruise::InjectFaultSample)

// The Rust structs in cruise_api.rs mirror these; keep both in step.
static_assert(sizeof(::sdv_cruise::CruiseStatusSample) == 32, "CruiseStatusSample layout");
static_assert(offsetof(::sdv_cruise::CruiseStatusSample, data) == 16, "CruiseStatusSample layout");
static_assert(sizeof(::sdv_cruise::InjectFaultSample) == 32, "InjectFaultSample layout");
static_assert(offsetof(::sdv_cruise::InjectFaultSample, data) == 16, "InjectFaultSample layout");
