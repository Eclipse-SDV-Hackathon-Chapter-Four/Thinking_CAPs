// SPDX-License-Identifier: Apache-2.0
#include "gateway/RoutingTable.h"

namespace gateway
{
namespace
{
constexpr uint32_t DIAG_CAN_MIN   = 0x7DFU;
constexpr uint32_t DIAG_CAN_MAX   = 0x7EFU;
constexpr uint16_t MAX_UDS_LENGTH = 4095U;

bool inDiagRange(uint32_t const canId) { return (canId >= DIAG_CAN_MIN) && (canId <= DIAG_CAN_MAX); }
} // namespace

RoutingTable::RoutingTable(Addresses const& addresses, ::etl::span<Route const> const routes)
: _addresses(addresses), _routes(routes)
{}

RoutingTable::Error RoutingTable::validate(size_t& badIndex) const
{
    badIndex = INVALID_INDEX;
    if (_routes.empty())
    {
        return Error::EMPTY;
    }
    if (!inDiagRange(_addresses.functionalCanId))
    {
        return Error::CAN_ID_OUT_OF_RANGE;
    }
    for (size_t i = 0U; i < _routes.size(); ++i)
    {
        Route const& route = _routes[i];
        badIndex           = i;
        if ((route.logicalAddress == _addresses.gateway)
            || (route.logicalAddress == _addresses.functional)
            || isTesterAddress(route.logicalAddress))
        {
            return Error::ADDRESS_CONFLICT;
        }
        if (!inDiagRange(route.requestCanId) || !inDiagRange(route.responseCanId))
        {
            return Error::CAN_ID_OUT_OF_RANGE;
        }
        if ((route.requestCanId == route.responseCanId)
            || (route.requestCanId == _addresses.functionalCanId)
            || (route.responseCanId == _addresses.functionalCanId))
        {
            return Error::DUPLICATE_CAN_ID;
        }
        if ((route.p2Ms == 0U) || (route.p2Ms > route.p2StarMs))
        {
            return Error::INVALID_TIMING;
        }
        if ((route.maxLength == 0U) || (route.maxLength > MAX_UDS_LENGTH))
        {
            return Error::INVALID_LENGTH;
        }
        for (size_t j = 0U; j < i; ++j)
        {
            Route const& other = _routes[j];
            if (other.logicalAddress == route.logicalAddress)
            {
                return Error::DUPLICATE_ADDRESS;
            }
            if ((other.requestCanId == route.requestCanId)
                || (other.requestCanId == route.responseCanId)
                || (other.responseCanId == route.requestCanId)
                || (other.responseCanId == route.responseCanId))
            {
                return Error::DUPLICATE_CAN_ID;
            }
        }
    }
    badIndex = INVALID_INDEX;
    return Error::NONE;
}

size_t RoutingTable::indexOf(uint16_t const logicalAddress) const
{
    for (size_t i = 0U; i < _routes.size(); ++i)
    {
        if (_routes[i].logicalAddress == logicalAddress)
        {
            return i;
        }
    }
    return INVALID_INDEX;
}

Route const* RoutingTable::find(uint16_t const logicalAddress) const
{
    size_t const index = indexOf(logicalAddress);
    return (index == INVALID_INDEX) ? nullptr : &_routes[index];
}

char const* RoutingTable::errorText(Error const error)
{
    switch (error)
    {
        case Error::NONE: return "ok";
        case Error::EMPTY: return "no routes";
        case Error::DUPLICATE_ADDRESS: return "duplicate logical address";
        case Error::ADDRESS_CONFLICT: return "address overlaps gateway, functional or tester range";
        case Error::DUPLICATE_CAN_ID: return "duplicate CAN identifier";
        case Error::CAN_ID_OUT_OF_RANGE: return "CAN identifier outside 0x7DF-0x7EF";
        case Error::INVALID_TIMING: return "invalid P2/P2* timing";
        case Error::INVALID_LENGTH: return "invalid maximum length";
        default: return "unknown";
    }
}

} // namespace gateway
