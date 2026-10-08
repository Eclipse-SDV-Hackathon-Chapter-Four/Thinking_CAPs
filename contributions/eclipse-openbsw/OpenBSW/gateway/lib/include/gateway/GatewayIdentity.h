// SPDX-License-Identifier: Apache-2.0
#pragma once

#include <etl/span.h>

#include <cstdint>

namespace gateway
{
namespace identity
{
/** DID F190: 17-character VIN from the routing configuration. */
::etl::span<uint8_t const> vin();
/** DID F18C: ECU serial number. */
::etl::span<uint8_t const> ecuSerial();
/** DID F195: gateway version, OpenBSW revision and routing-table hash (SWR-021). */
::etl::span<uint8_t const> softwareVersion();
} // namespace identity
} // namespace gateway
