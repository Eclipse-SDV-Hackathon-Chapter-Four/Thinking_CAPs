/********************************************************************************
 * Copyright (c) 2026 An Dao
 *
 * This program and the accompanying materials are made available under the
 * terms of the Apache License Version 2.0 which is available at
 * https://www.apache.org/licenses/LICENSE-2.0
 *
 * SPDX-License-Identifier: Apache-2.0
 ********************************************************************************/

// Modified for the zonal diagnostic gateway: registered DTCs, testFailedThisOperationCycle
// and pendingDTC bits, reportPassed(), clear keeps registered DTCs (SWR-025).

#pragma once

#include <etl/array.h>
#include <etl/span.h>

#include <cstdint>

namespace uds
{
/**
 * Minimal DTC manager for the diagnostic demo.
 * In-memory only (no NvM persistence).
 */
class DemoDtcManager
{
public:
    static size_t const MAX_DTCS = 16U;

    // ISO 14229-1 DTC status byte bits
    static uint8_t const STATUS_TEST_FAILED       = 0x01U;
    static uint8_t const STATUS_FAILED_THIS_CYCLE = 0x02U;
    static uint8_t const STATUS_PENDING           = 0x04U;
    static uint8_t const STATUS_CONFIRMED         = 0x08U;
    static uint8_t const STATUS_TEST_NOT_COMPLETE = 0x10U;

    struct DtcEntry
    {
        uint32_t dtcNumber; // 3-byte DTC (e.g. 0x123456)
        uint8_t statusByte;
        bool active;
    };

    DemoDtcManager();

    /** Makes a DTC supported (0x19 0A) with status testNotCompletedSinceLastClear. */
    void registerDtc(uint32_t dtcNumber);
    void reportFault(uint32_t dtcNumber);
    /** Test passed: clears testFailed, keeps the stored history bits. */
    void reportPassed(uint32_t dtcNumber);
    void clearAll();
    void clearByGroup(uint32_t groupOfDtc);

    uint16_t getCountByStatusMask(uint8_t statusMask) const;
    size_t getDtcsByStatusMask(uint8_t statusMask, ::etl::span<uint8_t> buffer) const;
    size_t getSupportedDtcs(::etl::span<uint8_t> buffer) const;

    void setDtcSettingEnabled(bool enabled) { _dtcSettingEnabled = enabled; }

    bool isDtcSettingEnabled() const { return _dtcSettingEnabled; }

private:
    DtcEntry* findOrCreate(uint32_t dtcNumber);
    // Serializes active DTCs (optionally filtered by status mask) as 4-byte
    // records (3-byte DTC number + 1 status byte). Returns the number of
    // serialized DTCs.
    size_t
    collectDtcs(::etl::span<uint8_t> buffer, bool filterByStatusMask, uint8_t statusMask) const;

    ::etl::array<DtcEntry, MAX_DTCS> _dtcs;
    size_t _dtcCount;
    bool _dtcSettingEnabled;
};

} // namespace uds
