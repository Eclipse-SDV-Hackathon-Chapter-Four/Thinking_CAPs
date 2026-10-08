/********************************************************************************
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
 ********************************************************************************/
#include "score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h"
#include <gtest/gtest.h>
#include <memory>

namespace score::mw::com::impl::rust
{
namespace
{
std::size_t state_deletions{};
std::size_t discovery_deletions{};
}  // namespace

extern "C" void mw_com_impl_delete_boxed_fnmut_subscription_state(const FatPtr*) noexcept
{
    ++state_deletions;
}
extern "C" void mw_com_impl_delete_boxed_fnmut_find_service(const FatPtr*) noexcept
{
    ++discovery_deletions;
}

TEST(CallbackOwnership, FailedRegistrationRetainsRustOwnership)
{
    state_deletions = 0U;
    discovery_deletions = 0U;
    {
        auto state = std::make_shared<SubscriptionStateHandlerOwnership>(FatPtr{});
        auto discovery = std::make_shared<DiscoveryCallbackOwnership>(FatPtr{});
        // Model native rejection destroying its reference before returning.
        auto rejected_state = state;
        auto rejected_discovery = discovery;
        rejected_state.reset();
        rejected_discovery.reset();
    }
    EXPECT_EQ(state_deletions, 0U);
    EXPECT_EQ(discovery_deletions, 0U);
}

TEST(CallbackOwnership, ImmediateRemovalDisposesOnlyAfterTransfer)
{
    state_deletions = 0U;
    discovery_deletions = 0U;
    {
        auto state = std::make_shared<SubscriptionStateHandlerOwnership>(FatPtr{});
        auto discovery = std::make_shared<DiscoveryCallbackOwnership>(FatPtr{});
        auto native_state = state;
        auto native_discovery = discovery;
        // A synchronous callback removes the native reference during Set/Start.
        native_state.reset();
        native_discovery.reset();
        EXPECT_EQ(state_deletions, 0U);
        EXPECT_EQ(discovery_deletions, 0U);
        state->transferred = true;
        discovery->transferred = true;
    }
    EXPECT_EQ(state_deletions, 1U);
    EXPECT_EQ(discovery_deletions, 1U);
}

TEST(CallbackOwnership, NativeTeardownDisposesAcceptedHandlerExactlyOnce)
{
    state_deletions = 0U;
    discovery_deletions = 0U;
    auto native = std::make_shared<SubscriptionStateHandlerOwnership>(FatPtr{});
    auto native_discovery = std::make_shared<DiscoveryCallbackOwnership>(FatPtr{});
    {
        auto registration = native;
        registration->transferred = true;
        auto discovery_registration = native_discovery;
        discovery_registration->transferred = true;
    }
    EXPECT_EQ(state_deletions, 0U);
    EXPECT_EQ(discovery_deletions, 0U);
    native.reset();
    native_discovery.reset();
    EXPECT_EQ(state_deletions, 1U);
    EXPECT_EQ(discovery_deletions, 1U);
}
}  // namespace score::mw::com::impl::rust
