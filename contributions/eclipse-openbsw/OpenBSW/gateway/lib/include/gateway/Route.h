// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <cstdint>

namespace gateway
{
enum class Transport : uint8_t
{
    DOCAN
};

/** One routing-table entry (SWR-010); generated from config/routing.yaml (SWR-052). */
struct Route
{
    uint16_t logicalAddress;
    char const* name;
    Transport transport;
    uint32_t requestCanId;
    uint32_t responseCanId;
    uint16_t p2Ms;
    uint16_t p2StarMs;
    uint16_t maxLength;
    uint32_t lostCommDtc;
};

} // namespace gateway
