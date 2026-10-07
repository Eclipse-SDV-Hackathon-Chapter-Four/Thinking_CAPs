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

/// \file registry_bridge_macro.cpp
/// \brief C FFI wrapper implementations for COM-API that use registry-based type resolution
/// \details This file provides extern "C" functions that implement the COM-API FFI using the registry-based approach
/// defined in registry_bridge_macro.h. These functions are called by Rust code through FFI and provide safe,
/// C-compatible interfaces to the C++ COM-API implementation.
/// The actual logic of these functions relies on the type and interface registries to resolve the correct operations at
/// runtime. The functions bridge between:
/// - Rust side: String-based, safe wrapper APIs
/// - C++ side: Template-based, type-erased implementation

#include "score/mw/com/impl/rust/com-api/com-api-ffi-lola/registry_bridge_macro.h"
#include "score/mw/com/impl/binding_type.h"
#include "score/mw/com/impl/configuration/lola_service_instance_id.h"
#include "score/mw/com/impl/configuration/lola_service_type_deployment.h"
#include "score/mw/com/impl/configuration/service_identifier_type.h"
#include "score/mw/com/impl/configuration/service_version_type.h"
#include "score/mw/com/impl/find_service_handler.h"
#include "score/mw/com/impl/handle_type.h"
#include "score/mw/com/impl/i_runtime.h"
#include "score/mw/com/impl/instance_identifier.h"
#include "score/mw/com/impl/plumbing/sample_ptr.h"
#include "score/mw/com/impl/proxy_base.h"
#include "score/mw/com/impl/proxy_event.h"
#include "score/mw/com/impl/proxy_event_base.h"
#include "score/mw/com/impl/runtime.h"
#include "score/mw/com/impl/skeleton_base.h"
#include "score/mw/com/impl/skeleton_event.h"
#include "score/mw/com/impl/skeleton_event_base.h"
#include "score/mw/com/runtime.h"
#include "score/mw/com/types.h"
#include "score/mw/log/logging.h"
#include "score/string_manipulation/arguments/arguments.h"

