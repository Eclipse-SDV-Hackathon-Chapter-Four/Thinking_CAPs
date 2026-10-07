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

//! Continuous, heterogeneous service-availability stream for the LoLa backend.
//!
//! The stream is bounded to the configured LoLa universe: it opens one wildcard (FindAny) discovery watch per service
//! type present in the loaded native configuration. Each watch reports the complete set of currently offered provider
//! instances of that type, including provider instances whose concrete instance id is absent from the consumer's
//! configuration. Availability items are emitted the first time a full identity (service type name, version, binding,
//! binding service id and concrete instance id) becomes visible across all watches, and again after that identity was
//! withdrawn everywhere and is later re-offered.
//!
//! # Ownership and termination limitations
//! * The native find-service callback box handed to native discovery is not reclaimed: the inherited find-service
//!   callable has an empty dispose hook, so each opened stream leaks its callback closure (and with it, the `Arc` to
//!   the stream state). This is a bounded, honest limitation; no Box/`Arc` reclamation or callback quiescence is
//!   claimed. Dropping the stream still stops every native watch, so no callback is expected to fire afterwards.
//! * The per-callback allocations (queue, membership maps) are bounded by the configured universe and by the number of
//!   currently offered instances. No running-phase capacity policy is proven for a changing universe.

use core::pin::Pin;
use core::task::{Context, Poll};
use std::collections::{hash_map::Entry as HashMapEntry, HashMap, HashSet, VecDeque};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};

use futures::stream::Stream;
use futures::task::AtomicWaker;

use bridge_ffi_rs::{
    FFIBridge, FindServiceCallable, FindServiceHandle, HandleContainer, NativeFindServiceHandle,
    NativeServiceIdentity,
};
use score_com_concept::{Error, Result, ServiceDescriptor, ServiceFailedReason, ServiceVersion};

/// Native binding tag of the LoLa shared-memory binding (`BindingType::kLoLa`).
const BINDING_LOLA: u32 = 0;

fn binding_name(binding: u32) -> String {
    if binding == BINDING_LOLA {
        "lola".to_string()
    } else {
        format!("binding_{binding}")
    }
}

/// Full identity used for availability deduplication.
///
/// Two services that share a numeric instance id but differ in interface name, version or binding stay distinct.
#[derive(Clone, Debug, PartialEq, Eq, Hash)]
struct IdentityKey {
    name: String,
    major: u32,
    minor: u32,
    binding: u32,
    service_id: u32,
    instance_id: u32,
}

impl IdentityKey {
    fn from_identity(identity: &NativeServiceIdentity) -> Self {
        Self {
            name: identity.name.clone(),
            major: identity.major,
            minor: identity.minor,
            binding: identity.binding,
            service_id: identity.service_id,
            instance_id: identity.instance_id,
        }
    }
}

fn descriptor_from_identity(identity: &NativeServiceIdentity) -> ServiceDescriptor {
    ServiceDescriptor::new(
        identity.name.clone(),
        ServiceVersion::new(identity.major, identity.minor),
        binding_name(identity.binding),
        identity.service_id,
        identity.instance_id,
    )
}

/// Per-watch current membership plus global refcounts, so overlapping watches do not emit the same service twice.
#[derive(Default)]
struct MembershipState {
    per_watch: HashMap<u32, HashSet<IdentityKey>>,
    refcount: HashMap<IdentityKey, u32>,
}

/// Owns one started native watch. Kept next to the bridge so it can be stopped after the runtime borrow ends.
struct WatchHandle<B: FFIBridge> {
    handle: NativeFindServiceHandle,
    bridge: B,
}

/// Shared state between the returned stream and the native discovery callbacks.
struct StreamState<B: FFIBridge> {
    queue: Mutex<VecDeque<Result<ServiceDescriptor>>>,
    members: Mutex<MembershipState>,
    watches: Mutex<Vec<WatchHandle<B>>>,
    waker: AtomicWaker,
    finished: AtomicBool,
}

/// Owned, `Send` stream of newly available services across configured LoLa interfaces.
pub struct LolaAllServicesStream<B: FFIBridge> {
    state: Arc<StreamState<B>>,
}

fn new_stream_state<B: FFIBridge>() -> Arc<StreamState<B>> {
    Arc::new(StreamState {
        queue: Mutex::new(VecDeque::new()),
        members: Mutex::new(MembershipState::default()),
        watches: Mutex::new(Vec::new()),
        waker: AtomicWaker::new(),
        finished: AtomicBool::new(false),
    })
}

