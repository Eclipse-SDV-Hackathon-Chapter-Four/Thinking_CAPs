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

//! This crate provides a mock implementation of the COM API for testing purposes.
//! It is meant to be used in conjunction with the `com-api` crate.
//! The mock implementation does not perform any real IPC and is not meant to be used in production.
//! It is only meant to be used for testing and development.
//!
//! The mock runtime keeps a process-wide, type-erased event bus shared by every
//! runtime instance created from [`RuntimeBuilderImpl`]. Offering a service makes it
//! discoverable and publishing an event makes the sample available to consumers that
//! subscribe to the same instance/event, so application code can be exercised end to
//! end without any backend.

#![allow(dead_code)]
//lifetime warning for all the Sample struct impl block . it is required for the Sample struct
// event lifetime parameter
// and mentaining lifetime of instances and data reference
// As of supressing clippy::needless_lifetimes
//TODO: revist this once com-api is stable - Ticket-234827
#![allow(clippy::needless_lifetimes)]

use core::cmp::Ordering;
use core::fmt::Debug;
use core::future::Future;
use core::marker::PhantomData;
use core::mem::MaybeUninit;
use core::ops::{Deref, DerefMut};
use std::any::Any;
use std::collections::{BTreeSet, HashMap, VecDeque};
use std::path::Path;
use std::sync::atomic::AtomicUsize;
use std::sync::{Mutex, OnceLock};

use futures::stream::{self, Stream};

use score_com_concept::{
    Builder, CommData, Consumer, ConsumerBuilder, ConsumerDescriptor, Error, FindServiceSpecifier, InstanceSpecifier,
    Interface, Producer, ProducerBuilder, ProviderInfo, Publisher, ReceiveFailedReason, Result, Runtime, RuntimeBuilder,
    Sample, SampleContainer, SampleMaybeUninit, SampleMut, ServiceDiscovery, Subscriber, Subscription,
};

/// Type-erased queue holding published but not yet received samples of one event stream.
type EventQueue = VecDeque<Box<dyn Any + Send>>;

/// Process-wide in-process state used by the mock runtime.
#[derive(Default)]
struct MockRegistry {
    /// Instance specifiers of services that are currently offered.
    offered: BTreeSet<String>,
    /// Published samples per `(instance_specifier, event_identifier)` event stream.
    events: HashMap<String, EventQueue>,
}

/// Access the process-wide mock registry, initializing it on first use.
fn registry() -> &'static Mutex<MockRegistry> {
    static REGISTRY: OnceLock<Mutex<MockRegistry>> = OnceLock::new();
    REGISTRY.get_or_init(|| Mutex::new(MockRegistry::default()))
}

/// Run `f` with exclusive access to the mock registry.
fn with_registry<R>(f: impl FnOnce(&mut MockRegistry) -> R) -> R {
    let mut guard = registry().lock().expect("mock registry mutex poisoned");
    f(&mut *guard)
}

/// Build the bus key identifying one event stream.
fn event_key(instance_specifier: &InstanceSpecifier, identifier: &str) -> String {
    format!("{}::{}", instance_specifier.as_ref(), identifier)
}

/// Test-oriented runtime that implements the [`Runtime`] contract in-process.
pub struct MockRuntimeImpl {}

#[derive(Clone, Debug)]
pub struct MockProviderInfo {
    instance_specifier: InstanceSpecifier,
}

impl ProviderInfo for MockProviderInfo {
    fn offer_service(&self) -> Result<()> {
        with_registry(|registry| {
            registry.offered.insert(self.instance_specifier.as_ref().to_string());
        });
        Ok(())
    }

    fn stop_offer_service(&self) -> Result<()> {
        with_registry(|registry| {
            registry.offered.remove(self.instance_specifier.as_ref());
        });
        Ok(())
    }
}

#[derive(Clone, Debug)]
pub struct MockConsumerInfo {
    instance_specifier: InstanceSpecifier,
}

