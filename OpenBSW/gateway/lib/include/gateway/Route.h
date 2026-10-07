// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <cstdint>

namespace gateway
{
enum class Transport : uint8_t
{
    DOCAN, ///< ISO-TP on CAN_0
    DOIP   ///< DoIP client connection to the node's DoIP entity (TCP 13400)
};

/** One routing-table entry (SWR-010); generated from config/routing.yaml (SWR-052). */
struct Route
{
    uint16_t logicalAddress;
    char const* name;
    Transport transport;
    uint32_t requestCanId;  ///< DoCAN only, 0 otherwise
    uint32_t responseCanId; ///< DoCAN only, 0 otherwise
    uint32_t ipAddress;     ///< DoIP only: IPv4 address in host byte order, 0 otherwise
    uint16_t p2Ms;
    uint16_t p2StarMs;
    uint16_t maxLength;
    uint32_t lostCommDtc;
};

} // namespace gateway
