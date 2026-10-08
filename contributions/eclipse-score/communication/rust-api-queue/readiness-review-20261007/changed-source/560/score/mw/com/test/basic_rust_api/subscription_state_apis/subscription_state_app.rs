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

//! Production-path Linux integration binary for the Rust subscription-state change API (#560).
//!
//! The binary runs in one of two roles:
//!
//! * **controller** (default, `--scenario <name>`): owns the production LoLa runtime, service
//!   discovery, the consumer and the subscription. It spawns *itself* in provider mode using
//!   standard child stdin/stdout pipes and drives a small, prefixed, phase-tagged line protocol.
//! * **provider** (`--provider`): owns a *separate* LoLa runtime and an offered
//!   `MixedPrimitivesInterface` producer. It executes `OFFER`, `WITHDRAW`, `SEND <marker>` and
//!   `FINISH` commands and acknowledges each one.
//!
//! The controller exercises the real production Rust -> C++ -> Rust callback path
//! (`Subscription::set_subscription_state_change_handler` -> FFI -> `ProxyEventBase` ->
//! `SubscriptionStateMachine` -> the Rust trampoline). No trampoline is called directly and no
//! mock bridge is linked. Registration is not expected to deliver an initial current-state
//! notification; the subscription state is established through the synchronous query before the
//! first handler is registered.
//!
//! Test diagnostics are emitted on stderr; only protocol acknowledgements are written to the
//! provider's stdout.

use std::io::{BufRead, BufReader, Stdout, Write};
use std::path::Path;
use std::process::{Child, ChildStdin, Command, Stdio};
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::mpsc::{channel, Receiver, RecvTimeoutError};
use std::sync::Arc;
use std::thread::{self, JoinHandle};
use std::time::{Duration, Instant};

use bigdata_com_api_gen::{MixedPrimitivesInterface, MixedPrimitivesPayload};
use score_com::{
    Builder, FindServiceSpecifier, InstanceSpecifier, LolaRuntimeBuilderImpl, OfferedProducer, Producer, Publisher,
    Runtime, RuntimeBuilder, SampleContainer, SampleMaybeUninit, SampleMut, ServiceDiscovery, Subscriber, Subscription,
    SubscriptionState,
};

/// Result type used throughout this binary. Failures carry a short human-readable description and
/// are reported on stderr before the process exits non-zero.
type AppResult<T> = std::result::Result<T, String>;

const CONFIG_PATH: &str = "etc/config.json";
const SERVICE_INSTANCE: &str = "/IntegrationTest/MixedPrimitives";
/// Unique prefix that separates protocol acknowledgements from native/application diagnostics.
const PROTOCOL_PREFIX: &str = "SSAPI-PROTO";
const MAX_SAMPLES: usize = 5;
const SAMPLE_MARKER_NOTIFICATIONS: u32 = 0x51;
const SAMPLE_MARKER_FALSE_THEN_DROP: u32 = 0x77;

const ACK_TIMEOUT: Duration = Duration::from_secs(30);
const EXIT_TIMEOUT: Duration = Duration::from_secs(30);
const DISCOVERY_TIMEOUT: Duration = Duration::from_secs(60);
const QUERY_TIMEOUT: Duration = Duration::from_secs(30);
const CALLBACK_TIMEOUT: Duration = Duration::from_secs(30);
const DISPOSAL_TIMEOUT: Duration = Duration::from_secs(30);
const SAMPLE_TIMEOUT: Duration = Duration::from_secs(30);
const POLL_INTERVAL: Duration = Duration::from_millis(20);

fn err_str<E: std::fmt::Debug>(error: E) -> String {
    format!("{:?}", error)
}

fn deadline_after(timeout: Duration) -> Instant {
    Instant::now() + timeout
}

fn main() {
    let arguments: Vec<String> = std::env::args().collect();
    if arguments.iter().any(|argument| argument == "--provider") {
        if let Err(error) = provider_entry() {
            eprintln!("[subscription-state-apis] provider failed: {}", error);
            std::process::exit(1);
        }
        return;
    }

    let scenario = match parse_scenario(&arguments) {
        Some(scenario) => scenario,
        None => {
            eprintln!(
                "[subscription-state-apis] usage: subscription-state-apis --scenario \
                 <notifications|replacement|unset|false-then-drop|drop-active>"
            );
            std::process::exit(2);
        },
    };

    if let Err(error) = controller_entry(scenario) {
        eprintln!(
            "[subscription-state-apis] controller scenario '{}' failed: {}",
            scenario, error
        );
        std::process::exit(1);
    }
}