impl Runtime for MockRuntimeImpl {
    type ServiceDiscovery<I: Interface + Send> = MockConsumerDiscovery<I>;
    type Subscriber<T: CommData + Debug> = MockSubscribableImpl<T>;
    type ProducerBuilder<I: Interface> = MockProducerBuilder<I>;
    type Publisher<T: CommData + Debug> = MockPublisher<T>;
    type ProviderInfo = MockProviderInfo;
    type ConsumerInfo = MockConsumerInfo;

    fn find_service<I: Interface + Send>(&self, instance_specifier: FindServiceSpecifier) -> Self::ServiceDiscovery<I> {
        MockConsumerDiscovery {
            specifier: instance_specifier,
            _interface: PhantomData,
        }
    }

    fn producer_builder<I: Interface>(&self, instance_specifier: InstanceSpecifier) -> Self::ProducerBuilder<I> {
        MockProducerBuilder::new(self, instance_specifier)
    }
}

/// An immutable snapshot of one received event sample.
#[derive(Debug)]
pub struct MockSample<'a, T>
where
    T: CommData + Debug,
{
    id: usize,
    inner: Box<T>,
    lifetime: PhantomData<&'a ()>,
}

static ID_COUNTER: AtomicUsize = AtomicUsize::new(0);

impl<'a, T> From<T> for MockSample<'a, T>
where
    T: CommData + Debug,
{
    fn from(value: T) -> Self {
        Self {
            id: ID_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed),
            inner: Box::new(value),
            lifetime: PhantomData,
        }
    }
}

impl<'a, T> Deref for MockSample<'a, T>
where
    T: CommData + Debug,
{
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &*self.inner
    }
}

impl<'a, T> Sample<T> for MockSample<'a, T> where T: CommData + Debug {}

impl<'a, T> PartialEq for MockSample<'a, T>
where
    T: CommData + Debug,
{
    fn eq(&self, other: &Self) -> bool {
        self.id == other.id
    }
}

impl<'a, T> Eq for MockSample<'a, T> where T: CommData + Debug {}

impl<'a, T> PartialOrd for MockSample<'a, T>
where
    T: CommData + Debug,
{
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl<'a, T> Ord for MockSample<'a, T>
where
    T: CommData + Debug,
{
    fn cmp(&self, other: &Self) -> Ordering {
        self.id.cmp(&other.id)
    }
}

/// A mutable sample buffer returned by the mock publisher.
#[derive(Debug)]
pub struct MockSampleMut<'a, T>
where
    T: CommData + Debug,
{
    data: T,
    key: String,
    lifetime: PhantomData<&'a ()>,
}

impl<'a, T> SampleMut<T> for MockSampleMut<'a, T>
where
    T: CommData + Debug,
{
    fn send(self) -> Result<()> {
        with_registry(|registry| {
            registry.events.entry(self.key).or_default().push_back(Box::new(self.data));
        });
        Ok(())
    }
}

impl<'a, T> Deref for MockSampleMut<'a, T>
where
    T: CommData + Debug,
{
    type Target = T;

    fn deref(&self) -> &Self::Target {
        &self.data
    }
}

impl<'a, T> DerefMut for MockSampleMut<'a, T>
where
    T: CommData + Debug,
{
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.data
    }
}

/// An uninitialized sample buffer returned by the mock publisher.
#[derive(Debug)]
pub struct MockSampleMaybeUninit<'a, T>
where
    T: CommData + Debug,
{
    data: MaybeUninit<T>,
    key: String,
    lifetime: PhantomData<&'a ()>,
}

impl<'a, T> SampleMaybeUninit<T> for MockSampleMaybeUninit<'a, T>
where
    T: CommData + Debug,
{
    type SampleMut = MockSampleMut<'a, T>;

    fn write(self, val: T) -> MockSampleMut<'a, T> {
        MockSampleMut {
            data: val,
            key: self.key,
            lifetime: PhantomData,
        }
    }

    unsafe fn assume_init(self) -> MockSampleMut<'a, T> {
        let data = unsafe { self.data.assume_init() };
        MockSampleMut {
            data,
            key: self.key,
            lifetime: PhantomData,
        }
    }
}

