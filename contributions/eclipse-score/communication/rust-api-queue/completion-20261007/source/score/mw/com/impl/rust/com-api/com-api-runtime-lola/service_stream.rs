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
//! type with a LoLa instance deployment in the loaded native configuration. The deployment supplies the configured
//! quality level; type declarations without such a deployment are not observed. Each watch reports currently offered
//! provider instances of that type, including provider instances whose concrete instance id is absent from the consumer's
//! configuration. Availability items are emitted the first time a full identity (service type name, version, binding,
//! binding service id and concrete instance id) becomes visible across all watches, and again after that identity was
//! withdrawn everywhere and is later re-offered.
//!
//! # Pending items, errors and termination
//! * Pending availability items are coalesced: at most one item is pending per identity that is currently offered,
//!   and a pending item is discarded when its identity is withdrawn everywhere before the consumer polls it. The
//!   number of pending items is therefore bounded by the number of currently offered identities in the configured
//!   universe. A consumer that polls slower than providers flap observes the latest availability state, not every
//!   intermediate offer/withdraw transition.
//! * Start-up failures are returned by the constructor (`FailedToStartDiscovery`; already started watches are stopped
//!   before returning). Once started, the stream yields only `Ok` items: native discovery does not report errors to
//!   an active watch, so no runtime error item is produced.
//! * The stream is infinite: it never yields `None` while it exists. It terminates when it is dropped, which stops
//!   every native watch.
//!
//! # Callback ownership
//! Native registration owns each callback after success and disposes it when the
//! watch is destroyed. A failed registration leaves ownership with Rust, which
//! reclaims the box and rolls back earlier watches. Each callback holds only a Weak
//! reference to stream state, so deferred native deletion cannot retain the queue.
//! A callback arriving after stream drop observes no state and returns safely.

use core::pin::Pin;
use core::task::{Context, Poll};
use std::collections::{hash_map::Entry as HashMapEntry, HashMap, HashSet, VecDeque};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex, Weak};

use futures::stream::Stream;
use futures::task::AtomicWaker;

use bridge_ffi_rs::{
    FFIBridge, FatPtr, FindServiceCallable, FindServiceHandle, HandleContainer, NativeFindServiceHandle,
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

/// Per-watch current membership plus global refcounts, so overlapping watches do not emit the same service twice,
/// and the coalesced pending items.
///
/// Invariant: every identity in `pending` has a non-zero refcount and appears at most once, so
/// `pending.len() <= refcount.len()`, i.e. the backlog is bounded by the currently offered identities.
#[derive(Default)]
struct MembershipState {
    per_watch: HashMap<u32, HashSet<IdentityKey>>,
    refcount: HashMap<IdentityKey, u32>,
    pending: VecDeque<(IdentityKey, ServiceDescriptor)>,
}

/// Owns one started native watch. Kept next to the bridge so it can be stopped after the runtime borrow ends.
struct WatchHandle<B: FFIBridge> {
    handle: NativeFindServiceHandle,
    bridge: B,
}

/// Shared state between the returned stream and the native discovery callbacks.
struct StreamState<B: FFIBridge> {
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
        members: Mutex::new(MembershipState::default()),
        watches: Mutex::new(Vec::new()),
        waker: AtomicWaker::new(),
        finished: AtomicBool::new(false),
    })
}