fn parse_scenario(arguments: &[String]) -> Option<&str> {
    let mut iter = arguments.iter();
    while let Some(argument) = iter.next() {
        if argument == "--scenario" {
            return iter.next().map(String::as_str);
        }
    }
    None
}

fn provider_entry() -> AppResult<()> {
    let mut builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();
    builder.load_config(Path::new(CONFIG_PATH));
    let runtime = builder.build().map_err(err_str)?;
    provider_main(&runtime)
}

fn controller_entry(scenario: &str) -> AppResult<()> {
    let mut builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();
    builder.load_config(Path::new(CONFIG_PATH));
    let runtime = builder.build().map_err(err_str)?;
    run_controller(&runtime, scenario)
}

// ------------------------------------------------------------------------------------------------
// Provider child
// ------------------------------------------------------------------------------------------------

fn provider_main<R: Runtime>(runtime: &R) -> AppResult<()> {
    let specifier = InstanceSpecifier::new(SERVICE_INSTANCE).map_err(err_str)?;
    let initial_producer = runtime
        .producer_builder::<MixedPrimitivesInterface>(specifier)
        .build()
        .map_err(err_str)?;

    // The provider starts unoffered and only offers on the controller's OFFER command. The
    // returned producer is retained across `unoffer` so the *same* provider can be re-offered.
    // Types are inferred from the concrete runtime `R`; no cross-crate type aliases are required.
    let mut offered = None;
    let mut unoffered = Some(initial_producer);

    let stdin = std::io::stdin();
    let mut stdout = std::io::stdout();

    for line_result in stdin.lock().lines() {
        let line = line_result.map_err(|error| format!("provider stdin read failed: {}", error))?;
        let trimmed = line.trim();
        if trimmed.is_empty() {
            continue;
        }

        let fields: Vec<&str> = trimmed.split_whitespace().collect();
        if fields.len() < 3 || fields[0] != PROTOCOL_PREFIX {
            continue;
        }
        let phase = fields[1].to_string();
        let command = fields[2].to_string();

        let mut status = true;
        let mut fatal: Option<String> = None;

        match command.as_str() {
            "OFFER" => {
                if offered.is_none() {
                    if let Some(producer) = unoffered.take() {
                        match producer.offer() {
                            Ok(offered_producer) => offered = Some(offered_producer),
                            Err(error) => {
                                status = false;
                                fatal = Some(format!("offer failed: {:?}", error));
                            },
                        }
                    } else {
                        status = false;
                    }
                }
            },
            "WITHDRAW" => {
                if let Some(offered_producer) = offered.take() {
                    match offered_producer.unoffer() {
                        Ok(producer) => unoffered = Some(producer),
                        Err(error) => {
                            status = false;
                            fatal = Some(format!("unoffer failed: {:?}", error));
                        },
                    }
                }
            },
            "SEND" => {
                let marker = fields.get(3).copied().and_then(|value| value.parse::<u32>().ok());
                match (marker, offered.as_ref()) {
                    (Some(marker), Some(offered_producer)) => {
                        let payload = make_payload(marker);
                        match offered_producer.mixed_event.allocate() {
                            Ok(uninitialized) => {
                                let initialized = uninitialized.write(payload);
                                if let Err(error) = initialized.send() {
                                    status = false;
                                    fatal = Some(format!("send failed: {:?}", error));
                                }
                            },
                            Err(error) => {
                                status = false;
                                fatal = Some(format!("allocate failed: {:?}", error));
                            },
                        }
                    },
                    _ => status = false,
                }
            },
            "FINISH" => {
                if let Some(offered_producer) = offered.take() {
                    let _ = offered_producer.unoffer();
                }
                ack(&mut stdout, &phase, &command, true)?;
                return Ok(());
            },
            _ => status = false,
        }

        ack(&mut stdout, &phase, &command, status)?;
        if let Some(message) = fatal {
            return Err(message);
        }
    }

    Ok(())
}

fn make_payload(marker: u32) -> MixedPrimitivesPayload {
    MixedPrimitivesPayload {
        u64_val: u64::from(marker),
        i64_val: i64::from(marker),
        u32_val: marker,
        i32_val: i32::try_from(marker).unwrap_or(i32::MAX),
        f32_val: marker as f32 / 2.0,
        u16_val: u16::try_from(marker).unwrap_or(u16::MAX),
        i16_val: i16::try_from(marker).unwrap_or(i16::MAX),
        u8_val: u8::try_from(marker).unwrap_or(u8::MAX),
        i8_val: i8::try_from(marker).unwrap_or(i8::MAX),
        flag: marker.is_multiple_of(2),
    }
}

