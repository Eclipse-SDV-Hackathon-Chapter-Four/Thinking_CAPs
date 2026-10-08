/********************************************************************************
 * Copyright (c) 2025 Contributors to the Eclipse Foundation
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

#include "service_identifier.hpp"

#include <tuple>

namespace score::socom {

bool operator<(Service_instance_identifier const& lhs, Service_instance_identifier const& rhs) {
    // The minor version is deliberately excluded from the registration key. It selects a compatible
    // instance of a service, but it does not identify the service ("service identifier = service id
    // + major", issue #84). Keeping the key on (instance, service id, major) makes it agree with
    // the minor-ignoring Service_database index, so any two configurations that resolve to the same
    // Service_record also collide here and are rejected as duplicate_service. The exact-major and
    // client-minor <= server-minor compatibility rules are unrelated to identity and remain
    // enforced by is_interface_compatible.
    return std::tie(lhs.instance, lhs.interface.id, lhs.interface.version.major) <
           std::tie(rhs.instance, rhs.interface.id, rhs.interface.version.major);
}

}  // namespace score::socom
