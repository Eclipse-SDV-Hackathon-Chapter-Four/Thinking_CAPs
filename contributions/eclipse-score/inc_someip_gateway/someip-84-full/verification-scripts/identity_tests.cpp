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
 * SPDX-License-Identifier: Apache-2.0 AND CC0-1.0
 * AI Disclosure: Generated with OpenAI Codex (model revision unavailable).
 * AI-generated portions are offered under CC0-1.0; copyrightable curation
 * retains Apache-2.0. Human review is pending.
 ********************************************************************************/

#include <array>
#include <atomic>
#include <cstdint>
#include <limits>
#include <optional>
#include <set>
#include <thread>
#include <unordered_set>
#include <vector>

#include "gtest/gtest.h"
#include "score/socom/service_interface_identifier.hpp"

namespace score::socom {
namespace {

TEST(ServiceIdentityTest, MinorVersionsShareCanonicalIdentityAndHash) {
    Service_interface const old_contract{std::string_view{"service"}, {1U, 0U}};
    Service_interface const new_contract{std::string_view{"service"}, {1U, 65535U}};
    EXPECT_EQ(old_contract.get_identifier(), new_contract.get_identifier());
    std::unordered_set<Service_interface_identifier> services{old_contract.get_identifier(),
                                                              new_contract.get_identifier()};
    EXPECT_EQ(1U, services.size());
    EXPECT_FALSE(old_contract == new_contract);
}

TEST(ServiceIdentityTest, DifferentIdsAndMajorsRemainSeparate) {
    Service_interface_identifier const first{std::string_view{"service"}, 1U};
    Service_interface_identifier const other_id{std::string_view{"other"}, 1U};
    Service_interface_identifier const other_major{std::string_view{"service"}, 2U};
    std::set<Service_interface_identifier> const ordered{first, other_id, other_major};
    std::unordered_set<Service_interface_identifier> const hashed{first, other_id, other_major};
    EXPECT_EQ(3U, ordered.size());
    EXPECT_EQ(3U, hashed.size());
}

TEST(ServiceIdentityTest, AllConstructorsUseRegisteredStringIdentity) {
    auto const registered = service_id_registry().insert(std::string_view{"service"}).first;
    Service_interface_identifier const by_registry{registered, 1U};
    Service_interface_identifier const by_view{std::string_view{"service"}, 1U};
    Service_interface_identifier const by_string{std::string{"service"}, 1U};
    Service_interface_identifier const by_literal{std::string_view{"service"}, Literal_tag{}, 1U};
    EXPECT_EQ(by_registry, by_view);
    EXPECT_EQ(by_view, by_string);
    EXPECT_EQ(by_string, by_literal);
    EXPECT_EQ(registered.data(), by_literal.id.data());
}

TEST(ServiceIdentityTest, FullInstanceIdentityIncludesActualMinorAndInstance) {
    Service_interface_identifier const service{std::string_view{"service"}, 1U};
    Service_instance const instance{std::string_view{"first"}};
    Service_instance_identifier const first{service, 0U, instance};
    Service_instance_identifier const different_minor{service, 1U, instance};
    Service_instance_identifier const different_instance{
        service, 0U, Service_instance{std::string_view{"second"}}};
    std::set<Service_instance_identifier> const ordered{first, different_minor, different_instance};
    std::unordered_set<Service_instance_identifier> const hashed{first, first, different_minor,
                                                                 different_instance};
    EXPECT_EQ(3U, ordered.size());
    EXPECT_EQ(3U, hashed.size());
    EXPECT_FALSE(first == different_minor);
    EXPECT_FALSE(first == different_instance);
}

class FindServiceCompatibilityTest
    : public ::testing::TestWithParam<std::tuple<std::uint16_t, std::uint16_t>> {};

TEST_P(FindServiceCompatibilityTest, MinimumMinorUsesCompatibleOfferSemantics) {
    auto const requested = std::get<0>(GetParam());
    auto const offered = std::get<1>(GetParam());
    Service_interface_identifier const service{std::string_view{"service"}, 1U};
    Find_service_request const request{service, requested, std::nullopt};
    Service_instance_identifier const offer{service, offered,
                                            Service_instance{std::string_view{"first"}}};
    EXPECT_EQ(requested <= offered, request.matches(offer));
}

INSTANTIATE_TEST_SUITE_P(Boundaries, FindServiceCompatibilityTest,
                         ::testing::Combine(::testing::Values<std::uint16_t>(0U, 1U, 42U, 65535U),
                                            ::testing::Values<std::uint16_t>(0U, 1U, 42U, 65535U)));

TEST(FindServiceRequestTest, MissingFiltersAcceptEveryMinorAndInstance) {
    Service_interface_identifier const service{std::string_view{"service"}, 1U};
    Find_service_request const request{service, std::nullopt, std::nullopt};
    EXPECT_TRUE(request.matches({service, 0U, Service_instance{std::string_view{""}}}));
    EXPECT_TRUE(request.matches({service, 65535U, Service_instance{std::string_view{"other"}}}));
}

TEST(FindServiceRequestTest, IdAndMajorMustMatchExactlyIncluding255) {
    Find_service_request const request{
        {std::string_view{"service"}, 255U}, std::nullopt, std::nullopt};
    EXPECT_TRUE(request.matches(
        {{std::string_view{"service"}, 255U}, 0U, Service_instance{std::string_view{"first"}}}));
    EXPECT_FALSE(request.matches(
        {{std::string_view{"service"}, 1U}, 0U, Service_instance{std::string_view{"first"}}}));
    EXPECT_FALSE(request.matches(
        {{std::string_view{"other"}, 255U}, 0U, Service_instance{std::string_view{"first"}}}));
}

TEST(FindServiceRequestTest, EmptyInstanceFilterIsAnExactId) {
    Service_interface_identifier const service{std::string_view{"service"}, 1U};
    Find_service_request const request{service, std::nullopt,
                                       Service_instance{std::string_view{""}}};
    EXPECT_TRUE(request.matches({service, 0U, Service_instance{std::string_view{""}}}));
    EXPECT_FALSE(request.matches({service, 0U, Service_instance{std::string_view{"other"}}}));
}


}  // namespace
}  // namespace score::socom