fn ack(stdout: &mut Stdout, phase: &str, command: &str, ok: bool) -> AppResult<()> {
    let status = if ok { "OK" } else { "ERR" };
    writeln!(stdout, "{} {} {} {}", PROTOCOL_PREFIX, phase, command, status)
        .map_err(|error| format!("provider stdout write failed: {}", error))?;
    stdout
        .flush()
        .map_err(|error| format!("provider stdout flush failed: {}", error))?;
    Ok(())
}

// ------------------------------------------------------------------------------------------------
// Controller side: provider child process and line protocol
// ------------------------------------------------------------------------------------------------

struct ProviderSession {
    child: Option<Child>,
    stdin: Option<ChildStdin>,
    receiver: Receiver<String>,
    reader: Option<JoinHandle<()>>,
    next_phase: u32,
    /// Non-protocol lines received from the provider stdout, retained for failure diagnostics.
    diagnostics: Vec<String>,
}

impl ProviderSession {
    fn offer(&mut self) -> AppResult<()> {
        self.command("OFFER", None)
    }

    fn withdraw(&mut self) -> AppResult<()> {
        self.command("WITHDRAW", None)
    }

    fn send_sample(&mut self, marker: u32) -> AppResult<()> {
        self.command("SEND", Some(marker))
    }

    fn finish(&mut self) -> AppResult<()> {
        self.finish_with_wait(Child::try_wait)
    }

    /// Keep the child in the session until it is reaped. Every error then leaves `Drop` able to
    /// terminate the owned process before joining its stdout reader. The injected poll operation
    /// permits deterministic testing of wait failures without changing the production protocol.
    fn finish_with_wait(
        &mut self,
        mut try_wait: impl FnMut(&mut Child) -> std::io::Result<Option<std::process::ExitStatus>>,
    ) -> AppResult<()> {
        self.command("FINISH", None)?;
        // Close the child stdin so a misbehaving provider cannot block on further reads.
        self.stdin.take();
        let deadline = deadline_after(EXIT_TIMEOUT);
        let status = loop {
            let child = self
                .child
                .as_mut()
                .ok_or_else(|| "provider child is missing".to_string())?;
            match try_wait(child) {
                Ok(Some(status)) => break status,
                Ok(None) => {
                    if Instant::now() >= deadline {
                        return Err("provider child did not exit after FINISH".to_string());
                    }
                    thread::sleep(POLL_INTERVAL);
                },
                Err(error) => return Err(format!("provider wait failed: {}", error)),
            }
        };
        self.child.take();
        if let Some(reader) = self.reader.take() {
            reader
                .join()
                .map_err(|_| "provider stdout reader panicked".to_string())?;
        }
        if !status.success() {
            return Err(format!("provider child exited unsuccessfully after FINISH: {}", status));
        }
        Ok(())
    }

    fn command(&mut self, command: &str, argument: Option<u32>) -> AppResult<()> {
        let phase = self.next_phase;
        self.next_phase = self.next_phase.wrapping_add(1);
        let line = match argument {
            Some(value) => format!("{} {} {} {}\n", PROTOCOL_PREFIX, phase, command, value),
            None => format!("{} {} {}\n", PROTOCOL_PREFIX, phase, command),
        };
        let stdin = self
            .stdin
            .as_mut()
            .ok_or_else(|| "provider stdin is closed".to_string())?;
        stdin
            .write_all(line.as_bytes())
            .map_err(|error| format!("provider stdin write failed: {}", error))?;
        stdin
            .flush()
            .map_err(|error| format!("provider stdin flush failed: {}", error))?;
        self.await_ack(phase, command)
    }