impl<'a, T> AsMut<core::mem::MaybeUninit<T>> for MockSampleMaybeUninit<'a, T>
where
    T: CommData + Debug,
{
    fn as_mut(&mut self) -> &mut core::mem::MaybeUninit<T> {
        &mut self.data
    }
}

/// Mock publisher that forwards samples to the in-process event bus.
#[derive(Debug)]
pub struct MockPublisher<T>
where
    T: CommData + Debug,
{
    key: String,
    _data: PhantomData<T>,
}

impl<T> Publisher<T, MockRuntimeImpl> for MockPublisher<T>
where
    T: CommData + Debug,
{
    type SampleMaybeUninit<'a>
        = MockSampleMaybeUninit<'a, T>
    where
        Self: 'a;

    fn allocate(&self) -> Result<Self::SampleMaybeUninit<'_>> {
        Ok(MockSampleMaybeUninit {
            data: MaybeUninit::uninit(),
            key: self.key.clone(),
            lifetime: PhantomData,
        })
    }

    fn new(identifier: &str, instance_info: MockProviderInfo) -> Result<Self> {
        Ok(Self {
            key: event_key(&instance_info.instance_specifier, identifier),
            _data: PhantomData,
        })
    }
}

/// Mock subscriber created by the generated consumer for one event.
#[derive(Debug)]
pub struct MockSubscribableImpl<T>
where
    T: CommData + Debug,
{
    identifier: &'static str,
    instance_info: MockConsumerInfo,
    data: PhantomData<T>,
}

impl<T> Subscriber<T, MockRuntimeImpl> for MockSubscribableImpl<T>
where
    T: CommData + Debug,
{
    type Subscription = MockSubscriberImpl<T>;

    fn new(identifier: &'static str, instance_info: MockConsumerInfo) -> Result<Self> {
        Ok(Self {
            identifier,
            instance_info,
            data: PhantomData,
        })
    }

    fn subscribe(self, max_num_samples: usize) -> Result<Self::Subscription> {
        Ok(MockSubscriberImpl {
            identifier: self.identifier,
            instance_info: self.instance_info,
            max_num_samples,
            data: PhantomData,
        })
    }
}

/// Active mock subscription reading samples from the in-process event bus.
#[derive(Debug)]
pub struct MockSubscriberImpl<T>
where
    T: CommData + Debug,
{
    identifier: &'static str,
    instance_info: MockConsumerInfo,
    max_num_samples: usize,
    data: PhantomData<T>,
}

impl<T> MockSubscriberImpl<T>
where
    T: CommData + Debug,
{
    /// Inject a sample directly into this subscription's event stream.
    ///
    /// Backend-free counterpart of a producer publishing an event, primarily useful in
    /// focused unit tests. Samples are delivered in reception order (oldest first).
    pub fn add_data(&self, data: T) {
        let key = self.key();
        with_registry(|registry| {
            registry.events.entry(key).or_default().push_back(Box::new(data));
        });
    }

    fn key(&self) -> String {
        event_key(&self.instance_info.instance_specifier, self.identifier)
    }

    /// Move up to `max_samples` queued samples into `scratch`, returning the number added.
    fn drain_into<'a>(&'a self, scratch: &mut SampleContainer<MockSample<'a, T>>, max_samples: usize) -> usize {
        let key = self.key();
        let drained: Vec<Box<dyn Any + Send>> = with_registry(|registry| {
            let mut drained = Vec::new();
            if let Some(queue) = registry.events.get_mut(&key) {
                for _ in 0..max_samples {
                    match queue.pop_front() {
                        Some(item) => drained.push(item),
                        None => break,
                    }
                }
            }
            drained
        });

        let mut added = 0;
        for item in drained {
            if let Ok(boxed) = item.downcast::<T>() {
                let sample = MockSample {
                    id: ID_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed),
                    inner: boxed,
                    lifetime: PhantomData,
                };
                if scratch.push_back(sample).is_err() {
                    break;
                }
                added += 1;
            }
        }
        added
    }
}