/// Apply one complete per-watch snapshot of observed identities.
///
/// The diff against the watch's previous membership drives both withdrawal and re-offer handling: a removed identity
/// decrements its global refcount (and is forgotten once it reaches zero), while an identity that transitions from a
/// global refcount of zero to one becomes a newly available item.
fn apply_snapshot<B: FFIBridge>(state: &Arc<StreamState<B>>, watch_slot: u32, identities: &[NativeServiceIdentity]) {
    let mut current: HashSet<IdentityKey> = HashSet::with_capacity(identities.len());
    let mut descriptors: HashMap<IdentityKey, ServiceDescriptor> = HashMap::with_capacity(identities.len());
    for identity in identities {
        if identity.name.is_empty() {
            continue;
        }
        let key = IdentityKey::from_identity(identity);
        current.insert(key.clone());
        descriptors.entry(key).or_insert_with(|| descriptor_from_identity(identity));
    }

    let newly_available = {
        let mut members = state.members.lock().expect("stream membership poisoned");
        let previous = members.per_watch.insert(watch_slot, current.clone()).unwrap_or_default();

        for removed in previous.difference(&current) {
            if let HashMapEntry::Occupied(mut entry) = members.refcount.entry(removed.clone()) {
                let value = entry.get_mut();
                *value = value.saturating_sub(1);
                if *value == 0 {
                    entry.remove();
                }
            }
        }

        let mut newly_available: Vec<IdentityKey> = Vec::new();
        for added in current.difference(&previous) {
            let entry = members.refcount.entry(added.clone()).or_insert(0);
            if *entry == 0 {
                newly_available.push(added.clone());
            }
            *entry += 1;
        }
        newly_available
    };

    if !newly_available.is_empty() {
        let mut queue = state.queue.lock().expect("stream queue poisoned");
        for key in &newly_available {
            if let Some(descriptor) = descriptors.remove(key) {
                queue.push_back(Ok(descriptor));
            }
        }
        drop(queue);
        state.waker.wake();
    }
}

/// Convert a native callback container into owned identities.
fn collect_identities<B: FFIBridge>(bridge: &B, handles: &HandleContainer) -> Vec<NativeServiceIdentity> {
    let mut identities = Vec::with_capacity(handles.len());
    for index in 0..handles.len() {
        if let Some(handle) = handles.get(index) {
            // SAFETY: handles inside a native discovery callback container stay valid for the duration of the
            // callback; we copy the identity out immediately.
            let identity = unsafe { bridge.handle_identity(handle) };
            identities.push(identity);
        }
    }
    identities
}

/// Build the configured-universe stream. Shared state and callback ownership are established before the first native
/// watch is started, so a callback that fires synchronously during start is handled and never dropped.
pub fn build_all_services_stream<B: FFIBridge>(bridge: &B) -> Result<LolaAllServicesStream<B>> {
    let state = new_stream_state::<B>();
    let service_types = bridge.enumerate_service_types();
    let mut started: Vec<WatchHandle<B>> = Vec::with_capacity(service_types.len());

    for (slot, service_type) in service_types.iter().enumerate() {
        let callback_state = Arc::clone(&state);
        let callback_bridge = bridge.clone();
        // The callback only enqueues/diffs collected identities; it never touches `watches`, so it is safe for it to
        // fire synchronously before this iteration stores its own handle.
        let callback = Box::new(move |handles: HandleContainer, _handle: NativeFindServiceHandle| {
            let identities = collect_identities(&callback_bridge, &handles);
            apply_snapshot(&callback_state, slot as u32, &identities);
        });
        let dyn_callback: Box<dyn FnMut(HandleContainer, NativeFindServiceHandle) + Send + 'static> = callback;
        // SAFETY: `dyn_callback` is a `FnMut(HandleContainer, NativeFindServiceHandle)`, exactly the find-service
        // callback contract, and its `FatPtr` is passed to native discovery.
        let callable = unsafe { FindServiceCallable::new(std::mem::transmute(dyn_callback)) };

        let raw_handle = bridge.start_find_service_any(
            &service_type.name,
            service_type.major,
            service_type.minor,
            &callable,
        );
        if raw_handle.is_null() {
            // Partial start failure: stop every watch that was already started, in reverse order, before returning.
            for mut watch in started.drain(..).rev() {
                // SAFETY: this handle was returned by start_find_service_any and has not been stopped yet.
                unsafe { watch.bridge.stop_find_service(watch.handle.as_mut() as *mut FindServiceHandle) };
            }
            return Err(Error::ServiceError(ServiceFailedReason::FailedToStartDiscovery));
        }
        started.push(WatchHandle {
            handle: NativeFindServiceHandle::new(raw_handle),
            bridge: bridge.clone(),
        });
    }

    // Publish ownership guards before the stream is returned and possibly dropped without ever being polled.
    {
        let mut watches = state.watches.lock().expect("stream watches poisoned");
        *watches = started;
    }

    Ok(LolaAllServicesStream { state })
}