    fn await_ack(&mut self, phase: u32, command: &str) -> AppResult<()> {
        let deadline = deadline_after(ACK_TIMEOUT);
        loop {
            let now = Instant::now();
            if now >= deadline {
                if let Some(child) = self.child.as_mut() {
                    if let Ok(Some(status)) = child.try_wait() {
                        return Err(format!(
                            "provider exited early ({}) while awaiting {} phase {}",
                            status, command, phase
                        ));
                    }
                }
                return Err(format!("timeout awaiting {} phase {}", command, phase));
            }

            match self.receiver.recv_timeout(deadline - now) {
                Ok(line) => {
                    if line.starts_with(PROTOCOL_PREFIX) {
                        let parsed =
                            parse_protocol(&line).ok_or_else(|| format!("malformed protocol message: {}", line))?;
                        let (received_phase, received_command, ok) = parsed;
                        if received_phase != phase {
                            return Err(format!(
                                "protocol phase mismatch: expected {}, received {}",
                                phase, received_phase
                            ));
                        }
                        if received_command != command {
                            return Err(format!(
                                "protocol command mismatch: expected {}, received {}",
                                command, received_command
                            ));
                        }
                        if !ok {
                            return Err(format!("provider reported failure for {} phase {}", command, phase));
                        }
                        return Ok(());
                    }
                    self.diagnostics.push(line);
                },
                Err(RecvTimeoutError::Timeout) => {
                    return Err(format!("timeout awaiting {} phase {}", command, phase));
                },
                Err(RecvTimeoutError::Disconnected) => {
                    return Err(format!(
                        "provider stdout closed while awaiting {} phase {}",
                        command, phase
                    ));
                },
            }
        }
    }
}

impl Drop for ProviderSession {
    fn drop(&mut self) {
        // Close the child stdin so the provider sees EOF, then forcibly reap the owned child. The
        // reader thread owns no native handles and only exits once stdout is closed.
        self.stdin.take();
        if let Some(mut child) = self.child.take() {
            let _ = child.kill();
            let _ = child.wait();
        }
        if let Some(reader) = self.reader.take() {
            let _ = reader.join();
        }
    }
}

fn parse_protocol(line: &str) -> Option<(u32, String, bool)> {
    let remainder = line.strip_prefix(PROTOCOL_PREFIX)?;
    let mut fields = remainder.split_whitespace();
    let phase = fields.next()?.parse::<u32>().ok()?;
    let command = fields.next()?.to_string();
    let ok = fields.next()? == "OK";
    Some((phase, command, ok))
}

fn spawn_provider() -> AppResult<ProviderSession> {
    let executable = std::env::current_exe().map_err(|error| format!("cannot resolve current exe: {}", error))?;
    let child = Command::new(executable)
        .arg("--provider")
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        // Inherit stderr so an unread pipe cannot block the provider, and so native diagnostics are
        // visible in the integration-test log.
        .stderr(Stdio::inherit())
        .spawn()
        .map_err(|error| format!("failed to spawn provider child: {}", error))?;

    provider_session_from_child(child)
}

fn provider_session_from_child(mut child: Child) -> AppResult<ProviderSession> {
    let stdin = child
        .stdin
        .take()
        .ok_or_else(|| "provider child has no stdin".to_string())?;
    let stdout = child
        .stdout
        .take()
        .ok_or_else(|| "provider child has no stdout".to_string())?;

    let (sender, receiver) = channel::<String>();
    let reader = thread::spawn(move || {
        let buffered = BufReader::new(stdout);
        for line in buffered.lines() {
            match line {
                Ok(line) => {
                    // The channel is unbounded, so the reader never blocks on the controller.
                    if sender.send(line).is_err() {
                        break;
                    }
                },
                Err(_) => break,
            }
        }
    });

    Ok(ProviderSession {
        child: Some(child),
        stdin: Some(stdin),
        receiver,
        reader: Some(reader),
        next_phase: 1,
        diagnostics: Vec::new(),
    })
}

// ------------------------------------------------------------------------------------------------
// Controller side: subscription, observation and scenarios
// ------------------------------------------------------------------------------------------------

