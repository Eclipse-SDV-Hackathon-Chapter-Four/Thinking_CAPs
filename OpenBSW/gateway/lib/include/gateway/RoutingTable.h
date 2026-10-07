// SPDX-License-Identifier: Apache-2.0
#pragma once

#include "gateway/Route.h"

#include <etl/span.h>

#include <cstddef>
#include <cstdint>

namespace gateway
{
/** Static routing table with start-up validation (ARC-04, SWR-010). */
class RoutingTable
{
public:
    static constexpr size_t INVALID_INDEX = 0xFFU;

    struct Addresses
    {
        uint16_t gateway;
        uint16_t functional;
        uint32_t functionalCanId;
        uint16_t testerMin;
        uint16_t testerMax;
    };

    enum class Error : uint8_t
    {
        NONE,
        EMPTY,
        DUPLICATE_ADDRESS,
        ADDRESS_CONFLICT,
        DUPLICATE_CAN_ID,
        CAN_ID_OUT_OF_RANGE,
        INVALID_TIMING,
        INVALID_LENGTH,
        INVALID_IP_ADDRESS,
        DUPLICATE_IP_ADDRESS
    };

    RoutingTable(Addresses const& addresses, ::etl::span<Route const> routes);

    /** Checks the rules of SWR-010; returns the first error and the offending index. */
    Error validate(size_t& badIndex) const;

    size_t indexOf(uint16_t logicalAddress) const;
    Route const* find(uint16_t logicalAddress) const;
    Route const& at(size_t index) const { return _routes[index]; }
    size_t size() const { return _routes.size(); }
    ::etl::span<Route const> routes() const { return _routes; }
    Addresses const& addresses() const { return _addresses; }

    bool isTesterAddress(uint16_t address) const
    {
        return (address >= _addresses.testerMin) && (address <= _addresses.testerMax);
    }

    static char const* errorText(Error error);

private:
    Addresses _addresses;
    ::etl::span<Route const> _routes;
};

} // namespace gateway