impl<T> Subscription<T, MockRuntimeImpl> for MockSubscriberImpl<T>
where
    T: CommData + Debug,
{
    type Subscriber = MockSubscribableImpl<T>;
    type Sample<'a>
        = MockSample<'a, T>
    where
        Self: 'a;

    fn unsubscribe(self) -> Self::Subscriber {
        MockSubscribableImpl {
            identifier: self.identifier,
            instance_info: self.instance_info,
            data: PhantomData,
        }
    }

    fn try_receive<'a>(
        &'a self,
        scratch: &'_ mut SampleContainer<Self::Sample<'a>>,
        max_samples: usize,
    ) -> Result<usize> {
        if max_samples == 0 {
            return Err(Error::ReceiveError(ReceiveFailedReason::SampleCountOutOfBounds {
                max: max_samples,
                requested: 0,
            }));
        }
        Ok(self.drain_into(scratch, max_samples))
    }

    #[allow(clippy::manual_async_fn)]
    fn cancellable_receive<'a>(
        &'a self,
        mut scratch: SampleContainer<Self::Sample<'a>>,
        new_samples: usize,
        max_samples: usize,
        cancellation: impl Future<Output = ()> + Send + 'static,
    ) -> impl Future<Output = (SampleContainer<Self::Sample<'a>>, Result<usize>)> + 'a {
        async move {
            if max_samples == 0 || new_samples == 0 {
                return (
                    scratch,
                    Err(Error::ReceiveError(ReceiveFailedReason::InputValueOutOfBounds {
                        max: max_samples,
                        requested: new_samples,
                    })),
                );
            }

            let mut added = match self.try_receive(&mut scratch, max_samples) {
                Ok(received) => received,
                Err(error) => return (scratch, Err(error)),
            };

            if added >= new_samples {
                return (scratch, Ok(added));
            }

            // No async notification channel in the mock: progress after the first probe
            // only happens once the caller cancels.
            cancellation.await;
            if let Ok(received) = self.try_receive(&mut scratch, max_samples) {
                added += received;
            }
            (scratch, Ok(added))
        }
    }

    fn to_stream<'a>(&'a mut self) -> impl Stream<Item = Result<Self::Sample<'a>>> + Unpin + 'a {
        let key = self.key();
        let drained: Vec<Box<dyn Any + Send>> = with_registry(|registry| {
            registry
                .events
                .get_mut(&key)
                .map(|queue| queue.drain(..).collect::<Vec<Box<dyn Any + Send>>>())
                .unwrap_or_default()
        });

        let items: Vec<Result<Self::Sample<'a>>> = drained
            .into_iter()
            .filter_map(|item| item.downcast::<T>().ok())
            .map(|value| {
                Ok(MockSample {
                    id: ID_COUNTER.fetch_add(1, std::sync::atomic::Ordering::Relaxed),
                    inner: value,
                    lifetime: PhantomData,
                })
            })
            .collect();
        stream::iter(items)
    }
}

/// Service discovery backed by the in-process registry of offered instances.
pub struct MockConsumerDiscovery<I> {
    specifier: FindServiceSpecifier,
    _interface: PhantomData<I>,
}

impl<I: Interface + Send> ServiceDiscovery<I, MockRuntimeImpl> for MockConsumerDiscovery<I>
where
    MockConsumerBuilder<I>: ConsumerBuilder<I, MockRuntimeImpl>,
{
    type ConsumerBuilder = MockConsumerBuilder<I>;
    type ServiceEnumerator = Vec<MockConsumerBuilder<I>>;

    fn get_available_instances(&self) -> Result<Self::ServiceEnumerator> {
        let offered: Vec<String> = with_registry(|registry| registry.offered.iter().cloned().collect());
        let selected: Vec<String> = match &self.specifier {
            FindServiceSpecifier::Specific(specifier) => offered
                .into_iter()
                .filter(|candidate| candidate.as_str() == specifier.as_ref())
                .collect(),
            FindServiceSpecifier::Any => offered,
        };

        Ok(selected
            .into_iter()
            .map(|specifier| MockConsumerBuilder {
                instance_specifier: InstanceSpecifier::new(specifier).expect("offered instance specifier stays valid"),
                _interface: PhantomData,
            })
            .collect())
    }

    #[allow(clippy::manual_async_fn)]
    fn get_available_instances_async(&self) -> impl Future<Output = Result<Self::ServiceEnumerator>> + Send {
        let result = self.get_available_instances();
        async move { result }
    }
}