#include <cstdint>
#include <limits>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace score::mw::com::impl::rust
{

namespace
{

/// \brief Resolve an interface's registered find-any selector to a genuine wildcard identifier.
/// \details The selector is trusted only when it resolves (through `IRuntime::resolve`) to exactly
/// one identifier whose deployment is a supported LoLa binding and whose instance id is unset. A
/// selector that resolves to a concrete instance id (a misconfigured registration) or to an
/// unsupported binding is rejected here, so the typed Any path can never silently return Specific
/// results merely because a registration string happened to name a concrete instance.
/// \param interface_id UTF-8 interface registry UID
/// \return The validated wildcard InstanceIdentifier, or `std::nullopt` when the interface is
///         unmapped/malformed or the selector is concrete/ambiguous/unsupported.
std::optional<::score::mw::com::impl::InstanceIdentifier> ResolveFindAnyIdentifier(const std::string_view interface_id)
{
    auto* registry = GlobalRegistryMapping::FindInterfaceRegistry(interface_id);
    if (registry == nullptr)
    {
        return std::nullopt;
    }

    const std::string& any_instance_specifier = registry->GetAnyInstanceSpecifier();
    if (any_instance_specifier.empty())
    {
        return std::nullopt;
    }

    auto instance_specifier_result = ::score::mw::com::InstanceSpecifier::Create(std::string{any_instance_specifier});
    if (!instance_specifier_result.has_value())
    {
        return std::nullopt;
    }

    const auto instance_identifiers =
        ::score::mw::com::impl::Runtime::getInstance().resolve(instance_specifier_result.value());
    if (instance_identifiers.size() != 1U)
    {
        return std::nullopt;
    }

    const auto& instance_identifier = instance_identifiers.front();
    ::score::mw::com::impl::InstanceIdentifierView instance_identifier_view{instance_identifier};
    if (instance_identifier_view.GetServiceInstanceDeployment().GetBindingType() !=
        ::score::mw::com::impl::BindingType::kLoLa)
    {
        return std::nullopt;
    }
    if (instance_identifier_view.GetServiceInstanceId().has_value())
    {
        return std::nullopt;
    }

    return instance_identifier;
}

/// \brief Opaque, owned list of configured LoLa service-type identities.
/// \details Returned by mw_com_impl_enumerate_service_types() and freed by
///          mw_com_impl_service_type_list_delete(). The Rust side treats this as an opaque pointer and copies
///          the string identity out of it while the list is alive.
struct NativeServiceTypeList
{
    struct Entry
    {
        std::string name;
        std::uint32_t major;
        std::uint32_t minor;
        std::uint32_t binding;
        std::uint32_t service_id;
    };
    std::vector<Entry> entries;
};

}  // namespace

extern "C" {

/// \brief Get event pointer from proxy by event name
/// \details Retrieves an event from a proxy instance by string name.
/// The returned pointer should be cast to ProxyEvent<T>* where T is the event type.
/// \param proxy_ptr Opaque proxy pointer (actually ProxyType*)
/// \param interface_id UTF-8 string view of interface ID
/// \param event_id UTF-8 string view of event name
/// \return Pointer to ProxyEventBase if found, nullptr otherwise
ProxyEventBase* mw_com_get_event_from_proxy(ProxyBase* proxy_ptr, StringView interface_id, StringView event_id)
{
    if (proxy_ptr == nullptr || interface_id.data == nullptr || event_id.data == nullptr)
    {
        return nullptr;
    }
    auto event = static_cast<std::string_view>(event_id);
    auto id = static_cast<std::string_view>(interface_id);

    auto* registry = GlobalRegistryMapping::FindMemberOperation(id, event);

    if (registry == nullptr)
    {
        return nullptr;
    }
    return registry->GetProxyEvent(proxy_ptr);
}

/// \brief Get event pointer from skeleton by event name
/// \details Retrieves an event from a skeleton instance by string name.
/// Similar to mw_com_get_event_from_proxy but for skeleton instances.
/// \param skeleton_ptr Opaque skeleton pointer (actually SkeletonType*)
/// \param interface_id UTF-8 string view of interface ID
/// \param event_id UTF-8 string view of event name
/// \return Pointer to SkeletonEventBase if found, nullptr otherwise
SkeletonEventBase* mw_com_get_event_from_skeleton(SkeletonBase* skeleton_ptr,
                                                  StringView interface_id,
                                                  StringView event_id)
{
    if (skeleton_ptr == nullptr || interface_id.data == nullptr || event_id.data == nullptr)
    {
        return nullptr;
    }
    auto event = static_cast<std::string_view>(event_id);
    auto id = static_cast<std::string_view>(interface_id);

    auto* registry = GlobalRegistryMapping::FindMemberOperation(id, event);

    if (registry == nullptr)
    {
        return nullptr;
    }
    return registry->GetSkeletonEvent(skeleton_ptr);
}

/// \brief Send data via a skeleton event by name
/// \details Sends event data to all subscribed proxy instances.
/// \param event_ptr Opaque skeleton event pointer (SkeletonEvent<T>*)
/// \param type_ops Pointer to TypeOperations for the event data type T
/// \param data_ptr Pointer to event data (T*)
/// \return true if send successful, false otherwise
bool mw_com_skeleton_send_event(SkeletonEventBase* event_ptr, const TypeOperations* type_ops, void* data_ptr)
{
    if (event_ptr == nullptr || type_ops == nullptr || data_ptr == nullptr)
    {
        return false;
    }

    return type_ops->SkeletonSendEvent(event_ptr, data_ptr);
}

/// \brief Subscribe to a proxy event to allocate sample buffers
/// \details Must be called before GetNewSamples to initialize the event's sample tracker.
/// \param event_ptr Opaque event pointer (ProxyEventBase*)
/// \param max_sample_count Maximum number of concurrent samples to allocate
/// \return true if subscription successful, false otherwise
bool mw_com_proxy_event_subscribe(ProxyEventBase* event_ptr, uint32_t max_sample_count)
{
    if (event_ptr == nullptr)
    {
        return false;
    }

    auto result = event_ptr->Subscribe(max_sample_count);

    return result.has_value();
}

/// \brief Unsubscribe from a proxy event to release sample buffers
/// \details Must be called only after no `SamplePtr` instances are held on the Rust side
/// \param event_ptr Opaque event pointer (ProxyEventBase*)
void mw_com_proxy_event_unsubscribe(ProxyEventBase* event_ptr)
{
    if (event_ptr == nullptr)
    {
        return;
    }
    event_ptr->Unsubscribe();
}

/// \brief Create proxy instance dynamically
/// \details Creates a proxy for the given interface UID using the provided handle.
/// \param interface_id UTF-8 string view of interface UID (e.g., "mw_com_IpcBridge")
/// \param handle_ptr Opaque handle identifying the service instance
/// \return Pointer to ProxyBase instance, or nullptr on failure
ProxyBase* mw_com_create_proxy(StringView interface_id, const HandleType& handle_ptr)
{
    if (interface_id.data == nullptr)
    {
        return nullptr;
    }
    auto id = static_cast<std::string_view>(interface_id);
    auto* registry = GlobalRegistryMapping::FindInterfaceRegistry(id);

    if (registry == nullptr)
    {
        return nullptr;
    }
    return registry->CreateProxy(handle_ptr);
}

/// \brief Create skeleton instance dynamically
/// \details Creates a skeleton for the given interface UID.
/// \param interface_id UTF-8 string view of interface UID
/// \param instance_spec Pointer to InstanceSpecifier identifying the service to offer
/// \return Pointer to SkeletonBase instance, or nullptr on failure
SkeletonBase* mw_com_create_skeleton(StringView interface_id, ::score::mw::com::InstanceSpecifier* instance_spec)
{
    if (interface_id.data == nullptr || instance_spec == nullptr)
    {
        return nullptr;
    }

    auto id = static_cast<std::string_view>(interface_id);
    auto* registry = GlobalRegistryMapping::FindInterfaceRegistry(id);

    if (registry == nullptr)
    {
        return nullptr;
    }

    return registry->CreateSkeleton(*instance_spec);
}

/// \brief Offer service for skeleton instance
/// \details Starts offering the service on the provided skeleton instance.
/// \param skeleton_ptr Opaque skeleton pointer
/// \return true if service is offered successfully, false otherwise
bool mw_com_skeleton_offer_service(SkeletonBase* skeleton_ptr)
{
    if (skeleton_ptr == nullptr)
    {
        return false;
    }

    bool result = skeleton_ptr->OfferService().has_value();
    return result;
}

/// \brief Stop offering service for skeleton instance
/// \details Stops offering the service on the provided skeleton instance.
/// \param skeleton_ptr Opaque skeleton pointer
void mw_com_skeleton_stop_offer_service(SkeletonBase* skeleton_ptr)
{
    if (skeleton_ptr == nullptr)
    {
        return;
    }
    skeleton_ptr->StopOfferService();
}

/// \brief Destroy proxy instance
/// \details Deallocates a proxy created with mw_com_create_proxy.
/// \param proxy_ptr Opaque proxy pointer to destroy
void mw_com_destroy_proxy(ProxyBase* proxy_ptr)
{
    if (proxy_ptr == nullptr)
    {
        return;
    }

    delete proxy_ptr;
    ;
}

/// \brief Destroy skeleton instance
/// \details Deallocates a skeleton created with mw_com_create_skeleton.
/// \param skeleton_ptr Opaque skeleton pointer to destroy
void mw_com_destroy_skeleton(SkeletonBase* skeleton_ptr)
{
    if (skeleton_ptr == nullptr)
    {
        return;
    }
    delete skeleton_ptr;
}

/// \brief Get samples from proxy event of specific type
/// \details Retrieves new samples from a proxy event using the type operations registry.
/// \param event_ptr Opaque proxy event pointer (ProxyEventBase*)
/// \param type_ops Pointer to TypeOperations for the event data type T
/// \param callback Pointer to FatPtr callback for sample processing
/// \param max_samples Maximum number of samples to retrieve
/// \return Number of samples retrieved, or std::numeric_limits<std::uint32_t>::max() on error
std::uint32_t mw_com_type_registry_get_samples_from_event(ProxyEventBase* event_ptr,
                                                          const TypeOperations* type_ops,
                                                          const FatPtr* callback,
                                                          uint32_t max_samples)
{
    if (event_ptr == nullptr || type_ops == nullptr || callback == nullptr)
    {
        return std::numeric_limits<std::uint32_t>::max();
    }

    auto result = type_ops->GetSamplesFromEvent(event_ptr, max_samples, *callback);

    if (!result.has_value())
    {
        return std::numeric_limits<std::uint32_t>::max();
    }

    return result.value();
}

/// @brief Get sample data pointer from SamplePtr<T>
/// @param sample_ptr Opaque sample pointer
/// @param type_ops Type operations pointer
/// @return Pointer to sample data, or nullptr if type mismatch
const void* mw_com_get_sample_ptr(const void* sample_ptr, const TypeOperations* type_ops)
{
    if (sample_ptr == nullptr || type_ops == nullptr)
    {
        return nullptr;
    }

    return type_ops->GetSamplePtrData(sample_ptr);
}

/// @brief Delete sample pointer of specific type
/// @param sample_ptr Opaque sample pointer
/// @param type_ops Type operations pointer
void mw_com_delete_sample_ptr(void* sample_ptr, const TypeOperations* type_ops)
{
    if (sample_ptr == nullptr || type_ops == nullptr)
    {
        return;
    }

    type_ops->DeleteSamplePtr(sample_ptr);
}

/// @brief Get allocatee pointer from skeleton event of specific type
/// @param event_ptr Opaque skeleton event pointer
/// @param allocatee_ptr Pointer to pre-allocated memory for allocatee
/// @param type_ops Type operations pointer
/// @return True if allocatee pointer was retrieved successfully, false otherwise
bool mw_com_get_allocatee_ptr(SkeletonEventBase* event_ptr, void* allocatee_ptr, const TypeOperations* type_ops)
{
    if (event_ptr == nullptr || type_ops == nullptr)
    {
        return false;
    }

    return type_ops->GetAllocateePtr(event_ptr, allocatee_ptr);
}

/// @brief Delete allocatee pointer of specific type
/// @param allocatee_ptr Pointer to SampleAllocateePtr<T>
/// @param type_ops Type operations pointer
void mw_com_delete_allocatee_ptr(void* allocatee_ptr, const TypeOperations* type_ops)
{
    if (allocatee_ptr == nullptr || type_ops == nullptr)
    {
        return;
    }

    type_ops->DeleteAllocateePtr(allocatee_ptr);
}

/// @brief Get allocatee data pointer from allocatee of specific type
/// @param allocatee_ptr Pointer to SampleAllocateePtr<T>
/// @param type_ops Type operations pointer
/// @return Pointer to allocatee data, or nullptr if type mismatch
void* mw_com_get_allocatee_data_ptr(void* allocatee_ptr, const TypeOperations* type_ops)
{
    if (allocatee_ptr == nullptr || type_ops == nullptr)
    {
        return nullptr;
    }

    return type_ops->GetAllocateeDataPtr(allocatee_ptr);
}

/// @brief  Send event via skeleton using allocatee pointer of specific type
/// @param event_ptr Opaque skeleton event pointer
/// @param type_ops Type operations pointer
/// @param allocatee_ptr Pointer to SampleAllocateePtr<T>
/// @return True if event was sent successfully, false otherwise
bool mw_com_skeleton_send_event_allocatee(SkeletonEventBase* event_ptr,
                                          const TypeOperations* type_ops,
                                          void* allocatee_ptr)
{
    if (event_ptr == nullptr || type_ops == nullptr || allocatee_ptr == nullptr)
    {
        return false;
    }

    return type_ops->SkeletonSendEventAllocatee(event_ptr, allocatee_ptr);
}

/// \brief Set event receive handler for proxy event
/// \details Registers a Rust FnMut handler for a proxy event. The handler will be called when new samples are received.
/// \param event_ptr Opaque proxy event pointer (ProxyEventBase*)
/// \param boxed_handler Pointer to FatPtr containing the Rust FnMut handler
/// @return True if handler was set successfully, false otherwise
bool mw_com_proxy_set_event_receive_handler(ProxyEventBase* event_ptr, const FatPtr* boxed_handler)
{
    if (event_ptr == nullptr || boxed_handler == nullptr)
    {
        return false;
    }

    auto result = event_ptr->SetReceiveHandler(RustFnMutCallable<RustBoxedCallable>{*boxed_handler});
    return result.has_value();
}

/// \brief Clear event receive handler for proxy event
/// \details Unregisters the event receive handler for a proxy event, if any.
/// \param event_ptr Opaque proxy event pointer (ProxyEventBase*)
void mw_com_proxy_clear_event_receive_handler(ProxyEventBase* event_ptr)
{
    if (event_ptr == nullptr)
    {
        return;
    }
    score::cpp::ignore = event_ptr->UnsetReceiveHandler();
}

/// \brief Get the current subscription state of a proxy event
/// \param event_ptr Opaque proxy event pointer (ProxyEventBase*)
/// \return Raw SubscriptionState enumeration value; kNotSubscribed for a null pointer
std::uint8_t mw_com_proxy_event_get_subscription_state(ProxyEventBase* event_ptr)
{
    if (event_ptr == nullptr)
    {
        return static_cast<std::uint8_t>(SubscriptionState::kNotSubscribed);
    }
    return static_cast<std::uint8_t>(event_ptr->GetSubscriptionState());
}

/// \brief Register a subscription state change handler for a proxy event
/// \param event_ptr Opaque proxy event pointer (ProxyEventBase*)
/// \param boxed_handler Pointer to FatPtr containing the Rust FnMut(u8) -> bool handler
/// \return true if the handler was registered, false otherwise
bool mw_com_proxy_event_set_subscription_state_change_handler(ProxyEventBase* event_ptr, const FatPtr* boxed_handler)
{
    if (event_ptr == nullptr || boxed_handler == nullptr)
    {
        return false;
    }

    // Keep ownership with Rust until the native registration succeeds. The binding
    // may destroy a rejected handler before returning an error; disposing the box
    // there would make the Rust failure cleanup a double free. The local shared
    // reference also keeps the state alive if a synchronous callback returns false.
    auto ownership = std::make_shared<SubscriptionStateHandlerOwnership>(*boxed_handler);
    auto result = event_ptr->SetSubscriptionStateChangeHandler([ownership](SubscriptionState state) noexcept {
        return RustBoxedCallable<bool, SubscriptionState>::invoke(ownership->pointer, state);
    });
    ownership->transferred = result.has_value();
    return result.has_value();
}

/// \brief Unregister the subscription state change handler of a proxy event
/// \param event_ptr Opaque proxy event pointer (ProxyEventBase*)
/// \return true if the handler was unregistered, false otherwise
bool mw_com_proxy_event_unset_subscription_state_change_handler(ProxyEventBase* event_ptr)
{
    if (event_ptr == nullptr)
    {
        return false;
    }
    auto result = event_ptr->UnsetSubscriptionStateChangeHandler();
    return result.has_value();
}

/// \brief Start asynchronous service discovery with a callback
/// \details Initiates a service discovery operation using a Rust callback. The callback will be invoked
/// when matching services are found. The callback signature is:
/// void(ServiceHandleContainer<HandleType>, FindServiceHandle)
///
/// The callback can be invoked:
/// - Synchronously: if matching services already exist when StartFindService is called
/// - Asynchronously: if new services become available after the search starts (called from worker thread)
///
/// \param callback FatPtr to Rust FnMut closure that matches the FindServiceHandler signature
/// \param instance_spec Pointer to InstanceSpecifier for service discovery criteria
/// \return Opaque pointer to FindServiceHandle on success, nullptr on failure
/// \note The FindServiceHandle returned is passed to the callback to allow StopFindService calls
void* mw_com_start_find_service(const FatPtr* callback, InstanceSpecifier* instance_spec)
{
    if (callback == nullptr || instance_spec == nullptr)
    {
        return nullptr;
    }

    // Create a RustFnMutCallable with RustBoxedCallable handler
    // Callback signature: void(ServiceHandleContainer<HandleType>, FindServiceHandle)
    RustFnMutCallable<RustBoxedCallable, void, ServiceHandleContainer<HandleType>, FindServiceHandle> rust_callable{
        *callback};

    if (auto result = ::score::mw::com::impl::Runtime::getInstance().GetServiceDiscovery().StartFindService(
            std::move(rust_callable), std::move(*instance_spec));
        result.has_value())
    {
        return new FindServiceHandle{std::move(result).value()};
    }
    else
    {
        return nullptr;
    }
}

/// \brief Start Specific discovery and transfer the boxed Rust callback on success
/// \details The original mw_com_start_find_service symbol retains its baseline ownership
/// semantics. This additive entry point releases an accepted callback when native discovery
/// relinquishes it; a rejected registration leaves ownership with the Rust caller.
void* mw_com_start_find_service_owned(const FatPtr* callback, InstanceSpecifier* instance_spec)
{
    if (callback == nullptr || instance_spec == nullptr)
    {
        return nullptr;
    }

    auto ownership = std::make_shared<DiscoveryCallbackOwnership>(*callback);
    auto result = Runtime::getInstance().GetServiceDiscovery().StartFindService(
        [ownership](ServiceHandleContainer<HandleType> handles, FindServiceHandle handle) noexcept {
            RustBoxedCallable<void, ServiceHandleContainer<HandleType>, FindServiceHandle>::invoke(
                ownership->pointer, std::move(handles), handle);
        },
        std::move(*instance_spec));
    ownership->transferred = result.has_value();
    if (result.has_value())
    {
        return new FindServiceHandle{std::move(result).value()};
    }
    return nullptr;
}

/// \brief Stop an ongoing service discovery operation and delete the handle
/// \details Stops the service discovery operation associated with the provided FindServiceHandle
/// and deallocates the handle. This is the only place where the handle should be deleted.
/// \param find_service_handle_ptr Opaque pointer to FindServiceHandle returned by mw_com_start_find_service
void mw_com_stop_find_service(void* find_service_handle_ptr)
{
    if (find_service_handle_ptr == nullptr)
    {
        return;
    }

    auto* find_service_handle = static_cast<FindServiceHandle*>(find_service_handle_ptr);

    // Stop the service discovery
    auto result =
        ::score::mw::com::impl::Runtime::getInstance().GetServiceDiscovery().StopFindService(*find_service_handle);

    if (!result.has_value())
    {
        mw::log::LogError("com-api") << "Failed to stop service discovery for handle: " << result.error();
    }

    delete find_service_handle;
}

/// \brief Get type operations instance for a given interface and member id
/// \details Retrieves a pointer to the TypeOperations instance associated with the specified interface ID and member id
/// (e.g., event name). This allows Rust code to perform type-specific operations for events without using the
/// registry-based approach.
/// \param interface_id UTF-8 string view of interface ID
/// \param member_name UTF-8 string view of member name (e.g., event name)
/// \return Const pointer to TypeOperations instance if found, nullptr otherwise
const void* mw_com_get_type_ops_instance(StringView interface_id, StringView member_name)
{
    if (interface_id.data == nullptr || member_name.data == nullptr)
    {
        return nullptr;
    }

    auto id = static_cast<std::string_view>(interface_id);
    auto member = static_cast<std::string_view>(member_name);

    auto* registry = GlobalRegistryMapping::FindMemberOperation(id, member);

    if (registry == nullptr)
    {
        return nullptr;
    }

    return registry->GetTypeOps();
}

/// \brief Create an InstanceSpecifier from a UTF-8 string
/// \details Allocates and returns a new InstanceSpecifier based on the provided UTF-8 string
/// \param instance_specifier UTF-8 string representing the instance specifier
/// \param instance_specifier_length Length of the UTF-8 string
/// \return Pointer to newly allocated InstanceSpecifier, or nullptr on failure
::score::mw::com::InstanceSpecifier* mw_com_impl_instance_specifier_create(
    const char* const instance_specifier,
    const std::uint32_t instance_specifier_length) noexcept
{
    if (auto result =
            ::score::mw::com::InstanceSpecifier::Create(std::string{instance_specifier, instance_specifier_length});
        result.has_value())
    {
        return new ::score::mw::com::InstanceSpecifier{std::move(result).value()};
    }
    else
    {
        return nullptr;
    }
}

/// \brief Clone an existing InstanceSpecifier
/// \details Allocates and returns a new InstanceSpecifier that is a copy of the provided one
/// \param instance_specifier Reference to the existing InstanceSpecifier to clone
/// \return Pointer to newly allocated InstanceSpecifier, or nullptr on failure
::score::mw::com::InstanceSpecifier* mw_com_impl_instance_specifier_clone(
    const ::score::mw::com::InstanceSpecifier& instance_specifier) noexcept
{
    return new ::score::mw::com::InstanceSpecifier{instance_specifier};
}

void mw_com_impl_instance_specifier_delete(::score::mw::com::InstanceSpecifier* instance_specifier) noexcept
{
    delete instance_specifier;
}

/// \brief Find services matching an InstanceSpecifier
/// \details Performs service discovery for services matching the provided InstanceSpecifier.
/// \param instance_specifier Pointer to InstanceSpecifier specifying the service criteria
/// \return Pointer to ServiceHandleContainer containing matching handles, or nullptr if none found
::score::mw::com::ServiceHandleContainer<::score::mw::com::impl::HandleType>* mw_com_impl_find_service(
    ::score::mw::com::InstanceSpecifier* instance_specifier) noexcept
{
    if (auto result = ::score::mw::com::impl::Runtime::getInstance().GetServiceDiscovery().FindService(
            std::move(*instance_specifier));
        result.has_value())
    {
        return new ::score::mw::com::ServiceHandleContainer<::score::mw::com::impl::HandleType>{
            std::move(result).value()};
    }
    else
    {
        return nullptr;
    }
}

/// \brief Find all currently offered instances of an interface (typed find-any path)
/// \details Resolves the interface registry UID to its explicitly registered find-any selector and
/// validates (through `IRuntime::resolve`) that it maps to exactly one supported LoLa
/// `InstanceIdentifier` whose instance id is unset. Only such a genuine wildcard identifier is
/// delegated to the existing typed native FindService path. Returns nullptr when the interface is
/// unknown, has no find-any registration, the selector is malformed or not part of the loaded
/// configuration, resolves to a concrete instance id or an unsupported binding, is ambiguous, or
/// the native search fails. It never terminates for an unmapped interface and never silently
/// returns Specific results for a misconfigured concrete selector.
/// \param interface_id UTF-8 string view of the interface registry UID
/// \return Pointer to ServiceHandleContainer containing matching handles, or nullptr
::score::mw::com::ServiceHandleContainer<::score::mw::com::impl::HandleType>* mw_com_impl_find_service_any(
    StringView interface_id) noexcept
{
    if (interface_id.data == nullptr)
    {
        return nullptr;
    }

    auto id = static_cast<std::string_view>(interface_id);
    auto instance_identifier = ResolveFindAnyIdentifier(id);
    if (!instance_identifier.has_value())
    {
        return nullptr;
    }

    if (auto result = ::score::mw::com::impl::Runtime::getInstance().GetServiceDiscovery().FindService(
            std::move(instance_identifier).value());
        result.has_value())
    {
        return new ::score::mw::com::ServiceHandleContainer<::score::mw::com::impl::HandleType>{
            std::move(result).value()};
    }
    else
    {
        return nullptr;
    }
}

/// \brief Start asynchronous typed find-any discovery with a callback
/// \details Resolves the interface registry UID to its explicitly registered find-any selector,
/// validates that it maps to exactly one supported LoLa wildcard `InstanceIdentifier` (instance id
/// unset), and only then delegates to the existing typed native StartFindService path. The callback
/// signature is void(ServiceHandleContainer<HandleType>, FindServiceHandle). Returns nullptr when
/// the interface is unknown, has no find-any registration, the selector is malformed or unmapped,
/// resolves to a concrete instance id or an unsupported binding, is ambiguous, or the search
/// cannot be started.
/// \param callback FatPtr to Rust FnMut closure matching the FindServiceHandler signature
/// \param interface_id UTF-8 string view of the interface registry UID
/// \return Opaque pointer to FindServiceHandle on success, nullptr on failure
void* mw_com_start_find_service_any(const FatPtr* callback, StringView interface_id)
{
    if (callback == nullptr || interface_id.data == nullptr)
    {
        return nullptr;
    }

    auto id = static_cast<std::string_view>(interface_id);
    auto instance_identifier = ResolveFindAnyIdentifier(id);
    if (!instance_identifier.has_value())
    {
        return nullptr;
    }

    auto ownership = std::make_shared<DiscoveryCallbackOwnership>(*callback);
    auto result = Runtime::getInstance().GetServiceDiscovery().StartFindService(
        [ownership](ServiceHandleContainer<HandleType> handles, FindServiceHandle handle) noexcept {
            RustBoxedCallable<void, ServiceHandleContainer<HandleType>, FindServiceHandle>::invoke(
                ownership->pointer, std::move(handles), handle);
        },
        std::move(instance_identifier).value());
    ownership->transferred = result.has_value();
    if (result.has_value())
    {
        return new FindServiceHandle{std::move(result).value()};
    }
    return nullptr;
}

/// \brief Delete a ServiceHandleContainer
/// \param container Pointer to the ServiceHandleContainer to delete
void mw_com_impl_handle_container_delete(
    ::score::mw::com::ServiceHandleContainer<::score::mw::com::impl::HandleType>* container) noexcept
{
    delete container;
}

/// \brief Get the size of a ServiceHandleContainer
/// \param container Pointer to the ServiceHandleContainer
/// \return Number of elements in the container
std::uint32_t mw_com_impl_handle_container_get_size(
    const ::score::mw::com::ServiceHandleContainer<::score::mw::com::impl::HandleType>* container)
{
    return static_cast<std::uint32_t>(container->size());
}

/// \brief Get a handle at a specific position in a ServiceHandleContainer
/// \param container Pointer to the ServiceHandleContainer
/// \param pos Index of the handle to retrieve
/// \return Pointer to the handle at the specified position, or nullptr if out of bounds
const ::score::mw::com::impl::HandleType* mw_com_impl_handle_container_get_handle_at(
    const ::score::mw::com::ServiceHandleContainer<::score::mw::com::impl::HandleType>* container,
    std::uint32_t pos) noexcept
{
    return &container->at(pos);
}

/// \brief Initialize the runtime
/// \param argv Array of command-line arguments
/// \param argc Number of command-line arguments
void mw_com_impl_initialize(const char* argv[], std::int32_t argc)
{
    ::score::mw::com::runtime::InitializeRuntime(score::string_manipulation::GetArguments(argc, argv));
}

/// \brief Get the size of a SamplePtr
/// \return Size of the SamplePtr type in bytes
std::uint32_t mw_com_impl_sample_ptr_get_size() noexcept
{
    return sizeof(::score::mw::com::impl::SamplePtr<std::uint32_t>);
}

/// \brief Enumerate the configured LoLa service types as a bounded discovery universe.
/// \details Enumerates types with a configured LoLa instance deployment at this call, using the selected
///          deployment's quality level (see Runtime::GetConfiguredServiceWildcardIdentifiers()). Merge add-on
///          configurations before opening a stream to include added types. Type declarations without such a
///          deployment, other bindings and unconfigured interface types are outside this universe.
/// \return Owned, heap-allocated list of identities; never nullptr (empty list on empty configuration).
NativeServiceTypeList* mw_com_impl_enumerate_service_types() noexcept
{
    auto* list = new NativeServiceTypeList{};
    const auto identifiers = Runtime::GetConfiguredServiceWildcardIdentifiers();
    list->entries.reserve(identifiers.size());
    for (const auto& identifier : identifiers)
    {
        const auto& instance_deployment = InstanceIdentifierView{identifier}.GetServiceInstanceDeployment();
        const ServiceIdentifierTypeView type_view{instance_deployment.service_};
        const ServiceVersionType version = type_view.GetVersion();
        const ServiceVersionTypeView version_view{version};
        std::uint32_t service_id = 0;
        const auto& type_deployment = InstanceIdentifierView{identifier}.GetServiceTypeDeployment();
        if (const auto* lola_type = std::get_if<LolaServiceTypeDeployment>(&type_deployment.binding_info_))
        {
            service_id = static_cast<std::uint32_t>(lola_type->service_id_);
        }
        list->entries.push_back(
            NativeServiceTypeList::Entry{std::string{type_view.getInternalTypeName()},
                                         version_view.getMajor(),
                                         version_view.getMinor(),
                                         static_cast<std::uint32_t>(instance_deployment.GetBindingType()),
                                         service_id});
    }
    return list;
}

/// \brief Delete a service type list returned by mw_com_impl_enumerate_service_types.
void mw_com_impl_service_type_list_delete(NativeServiceTypeList* list) noexcept
{
    delete list;
}

/// \brief Number of identities in a service type list.
std::uint32_t mw_com_impl_service_type_list_get_size(const NativeServiceTypeList* list) noexcept
{
    if (list == nullptr)
    {
        return 0U;
    }
    return static_cast<std::uint32_t>(list->entries.size());
}

/// \brief Copy the identity fields at \p pos out of a service type list.
/// \details The returned name pointer references storage owned by the list and is only valid while the list is alive.
void mw_com_impl_service_type_list_get(const NativeServiceTypeList* list,
                                       std::uint32_t pos,
                                       const char** name,
                                       std::uint32_t* name_len,
                                       std::uint32_t* major,
                                       std::uint32_t* minor,
                                       std::uint32_t* binding,
                                       std::uint32_t* service_id) noexcept
{
    if ((list == nullptr) || (pos >= list->entries.size()))
    {
        return;
    }
    const auto& entry = list->entries[pos];
    if (name != nullptr)
    {
        *name = entry.name.data();
    }
    if (name_len != nullptr)
    {
        *name_len = static_cast<std::uint32_t>(entry.name.size());
    }
    if (major != nullptr)
    {
        *major = entry.major;
    }
    if (minor != nullptr)
    {
        *minor = entry.minor;
    }
    if (binding != nullptr)
    {
        *binding = entry.binding;
    }
    if (service_id != nullptr)
    {
        *service_id = entry.service_id;
    }
}

/// \brief Start one wildcard (FindAny) discovery watch for a configured service type.
/// \details The watch is identified by the full service type identity (name + version). It is backed by the
///          runtime-owned wildcard deployment (instance id removed), so the native callback reports every offered
///          provider instance of that type, including provider instances whose concrete instance id is absent from
///          the consumer configuration.
/// \return Opaque FindServiceHandle pointer, or nullptr when the type is not configured or start fails.
void* mw_com_impl_start_find_service_any(const char* service_type_name,
                                         std::uint32_t service_type_name_length,
                                         std::uint32_t major,
                                         std::uint32_t minor,
                                         const FatPtr* callback) noexcept
{
    if ((callback == nullptr) || (service_type_name == nullptr))
    {
        return nullptr;
    }
    const std::string_view requested_name{service_type_name, service_type_name_length};
    auto identifiers = Runtime::GetConfiguredServiceWildcardIdentifiers();
    InstanceIdentifier* matching_identifier = nullptr;
    for (auto& identifier : identifiers)
    {
        const auto& instance_deployment = InstanceIdentifierView{identifier}.GetServiceInstanceDeployment();
        const ServiceIdentifierTypeView type_view{instance_deployment.service_};
        const ServiceVersionType version = type_view.GetVersion();
        const ServiceVersionTypeView version_view{version};
        if ((type_view.getInternalTypeName() == requested_name) && (version_view.getMajor() == major) &&
            (version_view.getMinor() == minor))
        {
            matching_identifier = &identifier;
            break;
        }
    }
    if (matching_identifier == nullptr)
    {
        return nullptr;
    }

    auto ownership = std::make_shared<DiscoveryCallbackOwnership>(*callback);
    auto result = Runtime::getInstance().GetServiceDiscovery().StartFindService(
        [ownership](ServiceHandleContainer<HandleType> handles, FindServiceHandle handle) noexcept {
            RustBoxedCallable<void, ServiceHandleContainer<HandleType>, FindServiceHandle>::invoke(
                ownership->pointer, std::move(handles), handle);
        },
        std::move(*matching_identifier));
    ownership->transferred = result.has_value();
    if (result.has_value())
    {
        return new FindServiceHandle{std::move(result).value()};
    }
    return nullptr;
}

/// \brief Extract the full observed service identity from a discovered native handle.
/// \details Identity is observed from the handle's InstanceIdentifier (configured type name + version + binding and
///          binding service id) and from HandleType::GetInstanceId() (the concrete provider instance id). No
///          InstanceSpecifier is fabricated. Quality is intentionally not part of the reported identity because the
///          native HandleType does not carry provider quality; watch selection uses the configured instance's ASIL
///          level (documented limitation).
void mw_com_impl_handle_get_identity(const HandleType* handle,
                                     const char** service_type_name,
                                     std::uint32_t* service_type_name_length,
                                     std::uint32_t* major,
                                     std::uint32_t* minor,
                                     std::uint32_t* binding,
                                     std::uint32_t* service_id,
                                     std::uint32_t* instance_id) noexcept
{
    if (handle == nullptr)
    {
        return;
    }
    const auto& instance_deployment =
        InstanceIdentifierView{handle->GetInstanceIdentifier()}.GetServiceInstanceDeployment();
    const ServiceIdentifierTypeView type_view{instance_deployment.service_};
    const ServiceVersionType version = type_view.GetVersion();
    const ServiceVersionTypeView version_view{version};
    const auto type_name = type_view.getInternalTypeName();
    if (service_type_name != nullptr)
    {
        *service_type_name = type_name.data();
    }
    if (service_type_name_length != nullptr)
    {
        *service_type_name_length = static_cast<std::uint32_t>(type_name.size());
    }
    if (major != nullptr)
    {
        *major = version_view.getMajor();
    }
    if (minor != nullptr)
    {
        *minor = version_view.getMinor();
    }
    if (binding != nullptr)
    {
        *binding = static_cast<std::uint32_t>(instance_deployment.GetBindingType());
    }

    std::uint32_t extracted_service_id = 0;
    const auto& type_deployment = handle->GetServiceTypeDeployment();
    if (const auto* lola_type = std::get_if<LolaServiceTypeDeployment>(&type_deployment.binding_info_))
    {
        extracted_service_id = static_cast<std::uint32_t>(lola_type->service_id_);
    }
    if (service_id != nullptr)
    {
        *service_id = extracted_service_id;
    }

    std::uint32_t extracted_instance_id = 0;
    const auto& deployment_instance_id = handle->GetInstanceId();
    if (const auto* lola_instance_id = std::get_if<LolaServiceInstanceId>(&deployment_instance_id.binding_info_))
    {
        extracted_instance_id = static_cast<std::uint32_t>(lola_instance_id->GetId());
    }
    if (instance_id != nullptr)
    {
        *instance_id = extracted_instance_id;
    }
}

}  // extern "C"
}  // namespace score::mw::com::impl::rust