/// Apply one complete per-watch snapshot of observed identities.
///
/// The diff against the watch's previous membership drives both withdrawal and re-offer handling: a removed identity
/// decrements its global refcount (and is forgotten, including any still pending item, once it reaches zero), while an
/// identity that transitions from a global refcount of zero to one becomes a newly available pending item.
fn apply_snapshot<B: FFIBridge>(state: &Arc<StreamState<B>>, watch_slot: u32, identities: &[NativeServiceIdentity]) {
    let mut current: HashSet<IdentityKey> = HashSet::with_capacity(identities.len());
    let mut descriptors: HashMap<IdentityKey, ServiceDescriptor> = HashMap::with_capacity(identities.len());
    for identity in identities {
        if identity.name.is_empty() {
            continue;
        }
        let key = IdentityKey::from_identity(identity);
        current.insert(key.clone());
        descriptors
            .entry(key)
            .or_insert_with(|| descriptor_from_identity(identity));
    }

    let became_available = {
        let mut guard = state.members.lock().expect("stream membership poisoned");
        let members = &mut *guard;
        let previous = members
            .per_watch
            .insert(watch_slot, current.clone())
            .unwrap_or_default();

        for removed in previous.difference(&current) {
            if let HashMapEntry::Occupied(mut entry) = members.refcount.entry(removed.clone()) {
                let value = entry.get_mut();
                *value = value.saturating_sub(1);
                if *value == 0 {
                    entry.remove();
                    // Withdrawn everywhere before being polled: drop the stale pending item.
                    members.pending.retain(|(key, _)| key != removed);
                }
            }
        }

        let mut became_available = false;
        for added in current.difference(&previous) {
            let entry = members.refcount.entry(added.clone()).or_insert(0);
            *entry += 1;
            if *entry == 1 {
                if let Some(descriptor) = descriptors.remove(added) {
                    members.pending.push_back((added.clone(), descriptor));
                    became_available = true;
                }
            }
        }
        became_available
    };

    if became_available {
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
        // Native watch deletion may be deferred; its callback must not retain stream state.
        let callback_state: Weak<StreamState<B>> = Arc::downgrade(&state);
        let callback_bridge = bridge.clone();
        // The callback only diffs collected identities; it never touches `watches`, so it is safe for it to fire
        // synchronously before this iteration stores its own handle.
        let callback = Box::new(move |handles: HandleContainer, _handle: NativeFindServiceHandle| {
            let Some(state) = callback_state.upgrade() else {
                return;
            };
            let identities = collect_identities(&callback_bridge, &handles);
            apply_snapshot(&state, slot as u32, &identities);
        });
        let dyn_callback: Box<dyn FnMut(HandleContainer, NativeFindServiceHandle) + Send + 'static> = callback;
        // SAFETY: `dyn_callback` is a `FnMut(HandleContainer, NativeFindServiceHandle)`, exactly the find-service
        // callback contract, and its `FatPtr` is passed to native discovery.
        let raw_callback = Box::into_raw(dyn_callback);
        let fat_ptr: FatPtr = unsafe { std::mem::transmute(raw_callback) };
        let callable = unsafe { FindServiceCallable::new(fat_ptr) };

        let raw_handle =
            bridge.start_find_service_type(&service_type.name, service_type.major, service_type.minor, &callable);
        if raw_handle.is_null() {
            // SAFETY: failed native registration leaves this box with the caller.
            drop(unsafe { Box::from_raw(raw_callback) });
            // Partial start failure: stop every watch that was already started, in reverse order, before returning.
            for mut watch in started.drain(..).rev() {
                // SAFETY: this handle was returned by start_find_service_type and has not been stopped yet.
                unsafe {
                    watch
                        .bridge
                        .stop_find_service(watch.handle.as_mut() as *mut FindServiceHandle)
                };
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

impl<B: FFIBridge> LolaAllServicesStream<B> {
    fn pop_pending(&self) -> Option<Result<ServiceDescriptor>> {
        let mut members = self.state.members.lock().expect("stream membership poisoned");
        members.pending.pop_front().map(|(_, descriptor)| Ok(descriptor))
    }
}

impl<B: FFIBridge> Stream for LolaAllServicesStream<B> {
    type Item = Result<ServiceDescriptor>;

    fn poll_next(self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        if let Some(item) = self.pop_pending() {
            return Poll::Ready(Some(item));
        }

        if self.state.finished.load(Ordering::Acquire) {
            return Poll::Ready(None);
        }

        // Register before re-checking so a concurrent callback cannot slip in between the check and the registration.
        self.state.waker.register(cx.waker());
        match self.pop_pending() {
            Some(item) => Poll::Ready(Some(item)),
            None => Poll::Pending,
        }
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
            // SAFETY: this handle was returned by start_find_service_type and has not been stopped yet.
            unsafe {
                watch
                    .bridge
                    .stop_find_service(watch.handle.as_mut() as *mut FindServiceHandle)
            };
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use bridge_ffi_mock::{MockFFIBridge, MockPointerAllocator, SharedMockBridge};
    use bridge_ffi_rs::NativeServiceType;
    use std::sync::atomic::AtomicUsize;

    fn retain_callback(
        pointer: *mut FindServiceHandle,
        callable: &FindServiceCallable,
        callbacks: &Arc<Mutex<HashMap<usize, Vec<FatPtr>>>>,
    ) {
        callbacks
            .lock()
            .unwrap()
            .entry(pointer as usize)
            .or_default()
            .push(*callable.as_fat_ptr());
    }

    fn release_callback(pointer: *mut FindServiceHandle, callbacks: &Arc<Mutex<HashMap<usize, Vec<FatPtr>>>>) {
        let pointer = {
            let mut callbacks = callbacks.lock().unwrap();
            let key = pointer as usize;
            let values = callbacks.get_mut(&key).unwrap();
            let pointer = values.pop().unwrap();
            if values.is_empty() {
                callbacks.remove(&key);
            }
            pointer
        };
        // SAFETY: the mock takes the owned boxed callback on successful registration,
        // and releases it once after its final invocation, matching native teardown.
        let callback: *mut (dyn FnMut(HandleContainer, NativeFindServiceHandle) + Send + 'static) =
            unsafe { std::mem::transmute(pointer) };
        drop(unsafe { Box::from_raw(callback) });
    }

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
        state
            .members
            .lock()
            .unwrap()
            .pending
            .drain(..)
            .map(|(_, descriptor)| Ok(descriptor))
            .collect()
    }

    fn pending_len<B: FFIBridge>(state: &Arc<StreamState<B>>) -> usize {
        state.members.lock().unwrap().pending.len()
    }

    #[test]
    fn apply_snapshot_deduplicates_and_reports_reoffer_after_withdrawal() {
        let state = new_stream_state::<SharedMockBridge>();

        apply_snapshot(&state, 0, &[identity("/svc/A", 1), identity("/svc/A", 2)]);
        let first = drain(&state);
        assert_eq!(first.len(), 2, "both newly observed instances must be reported once");
        // Items observed in one snapshot have no defined relative order; compare them as a set.
        let mut instance_ids: Vec<_> = first.iter().map(|item| item.as_ref().unwrap().instance_id()).collect();
        instance_ids.sort_unstable();
        assert_eq!(instance_ids, vec![1, 2]);
        for item in &first {
            let descriptor = item.as_ref().unwrap();
            assert_eq!(descriptor.service_type_name(), "/svc/A");
            assert_eq!(descriptor.version(), ServiceVersion::new(1, 0));
            assert_eq!(descriptor.binding(), "lola");
        }

        // An unchanged complete snapshot must not produce duplicates.
        apply_snapshot(&state, 0, &[identity("/svc/A", 1), identity("/svc/A", 2)]);
        assert!(drain(&state).is_empty(), "unchanged snapshots must be deduplicated");

        // Withdrawal of instance 2 produces no availability item.
        apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
        assert!(
            drain(&state).is_empty(),
            "withdrawal must not yield an availability item"
        );

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
        assert_eq!(
            items.len(),
            2,
            "same numeric instance id on different interfaces must not be deduplicated"
        );
    }

    #[test]
    fn never_polled_drop_stops_every_watch() {
        let callbacks = Arc::new(Mutex::new(HashMap::new()));
        let handle_alloc = MockPointerAllocator::<FindServiceHandle>::new();
        let mut mock = MockFFIBridge::new();
        mock.expect_enumerate_service_types()
            .returning(|| vec![service_type("/svc/A")]);
        let alloc = handle_alloc.clone();
        let registered = Arc::clone(&callbacks);
        mock.expect_start_find_service_type()
            .returning(move |_, _, _, callable| {
                let pointer = alloc.allocate();
                retain_callback(pointer, callable, &registered);
                pointer
            });

        let cleanup = handle_alloc.clone();
        let retained = Arc::clone(&callbacks);
        mock.expect_stop_find_service().returning(move |ptr| {
            release_callback(ptr, &retained);
            assert!(cleanup.free(ptr), "stop_find_service called with an unknown handle");
        });

        let bridge = SharedMockBridge::new(mock);
        let stream = build_all_services_stream(&bridge).expect("stream creation must succeed");
        drop(stream);
        handle_alloc.assert_all_freed();
        assert!(
            callbacks.lock().unwrap().is_empty(),
            "every accepted callback must be reclaimed"
        );
    }

    #[test]
    fn partial_start_failure_rolls_back_earlier_watches() {
        let callbacks = Arc::new(Mutex::new(HashMap::new()));
        let handle_alloc = MockPointerAllocator::<FindServiceHandle>::new();
        let mut mock = MockFFIBridge::new();
        mock.expect_enumerate_service_types()
            .returning(|| vec![service_type("/svc/A"), service_type("/svc/B")]);

        let alloc = handle_alloc.clone();
        let registered = Arc::clone(&callbacks);
        let start_count = AtomicUsize::new(0);
        mock.expect_start_find_service_type()
            .returning(move |_, _, _, callable| {
                if start_count.fetch_add(1, Ordering::SeqCst) == 0 {
                    let pointer = alloc.allocate();
                    retain_callback(pointer, callable, &registered);
                    pointer
                } else {
                    std::ptr::null_mut()
                }
            });

        let cleanup = handle_alloc.clone();
        let retained = Arc::clone(&callbacks);
        mock.expect_stop_find_service().returning(move |ptr| {
            release_callback(ptr, &retained);
            assert!(cleanup.free(ptr), "stop_find_service called with an unknown handle");
        });

        let bridge = SharedMockBridge::new(mock);
        let result = build_all_services_stream(&bridge);
        assert!(matches!(
            result,
            Err(Error::ServiceError(ServiceFailedReason::FailedToStartDiscovery))
        ));
        handle_alloc.assert_all_freed();
        assert!(
            callbacks.lock().unwrap().is_empty(),
            "every accepted callback must be reclaimed"
        );
    }

    #[test]
    fn empty_universe_stream_is_pending_not_one_shot() {
        let mut mock = MockFFIBridge::new();
        mock.expect_enumerate_service_types()
            .returning(Vec::<NativeServiceType>::new);
        mock.expect_start_find_service_type().never();

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

    #[test]
    fn unpolled_flapping_is_coalesced_to_currently_offered_identities() {
        let state = new_stream_state::<SharedMockBridge>();

        // A provider that flaps many times while nobody polls must not grow the backlog.
        for _ in 0..1000 {
            apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
            apply_snapshot(&state, 0, &[]);
        }
        assert_eq!(
            pending_len(&state),
            0,
            "withdrawn identities must not leave pending items behind"
        );

        for _ in 0..1000 {
            apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
            apply_snapshot(&state, 0, &[]);
        }
        apply_snapshot(&state, 0, &[identity("/svc/A", 1)]);
        assert_eq!(
            pending_len(&state),
            1,
            "the latest availability state is reported exactly once"
        );
        let items = drain(&state);
        assert_eq!(items[0].as_ref().unwrap().instance_id(), 1);
    }

    #[test]
    fn pending_items_never_exceed_currently_offered_identities() {
        let state = new_stream_state::<SharedMockBridge>();
        apply_snapshot(
            &state,
            0,
            &[identity("/svc/A", 1), identity("/svc/A", 2), identity("/svc/A", 3)],
        );
        apply_snapshot(&state, 1, &[identity("/svc/B", 1)]);
        assert_eq!(pending_len(&state), 4);

        // Withdrawing instance 2 before it is polled drops only its pending item.
        apply_snapshot(&state, 0, &[identity("/svc/A", 1), identity("/svc/A", 3)]);
        let mut remaining: Vec<_> = drain(&state)
            .into_iter()
            .map(|item| {
                let descriptor = item.unwrap();
                (descriptor.service_type_name().to_string(), descriptor.instance_id())
            })
            .collect();
        remaining.sort();
        assert_eq!(
            remaining,
            vec![
                ("/svc/A".to_string(), 1),
                ("/svc/A".to_string(), 3),
                ("/svc/B".to_string(), 1)
            ]
        );
    }

    #[test]
    fn callbacks_do_not_keep_the_stream_state_alive() {
        let callbacks = Arc::new(Mutex::new(HashMap::new()));
        let handle_alloc = MockPointerAllocator::<FindServiceHandle>::new();
        let mut mock = MockFFIBridge::new();
        mock.expect_enumerate_service_types()
            .returning(|| vec![service_type("/svc/A"), service_type("/svc/B")]);
        let alloc = handle_alloc.clone();
        let registered = Arc::clone(&callbacks);
        mock.expect_start_find_service_type()
            .returning(move |_, _, _, callable| {
                let pointer = alloc.allocate();
                retain_callback(pointer, callable, &registered);
                pointer
            });
        let cleanup = handle_alloc.clone();
        let retained = Arc::clone(&callbacks);
        mock.expect_stop_find_service().returning(move |ptr| {
            release_callback(ptr, &retained);
            assert!(cleanup.free(ptr), "stop_find_service called with an unknown handle");
        });

        let bridge = SharedMockBridge::new(mock);
        let stream = build_all_services_stream(&bridge).expect("stream creation must succeed");
        assert_eq!(
            Arc::strong_count(&stream.state),
            1,
            "callbacks must not hold strong references"
        );
        assert_eq!(
            Arc::weak_count(&stream.state),
            2,
            "one weak reference per started watch"
        );

        let weak = Arc::downgrade(&stream.state);
        drop(stream);
        assert!(
            weak.upgrade().is_none(),
            "stream state must be freed when the stream is dropped"
        );
        handle_alloc.assert_all_freed();
        assert!(
            callbacks.lock().unwrap().is_empty(),
            "every accepted callback must be reclaimed"
        );
    }
}