/// Builder for mock producer instances.
pub struct MockProducerBuilder<I: Interface> {
    instance_specifier: InstanceSpecifier,
    _interface: PhantomData<I>,
}

impl<I: Interface> MockProducerBuilder<I> {
    fn new(_runtime: &MockRuntimeImpl, instance_specifier: InstanceSpecifier) -> Self {
        Self {
            instance_specifier,
            _interface: PhantomData,
        }
    }
}

impl<I: Interface> ProducerBuilder<I, MockRuntimeImpl> for MockProducerBuilder<I> {}

impl<I: Interface> Builder<I::Producer<MockRuntimeImpl>> for MockProducerBuilder<I> {
    fn build(self) -> Result<I::Producer<MockRuntimeImpl>> {
        I::Producer::new(MockProviderInfo {
            instance_specifier: self.instance_specifier,
        })
    }
}

/// Builder for mock consumer instances produced by service discovery.
pub struct MockConsumerBuilder<I: Interface> {
    instance_specifier: InstanceSpecifier,
    _interface: PhantomData<I>,
}

impl<I: Interface> ConsumerDescriptor<MockRuntimeImpl> for MockConsumerBuilder<I> {
    fn get_instance_specifier(&self) -> &InstanceSpecifier {
        // For the mock runtime, simply return the stored instance specifier.
        &self.instance_specifier
    }
}

impl<I: Interface> ConsumerBuilder<I, MockRuntimeImpl> for MockConsumerBuilder<I> {}

impl<I: Interface> Builder<I::Consumer<MockRuntimeImpl>> for MockConsumerBuilder<I> {
    fn build(self) -> Result<I::Consumer<MockRuntimeImpl>> {
        Ok(Consumer::new(MockConsumerInfo {
            instance_specifier: self.instance_specifier,
        }))
    }
}

pub struct RuntimeBuilderImpl {}

impl Builder<MockRuntimeImpl> for RuntimeBuilderImpl {
    fn build(self) -> Result<MockRuntimeImpl> {
        Ok(MockRuntimeImpl {})
    }
}

/// Entry point for the default implementation for the com module of s-core
impl RuntimeBuilder<MockRuntimeImpl> for RuntimeBuilderImpl {
    fn load_config(&mut self, _config: &Path) -> &mut Self {
        self
    }
}

impl Default for RuntimeBuilderImpl {
    fn default() -> Self {
        Self::new()
    }
}

impl RuntimeBuilderImpl {
    /// Creates a new instance of the default implementation of the com layer
    pub fn new() -> Self {
        Self {}
    }
}

#[cfg(test)]
mod tests {
    use core::marker::PhantomData;

    use crate::{MockConsumerInfo, MockRuntimeImpl, MockSubscribableImpl, RuntimeBuilderImpl};
    use score_com_concept::{
        Builder, CommData, Consumer, FindServiceSpecifier, InstanceSpecifier, Interface, OfferedProducer, Producer,
        ProviderInfo, Publisher, Reloc, Result, Runtime, SampleContainer, ServiceDiscovery, Subscriber, Subscription,
    };

    #[derive(Debug, Reloc, CommData)]
    #[repr(C)]
    struct TestData {
        value: u32,
    }

    struct TestInterface;

    struct TestConsumer<R: Runtime + ?Sized> {
        event: R::Subscriber<TestData>,
    }