impl<B: FFIBridge> Stream for LolaAllServicesStream<B> {
    type Item = Result<ServiceDescriptor>;

    fn poll_next(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        {
            let mut queue = self.state.queue.lock().expect("stream queue poisoned");
            if let Some(item) = queue.pop_front() {
                return Poll::Ready(Some(item));
            }
        }

        if self.state.finished.load(Ordering::Acquire) {
            return Poll::Ready(None);
        }

        // Register before re-checking so a concurrent callback cannot slip in between the check and the registration.
        self.state.waker.register(cx.waker());
        let mut queue = self.state.queue.lock().expect("stream queue poisoned");
        if let Some(item) = queue.pop_front() {
            return Poll::Ready(Some(item));
        }
        Poll::Pending
    }
}

impl<B: FFIBridge> Drop for LolaAllServicesStream<B> {
    fn drop(&mut self) {
        self.state.finished.store(true, Ordering::Release);
        // Take the watches out under the watches lock, then stop them without holding the callback state mutex, so a
        // native stop that waits for an in-flight callback cannot deadlock against that callback's membership lock.
        let watches = {
            let mut guard = self.state.watches.lock().expect("stream watches poisoned");
            std::mem::take(&mut *guard)
        };
        for mut watch in watches {
            // SAFETY: this handle was returned by start_find_service_any and has not been stopped yet.
            unsafe { watch.bridge.stop_find_service(watch.handle.as_mut() as *mut FindServiceHandle) };
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use bridge_ffi_mock::{MockFFIBridge, MockPointerAllocator, SharedMockBridge};
    use bridge_ffi_rs::NativeServiceType;
    use std::sync::atomic::AtomicUsize;

    fn identity(name: &str, instance_id: u32) -> NativeServiceIdentity {
        NativeServiceIdentity {
            name: name.to_string(),
            major: 1,
            minor: 0,
            binding: BINDING_LOLA,
            service_id: 42,
            instance_id,
        }
    }

    fn service_type(name: &str) -> NativeServiceType {
        NativeServiceType {
            name: name.to_string(),
            major: 1,
            minor: 0,
            binding: BINDING_LOLA,
            service_id: 42,
        }
    }

    fn drain<B: FFIBridge>(state: &Arc<StreamState<B>>) -> Vec<Result<ServiceDescriptor>> {
        state.queue.lock().unwrap().drain(..).collect()
    }

    #[test]
    fn apply_snapshot_deduplicates_and_reports_reoffer_after_withdrawal() {
        let state = new_stream_state::<SharedMockBridge>();

        apply_snapshot(&state, 0, &[identity("/svc/A", 1), identity("/svc/A", 2)]);
        let first = drain(&state);
        assert_eq!(first.len(), 2, "both newly observed instances must be reported once");
        assert_eq!(first[0].as_ref().unwrap().instance_id(), 1);
        assert_eq!(first[1].as_ref().unwrap().instance_id(), 2);
        assert_eq!(first[0].as_ref().unwrap().service_type_name(), "/svc/A");
        assert_eq!(first[0].as_ref().unwrap().version(), ServiceVersion::new(1, 0));
        assert_eq!(first[0].as_ref().unwrap().binding(), "lola");

        // An unchanged complete snapshot must not produce duplicates.
        apply_snapshot(&state, 0, &[identity("/svc/A", 1), identity("/svc/A", 2)]);
        assert!(drain(&state).is_empty(), "unchanged snapshots must be deduplicated");

        // Withdrawal of instance 2 produces no availability item.
        apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
        assert!(drain(&state).is_empty(), "withdrawal must not yield an availability item");

        // Re-offering the same identity emits it again.
        apply_snapshot(&state, 0, &[identity("/svc/A", 1), identity("/svc/A", 2)]);
        let reoffered = drain(&state);
        assert_eq!(reoffered.len(), 1, "only the re-offered instance is emitted");
        assert_eq!(reoffered[0].as_ref().unwrap().instance_id(), 2);
    }

    #[test]
    fn empty_withdrawal_snapshot_clears_membership_and_allows_reoffer() {
        let state = new_stream_state::<SharedMockBridge>();
        apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
        assert_eq!(drain(&state).len(), 1);

        // Native delivers an empty complete set on withdrawal; membership must be cleared.
        apply_snapshot(&state, 0, &[]);
        assert!(drain(&state).is_empty());

        apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
        assert_eq!(drain(&state).len(), 1);
    }

    #[test]
    fn overlapping_watches_deduplicate_by_global_identity() {
        let state = new_stream_state::<SharedMockBridge>();

        // Same identity observed by two overlapping watches is emitted once globally.
        apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
        apply_snapshot(&state, 1, &[identity("/svc/A", 1)]);
        assert_eq!(drain(&state).len(), 1);

        // One watch withdrawing does not re-emit while the other still observes the service.
        apply_snapshot(&state, 0, &[]);
        assert!(drain(&state).is_empty());

        // Only when the last observer withdraws and re-offers does a new item appear.
        apply_snapshot(&state, 1, &[]);
        assert!(drain(&state).is_empty());
        apply_snapshot(&state, 1, &[identity("/svc/A", 1)]);
        assert_eq!(drain(&state).len(), 1);
    }

    #[test]
    fn distinct_interfaces_with_same_instance_id_stay_distinct() {
        let state = new_stream_state::<SharedMockBridge>();
        apply_snapshot(&state, 0, &[identity("/svc/A", 7), identity("/svc/B", 7)]);
        let items = drain(&state);
        assert_eq!(items.len(), 2, "same numeric instance id on different interfaces must not be deduplicated");
    }

    #[test]
    fn never_polled_drop_stops_every_watch() {
        let handle_alloc = MockPointerAllocator::<FindServiceHandle>::new();
        let mut mock = MockFFIBridge::new();
        mock.expect_enumerate_service_types()
            .returning(|| vec![service_type("/svc/A")]);
        let alloc = handle_alloc.clone();
        mock.expect_start_find_service_any()
            .returning(move |_, _, _, _| alloc.allocate());

        let cleanup = handle_alloc.clone();
        mock.expect_stop_find_service().returning(move |ptr| {
            assert!(cleanup.free(ptr), "stop_find_service called with an unknown handle");
        });

        let bridge = SharedMockBridge::new(mock);
        let stream = build_all_services_stream(&bridge).expect("stream creation must succeed");
        drop(stream);
        handle_alloc.assert_all_freed();
    }

    #[test]
    fn partial_start_failure_rolls_back_earlier_watches() {
        let handle_alloc = MockPointerAllocator::<FindServiceHandle>::new();
        let mut mock = MockFFIBridge::new();
        mock.expect_enumerate_service_types()
            .returning(|| vec![service_type("/svc/A"), service_type("/svc/B")]);

        let alloc = handle_alloc.clone();
        let start_count = AtomicUsize::new(0);
        mock.expect_start_find_service_any().returning(move |_, _, _, _| {
            if start_count.fetch_add(1, Ordering::SeqCst) == 0 {
                alloc.allocate()
            } else {
                std::ptr::null_mut()
            }
        });

        let cleanup = handle_alloc.clone();
        mock.expect_stop_find_service().returning(move |ptr| {
            assert!(cleanup.free(ptr), "stop_find_service called with an unknown handle");
        });

        let bridge = SharedMockBridge::new(mock);
        let result = build_all_services_stream(&bridge);
        assert!(matches!(
            result,
            Err(Error::ServiceError(ServiceFailedReason::FailedToStartDiscovery))
        ));
        handle_alloc.assert_all_freed();
    }

    #[test]
    fn empty_universe_stream_is_pending_not_one_shot() {
        let mut mock = MockFFIBridge::new();
        mock.expect_enumerate_service_types().returning(Vec::<NativeServiceType>::new);
        mock.expect_start_find_service_any().never();

        let bridge = SharedMockBridge::new(mock);
        let stream = build_all_services_stream(&bridge).expect("stream creation must succeed");
        let mut pinned = Box::pin(stream);
        let waker = futures::task::noop_waker();
        let mut context = Context::from_waker(&waker);
        assert!(
            matches!(pinned.as_mut().poll_next(&mut context), Poll::Pending),
            "an empty configured universe must yield a pending stream, not a terminated one"
        );
    }
}
