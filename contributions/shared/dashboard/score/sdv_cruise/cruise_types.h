// SPDX-License-Identifier: Apache-2.0
//
// mw::com interfaces between the vehicle computer's apps and gatewayd.
//
// gatewayd moves SOME/IP payloads through shared memory unchanged
// (NullSerializer): each sample is a PreSerializedData, a size plus the raw
// big-endian SOME/IP payload. Both sides of link ④ must use exactly this layout.
//
//   cruise_status  (SOME/IP 0x4300.0001, event 0x8001, 12 bytes)
//     [0..4)  vehicle speed, km/h, IEEE-754 float32 BE
//     [4..8)  set speed, km/h, float32 BE (valid only when flags bit 0 is set)
//     [8]     state: 0 standby, 1 active, 2 unavailable
//     [9]     flags: bit 0 = set speed valid
//     [10..12) reserved
//   inject_fault   (SOME/IP 0x4301.0001, event 0x8001, 1 byte)
//     [0]     0 = release, 1 = speed sensor stuck

#ifndef SDV_CRUISE_CRUISE_TYPES_H
#define SDV_CRUISE_CRUISE_TYPES_H

#include "score/mw/com/types.h"
#include "score/serializer/pre_serialized_data.h"

namespace sdv_cruise {

constexpr std::size_t kCruiseStatusBytes = 12;
constexpr std::size_t kInjectFaultBytes = 1;

// max_message_size in vehicle_someip_config.json: 16 and 8.
using CruiseStatusSample = score::someip_gateway::serializer::PreSerializedData<16>;
using InjectFaultSample = score::someip_gateway::serializer::PreSerializedData<8>;

template <typename Trait>
class CruiseStatusInterface : public Trait::Base {
   public:
    using Trait::Base::Base;
    typename Trait::template Event<CruiseStatusSample> cruise_status_{*this, "cruise_status"};
};

template <typename Trait>
class DiagInjectionInterface : public Trait::Base {
   public:
    using Trait::Base::Base;
    typename Trait::template Event<InjectFaultSample> inject_fault_{*this, "inject_fault"};
};

using CruiseStatusProxy = score::mw::com::AsProxy<CruiseStatusInterface>;
using CruiseStatusSkeleton = score::mw::com::AsSkeleton<CruiseStatusInterface>;
using DiagInjectionProxy = score::mw::com::AsProxy<DiagInjectionInterface>;
using DiagInjectionSkeleton = score::mw::com::AsSkeleton<DiagInjectionInterface>;

}  // namespace sdv_cruise

#endif  // SDV_CRUISE_CRUISE_TYPES_H