fn run_controller<R: Runtime>(runtime: &R, scenario: &str) -> AppResult<()> {
    let mut session = spawn_provider()?;

    // Offer the service before discovery; the provider starts unoffered itself.
    session.offer()?;

    let subscription = discover_and_subscribe::<R>(runtime)?;
    // Registration never promises an immediate current-state notification, so establish the
    // initial Subscribed state through the synchronous query before registering any handler.
    wait_for_state::<R, _>(&subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;

    match scenario {
        "notifications" => scenario_notifications::<R, _>(&mut session, subscription)?,
        "replacement" => scenario_replacement::<R, _>(&mut session, subscription)?,
        "unset" => scenario_unset::<R, _>(&mut session, subscription)?,
        "false-then-drop" => scenario_false_then_drop::<R, _>(&mut session, subscription)?,
        "drop-active" => scenario_drop_active::<R, _>(&mut session, runtime, subscription)?,
        other => return Err(format!("unknown scenario: {}", other)),
    }

    session.finish()?;
    eprintln!("[subscription-state-apis] scenario '{}' completed", scenario);
    Ok(())
}

fn discover_and_subscribe<R: Runtime>(runtime: &R) -> AppResult<impl Subscription<MixedPrimitivesPayload, R>> {
    let specifier = InstanceSpecifier::new(SERVICE_INSTANCE).map_err(err_str)?;
    let discovery = runtime.find_service::<MixedPrimitivesInterface>(FindServiceSpecifier::Specific(specifier));
    let deadline = deadline_after(DISCOVERY_TIMEOUT);
    let consumer = loop {
        let instances = discovery.get_available_instances().map_err(err_str)?;
        if let Some(builder) = instances.into_iter().next() {
            break builder.build().map_err(err_str)?;
        }
        if Instant::now() >= deadline {
            return Err("service discovery timeout".to_string());
        }
        thread::sleep(POLL_INTERVAL);
    };
    let subscription = consumer.mixed_event.subscribe(MAX_SAMPLES).map_err(err_str)?;
    Ok(subscription)
}

fn wait_for_state<R, S>(subscription: &S, expected: SubscriptionState, timeout: Duration) -> AppResult<()>
where
    R: Runtime,
    S: Subscription<MixedPrimitivesPayload, R>,
{
    let deadline = deadline_after(timeout);
    let mut observed = Vec::new();
    loop {
        let state = subscription.get_subscription_state();
        observed.push(state);
        if state == expected {
            return Ok(());
        }
        if Instant::now() >= deadline {
            return Err(format!(
                "timeout waiting for state {:?}, observed {:?}",
                expected, observed
            ));
        }
        thread::sleep(POLL_INTERVAL);
    }
}

fn receive_marker<R, S>(subscription: &S, marker: u32, timeout: Duration) -> AppResult<()>
where
    R: Runtime,
    S: Subscription<MixedPrimitivesPayload, R>,
{
    let deadline = deadline_after(timeout);
    let mut container = SampleContainer::new(MAX_SAMPLES);
    loop {
        let received = subscription.try_receive(&mut container, MAX_SAMPLES).map_err(err_str)?;
        if received > 0 {
            while let Some(sample) = container.pop_front() {
                if sample.u32_val == marker {
                    return Ok(());
                }
            }
        }
        if Instant::now() >= deadline {
            return Err(format!("timeout waiting for sample marker {}", marker));
        }
        thread::sleep(POLL_INTERVAL);
    }
}

/// A single handler invocation, tagged with the originating handler ID.
#[derive(Debug)]
struct Observation {
    handler_id: u32,
    state: SubscriptionState,
}

/// Resources captured by a subscription-state handler. Dropping this value records exactly one
/// disposal of the callable that owned it.
struct DisposeProbe {
    handler_id: u32,
    disposals: Arc<AtomicUsize>,
}

impl DisposeProbe {
    fn handler_id(&self) -> u32 {
        self.handler_id
    }
}

impl Drop for DisposeProbe {
    fn drop(&mut self) {
        self.disposals.fetch_add(1, Ordering::SeqCst);
    }
}

/// Test-owned view of one registered handler.
struct HandlerControl {
    id: u32,
    receiver: Receiver<Observation>,
    disposals: Arc<AtomicUsize>,
    invocations: Arc<AtomicUsize>,
    send_failures: Arc<AtomicUsize>,
}

/// Create a handler that records every invocation and always/never keeps itself registered.
///
/// The returned closure never calls back into the subscription, never blocks and never panics; a
/// failed observation send is recorded in a test-owned atomic instead.
fn make_handler(id: u32, keep: bool) -> (HandlerControl, impl FnMut(SubscriptionState) -> bool + Send + 'static) {
    let (sender, receiver) = channel::<Observation>();
    let disposals = Arc::new(AtomicUsize::new(0));
    let invocations = Arc::new(AtomicUsize::new(0));
    let send_failures = Arc::new(AtomicUsize::new(0));

    let probe = DisposeProbe {
        handler_id: id,
        disposals: Arc::clone(&disposals),
    };
    let invocations_counter = Arc::clone(&invocations);
    let send_failures_counter = Arc::clone(&send_failures);

    let handler = move |state: SubscriptionState| -> bool {
        // Referencing the probe keeps it owned by, and disposed with, this callable.
        let _ = probe.handler_id();
        invocations_counter.fetch_add(1, Ordering::SeqCst);
        let observation = Observation { handler_id: id, state };
        if sender.send(observation).is_err() {
            send_failures_counter.fetch_add(1, Ordering::SeqCst);
        }
        keep
    };

    (
        HandlerControl {
            id,
            receiver,
            disposals,
            invocations,
            send_failures,
        },
        handler,
    )
}

fn await_observation(
    control: &HandlerControl,
    expected: SubscriptionState,
    timeout: Duration,
) -> AppResult<Vec<Observation>> {
    let deadline = deadline_after(timeout);
    let mut collected = Vec::new();
    loop {
        let now = Instant::now();
        if now >= deadline {
            return Err(format!(
                "timeout awaiting {:?} observation from handler {}, collected {:?}",
                expected, control.id, collected
            ));
        }
        match control.receiver.recv_timeout(deadline - now) {
            Ok(observation) => {
                let matched = observation.handler_id == control.id && observation.state == expected;
                collected.push(observation);
                if matched {
                    return Ok(collected);
                }
            },
            Err(RecvTimeoutError::Timeout) => {
                return Err(format!(
                    "timeout awaiting {:?} observation from handler {}, collected {:?}",
                    expected, control.id, collected
                ));
            },
            Err(RecvTimeoutError::Disconnected) => {
                return Err(format!("observation channel for handler {} disconnected", control.id));
            },
        }
    }
}

fn await_disposal(control: &HandlerControl, timeout: Duration) -> AppResult<()> {
    let deadline = deadline_after(timeout);
    loop {
        if control.disposals.load(Ordering::SeqCst) >= 1 {
            return Ok(());
        }
        if Instant::now() >= deadline {
            return Err(format!("timeout awaiting disposal of handler {}", control.id));
        }
        thread::sleep(POLL_INTERVAL);
    }
}

fn require_eq(actual: usize, expected: usize, what: &str) -> AppResult<()> {
    if actual == expected {
        Ok(())
    } else {
        Err(format!("{}: expected {}, got {}", what, expected, actual))
    }
}

fn require_at_least(actual: usize, minimum: usize, what: &str) -> AppResult<()> {
    if actual >= minimum {
        Ok(())
    } else {
        Err(format!("{}: expected at least {}, got {}", what, minimum, actual))
    }
}

/// Case 1: real pending-after-withdrawal and subscribed-after-reoffer notifications.
fn scenario_notifications<R, S>(session: &mut ProviderSession, subscription: S) -> AppResult<()>
where
    R: Runtime,
    S: Subscription<MixedPrimitivesPayload, R>,
{
    let (control, handler) = make_handler(1, true);
    subscription
        .set_subscription_state_change_handler(handler)
        .map_err(err_str)?;

    session.withdraw()?;
    let pending = await_observation(&control, SubscriptionState::SubscriptionPending, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::SubscriptionPending, QUERY_TIMEOUT)?;

    session.offer()?;
    let subscribed = await_observation(&control, SubscriptionState::Subscribed, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;

    session.send_sample(SAMPLE_MARKER_NOTIFICATIONS)?;
    receive_marker::<R, S>(&subscription, SAMPLE_MARKER_NOTIFICATIONS, SAMPLE_TIMEOUT)?;

    subscription
        .unset_subscription_state_change_handler()
        .map_err(err_str)?;
    require_eq(
        control.disposals.load(Ordering::SeqCst),
        1,
        "notifications: handler disposed exactly once on unset",
    )?;
    require_at_least(
        control.invocations.load(Ordering::SeqCst),
        2,
        "notifications: handler observes pending and subscribed",
    )?;
    require_eq(
        control.send_failures.load(Ordering::SeqCst),
        0,
        "notifications: callback observations were delivered",
    )?;
    eprintln!(
        "[notifications] pending observations={:?} subscribed observations={:?}",
        pending, subscribed
    );
    drop(subscription);
    Ok(())
}

/// Case 2: setting a second handler replaces the first, disposing it exactly once.
fn scenario_replacement<R, S>(session: &mut ProviderSession, subscription: S) -> AppResult<()>
where
    R: Runtime,
    S: Subscription<MixedPrimitivesPayload, R>,
{
    let (control_a, handler_a) = make_handler(1, true);
    let (control_b, handler_b) = make_handler(2, true);

    subscription
        .set_subscription_state_change_handler(handler_a)
        .map_err(err_str)?;
    subscription
        .set_subscription_state_change_handler(handler_b)
        .map_err(err_str)?;
    require_eq(
        control_a.disposals.load(Ordering::SeqCst),
        1,
        "replacement: replaced handler A disposed once",
    )?;

    session.withdraw()?;
    await_observation(&control_b, SubscriptionState::SubscriptionPending, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::SubscriptionPending, QUERY_TIMEOUT)?;

    session.offer()?;
    await_observation(&control_b, SubscriptionState::Subscribed, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;

    require_eq(
        control_a.invocations.load(Ordering::SeqCst),
        0,
        "replacement: replaced handler A never invoked",
    )?;

    subscription
        .unset_subscription_state_change_handler()
        .map_err(err_str)?;
    require_eq(
        control_b.disposals.load(Ordering::SeqCst),
        1,
        "replacement: handler B disposed once on unset",
    )?;

    drop(subscription);
    require_eq(
        control_a.disposals.load(Ordering::SeqCst),
        1,
        "replacement: A disposal remains exactly one after drop",
    )?;
    require_eq(
        control_b.disposals.load(Ordering::SeqCst),
        1,
        "replacement: B disposal remains exactly one after drop",
    )?;
    Ok(())
}

/// Case 3: unset while subscribed fences the handler; a positive control verifies transitions.
fn scenario_unset<R, S>(session: &mut ProviderSession, subscription: S) -> AppResult<()>
where
    R: Runtime,
    S: Subscription<MixedPrimitivesPayload, R>,
{
    let (control_a, handler_a) = make_handler(1, true);
    let (control_b, handler_b) = make_handler(2, true);

    subscription
        .set_subscription_state_change_handler(handler_a)
        .map_err(err_str)?;
    subscription
        .unset_subscription_state_change_handler()
        .map_err(err_str)?;
    require_eq(
        control_a.disposals.load(Ordering::SeqCst),
        1,
        "unset: handler A disposed once on unset",
    )?;

    session.withdraw()?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::SubscriptionPending, QUERY_TIMEOUT)?;
    session.offer()?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;
    require_eq(
        control_a.invocations.load(Ordering::SeqCst),
        0,
        "unset: handler A never invoked after unset",
    )?;

    subscription
        .set_subscription_state_change_handler(handler_b)
        .map_err(err_str)?;
    session.withdraw()?;
    await_observation(&control_b, SubscriptionState::SubscriptionPending, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::SubscriptionPending, QUERY_TIMEOUT)?;
    session.offer()?;
    await_observation(&control_b, SubscriptionState::Subscribed, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;

    subscription
        .unset_subscription_state_change_handler()
        .map_err(err_str)?;
    require_eq(
        control_b.disposals.load(Ordering::SeqCst),
        1,
        "unset: handler B disposed once on unset",
    )?;
    require_at_least(
        control_b.invocations.load(Ordering::SeqCst),
        2,
        "unset: positive-control handler B observes both transitions",
    )?;
    require_eq(
        control_a.disposals.load(Ordering::SeqCst),
        1,
        "unset: handler A disposal remains exactly one",
    )?;
    drop(subscription);
    Ok(())
}

/// Case 4: a handler that returns false is unregistered and disposed exactly once.
fn scenario_false_then_drop<R, S>(session: &mut ProviderSession, subscription: S) -> AppResult<()>
where
    R: Runtime,
    S: Subscription<MixedPrimitivesPayload, R>,
{
    let (control_a, handler_a) = make_handler(1, false);
    subscription
        .set_subscription_state_change_handler(handler_a)
        .map_err(err_str)?;

    session.withdraw()?;
    await_observation(&control_a, SubscriptionState::SubscriptionPending, CALLBACK_TIMEOUT)?;
    // Receiving the callback is not a disposal fence: await the captured resource's destruction
    // and then use a synchronous query as the state-lock fence before re-offer.
    await_disposal(&control_a, DISPOSAL_TIMEOUT)?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::SubscriptionPending, QUERY_TIMEOUT)?;

    session.offer()?;
    wait_for_state::<R, S>(&subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;
    session.send_sample(SAMPLE_MARKER_FALSE_THEN_DROP)?;
    receive_marker::<R, S>(&subscription, SAMPLE_MARKER_FALSE_THEN_DROP, SAMPLE_TIMEOUT)?;
    require_eq(
        control_a.invocations.load(Ordering::SeqCst),
        1,
        "false-then-drop: handler A records exactly the first pending transition",
    )?;

    // Drop the same subscription with the still-true Rust flag: a redundant native unset followed
    // by unsubscribe must still dispose the handler exactly once.
    drop(subscription);
    require_eq(
        control_a.disposals.load(Ordering::SeqCst),
        1,
        "false-then-drop: handler A disposal exactly one after drop",
    )?;
    require_eq(
        control_a.invocations.load(Ordering::SeqCst),
        1,
        "false-then-drop: no later handler A invocation",
    )?;
    Ok(())
}

/// Case 5: dropping a subscription with an active handler disposes it once; a fresh
/// subscription with a positive-control handler verifies a full withdrawal/re-offer cycle.
fn scenario_drop_active<R, S>(session: &mut ProviderSession, runtime: &R, subscription: S) -> AppResult<()>
where
    R: Runtime,
    S: Subscription<MixedPrimitivesPayload, R>,
{
    let (control_a, handler_a) = make_handler(1, true);
    subscription
        .set_subscription_state_change_handler(handler_a)
        .map_err(err_str)?;
    drop(subscription);
    require_eq(
        control_a.disposals.load(Ordering::SeqCst),
        1,
        "drop-active: active handler A disposed once on subscription drop",
    )?;
    require_eq(
        control_a.invocations.load(Ordering::SeqCst),
        0,
        "drop-active: handler A observes no callback",
    )?;

    let fresh_subscription = discover_and_subscribe::<R>(runtime)?;
    wait_for_state::<R, _>(&fresh_subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;

    let (control_b, handler_b) = make_handler(2, true);
    fresh_subscription
        .set_subscription_state_change_handler(handler_b)
        .map_err(err_str)?;

    session.withdraw()?;
    await_observation(&control_b, SubscriptionState::SubscriptionPending, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, _>(
        &fresh_subscription,
        SubscriptionState::SubscriptionPending,
        QUERY_TIMEOUT,
    )?;
    session.offer()?;
    await_observation(&control_b, SubscriptionState::Subscribed, CALLBACK_TIMEOUT)?;
    wait_for_state::<R, _>(&fresh_subscription, SubscriptionState::Subscribed, QUERY_TIMEOUT)?;

    fresh_subscription
        .unset_subscription_state_change_handler()
        .map_err(err_str)?;
    require_eq(
        control_b.disposals.load(Ordering::SeqCst),
        1,
        "drop-active: positive-control handler B disposed once",
    )?;
    require_at_least(
        control_b.invocations.load(Ordering::SeqCst),
        2,
        "drop-active: handler B observes both transitions",
    )?;
    drop(fresh_subscription);
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    // These subprocess tests cover controller cleanup only. The five integration scenarios
    // continue to require the production LoLa provider and do not use these protocol stubs.
    fn scripted_provider(script: &str) -> ProviderSession {
        let child = Command::new("/bin/sh")
            .arg("-c")
            .arg(script)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::inherit())
            .spawn()
            .expect("scripted provider must start");
        provider_session_from_child(child).expect("scripted provider pipes must be available")
    }

    #[test]
    fn provider_success_after_finish_is_accepted() {
        let mut session = scripted_provider("read -r line; printf 'SSAPI-PROTO 1 FINISH OK\\n'; exit 0");
        assert!(session.finish().is_ok());
        assert!(session.child.is_none());
    }

    #[test]
    fn provider_failure_after_finish_is_rejected() {
        let mut session = scripted_provider("read -r line; printf 'SSAPI-PROTO 1 FINISH OK\\n'; exit 7");
        let error = session
            .finish()
            .expect_err("a FINISH acknowledgement cannot hide a failed exit");
        assert!(error.contains("exited unsuccessfully"), "{error}");
        assert!(session.child.is_none(), "the exited child must already be reaped");
    }

    #[test]
    fn provider_wait_error_preserves_cleanup_and_reaps_live_child() {
        // exec avoids a grandchild inheriting stdout: the child PID itself remains alive until
        // session Drop terminates it. The error is injected only after the FINISH acknowledgement.
        let mut session = scripted_provider("read -r line; printf 'SSAPI-PROTO 1 FINISH OK\\n'; exec sleep 60");
        let pid = session.child.as_ref().expect("owned child").id();
        let error = session
            .finish_with_wait(|_| Err(std::io::Error::other("injected wait error")))
            .expect_err("wait errors must propagate");
        assert!(error.contains("injected wait error"), "{error}");
        assert!(session.child.is_some(), "wait error must preserve cleanup ownership");
        assert!(session
            .child
            .as_mut()
            .expect("owned child")
            .try_wait()
            .expect("real wait")
            .is_none());
        drop(session);
        assert!(
            !Path::new(&format!("/proc/{pid}")).exists(),
            "the owned child must be reaped"
        );
    }
}
