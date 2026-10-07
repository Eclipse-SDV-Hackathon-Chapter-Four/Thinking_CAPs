// SPDX-License-Identifier: Apache-2.0
#include "gateway/GatewayIdentity.h"

#include "gateway/RoutingConfig.h"

#include <cstring>

#ifndef GATEWAY_VERSION
#define GATEWAY_VERSION "0.0.0"
#endif
#ifndef OPENBSW_REVISION
#define OPENBSW_REVISION "unknown"
#endif

namespace gateway
{
namespace identity
{
namespace
{
::etl::span<uint8_t const> asBytes(char const* const text)
{
    return ::etl::span<uint8_t const>(
        reinterpret_cast<uint8_t const*>(text), static_cast<size_t>(::std::strlen(text)));
}

// e.g. "zgw 0.1.0 obsw 432b9be6 rt b4bdeccc"
constexpr char const SOFTWARE_VERSION[] = "zgw " GATEWAY_VERSION " obsw " OPENBSW_REVISION " rt ";
char softwareVersionText[sizeof(SOFTWARE_VERSION) + 8U] = {};
} // namespace

::etl::span<uint8_t const> vin() { return asBytes(config::VIN); }

::etl::span<uint8_t const> ecuSerial() { return asBytes(config::ECU_SERIAL); }

::etl::span<uint8_t const> softwareVersion()
{
    if (softwareVersionText[0] == '\0')
    {
        (void)::std::memcpy(softwareVersionText, SOFTWARE_VERSION, sizeof(SOFTWARE_VERSION) - 1U);
        (void)::std::strncpy(
            &softwareVersionText[sizeof(SOFTWARE_VERSION) - 1U], config::ROUTING_TABLE_HASH, 8U);
    }
    return asBytes(softwareVersionText);
}

} // namespace identity
} // namespace gateway
