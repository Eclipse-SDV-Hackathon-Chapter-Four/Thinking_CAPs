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

#ifndef SRC_SOCOM_SRC_SERVICE_IDENTIFIER
#define SRC_SOCOM_SRC_SERVICE_IDENTIFIER

#include "score/socom/service_interface_identifier.hpp"

namespace score::socom {

/// Service instance identification information
///
/// This is only used to check if any (Disabled, Enabled) Server_connector for the given interface
/// and instance already exists.
///
/// For that check the interface is reduced to its service id and major version; the minor version
/// is a compatibility property of the instance and is intentionally not part of the identity (see
/// the operator< definition). This matches the minor-ignoring Service_database index.
struct Service_instance_identifier final {
    Service_interface_identifier interface;
    Service_instance instance;
};

/// \cond
bool operator<(Service_instance_identifier const& lhs, Service_instance_identifier const& rhs);
/// \endcond

}  // namespace score::socom

#endif  // SRC_SOCOM_SRC_SERVICE_IDENTIFIER