    impl Interface for TestInterface {
        const INTERFACE_ID: &'static str = "mock_test::TestInterface";
        type Consumer<R: Runtime + ?Sized> = TestConsumer<R>;
        type Producer<R: Runtime + ?Sized> = TestProducer<R>;
    }

    impl<R: Runtime + ?Sized> Consumer<R> for TestConsumer<R> {
        fn new(instance_info: R::ConsumerInfo) -> Self {
            Self {
                event: <R::Subscriber<TestData> as Subscriber<TestData, R>>::new("event", instance_info)
                    .expect("failed to create mock subscriber"),
            }
        }
    }

    struct TestProducer<R: Runtime + ?Sized> {
        instance_info: R::ProviderInfo,
        _runtime: PhantomData<R>,
    }

    impl<R: Runtime + ?Sized> Producer<R> for TestProducer<R> {
        type Interface = TestInterface;
        type OfferedProducer = TestOfferedProducer<R>;

        fn offer(self) -> Result<Self::OfferedProducer> {
            let event = <R::Publisher<TestData> as Publisher<TestData, R>>::new("event", self.instance_info.clone())
                .expect("failed to create mock publisher");
            self.instance_info.offer_service()?;
            Ok(TestOfferedProducer {
                event,
                instance_info: self.instance_info,
            })
        }

        fn new(instance_info: R::ProviderInfo) -> Result<Self> {
            Ok(Self {
                instance_info,
                _runtime: PhantomData,
            })
        }
    }

    struct TestOfferedProducer<R: Runtime + ?Sized> {
        event: R::Publisher<TestData>,
        instance_info: R::ProviderInfo,
    }

    impl<R: Runtime + ?Sized> OfferedProducer<R> for TestOfferedProducer<R> {
        type Interface = TestInterface;
        type Producer = TestProducer<R>;

        fn unoffer(self) -> Result<Self::Producer> {
            self.instance_info.stop_offer_service()?;
            Ok(TestProducer {
                instance_info: self.instance_info,
                _runtime: PhantomData,
            })
        }
    }

    #[test]
    fn offer_publish_discover_receive_roundtrip() {
        let runtime = RuntimeBuilderImpl::new().build().expect("build mock runtime");
        let specifier = InstanceSpecifier::new("/mock_test/roundtrip").expect("valid instance specifier");

        let producer = runtime
            .producer_builder::<TestInterface>(specifier.clone())
            .build()
            .expect("build producer");
        let offered = producer.offer().expect("offer service");
        offered.event.send(TestData { value: 42 }).expect("publish sample");

        let discovery = runtime.find_service::<TestInterface>(FindServiceSpecifier::Specific(specifier));
        let consumers = discovery.get_available_instances().expect("discover offered instances");
        assert_eq!(consumers.len(), 1, "exactly one offered instance expected");

        let consumer = consumers
            .into_iter()
            .next()
            .expect("consumer builder")
            .build()
            .expect("build consumer");
        let subscription = consumer.event.subscribe(4).expect("subscribe to event");

        let mut container = SampleContainer::new(4);
        let received = subscription.try_receive(&mut container, 4).expect("receive sample");
        assert_eq!(received, 1);

        let sample = container.pop_front().expect("sample available");
        assert_eq!(sample.value, 42);

        let _ = offered.unoffer().expect("unoffer service");
    }

    #[test]
    fn manually_injected_data_is_received() {
        let instance_info = MockConsumerInfo {
            instance_specifier: InstanceSpecifier::new("/mock_test/manual").expect("valid instance specifier"),
        };
        let subscription = <MockSubscribableImpl<TestData> as Subscriber<TestData, MockRuntimeImpl>>::new(
            "event",
            instance_info,
        )
        .expect("create subscriber")
        .subscribe(2)
        .expect("subscribe to event");

        subscription.add_data(TestData { value: 7 });

        let mut container = SampleContainer::new(2);
        assert_eq!(subscription.try_receive(&mut container, 2).expect("receive sample"), 1);
        assert_eq!(container.pop_front().expect("sample available").value, 7);
    }
}
