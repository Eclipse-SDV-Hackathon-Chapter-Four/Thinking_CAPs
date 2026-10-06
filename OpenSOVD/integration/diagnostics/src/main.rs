use async_trait::async_trait;
use opensovd_core::{App, Component};
use opensovd_models::data::DataCategory;
use opensovd_providers::data::{DataProviderBuilder, ReadableDataResource, Value};
use opensovd_server::{Server, Topology};
use sdv_receiver_diagnostics::{Budgets, Cache, DiagnosticView, Observation, monotonic_ns};
use std::os::unix::fs::{MetadataExt, PermissionsExt};
use std::path::PathBuf;
use std::sync::{Arc, RwLock};
use tokio::net::{TcpListener, UnixDatagram};

struct ReceiverResource(Arc<RwLock<Cache>>);

#[cfg(feature = "fault-lifecycle")]
struct FaultResource(Arc<RwLock<sdv_receiver_diagnostics::faults::FaultView>>);
#[cfg(feature = "fault-lifecycle")]
#[async_trait]
impl ReadableDataResource for FaultResource {
    type Value = Value<sdv_receiver_diagnostics::faults::FaultView>;
    async fn read(&self) -> Result<Self::Value, opensovd_core::DataError> {
        Ok(Value::new(
            self.0
                .read()
                .unwrap_or_else(|p| p.into_inner())
                .view(monotonic_ns()),
        ))
    }
}

#[async_trait]
impl ReadableDataResource for ReceiverResource {
    type Value = Value<DiagnosticView>;
    async fn read(&self) -> Result<Self::Value, opensovd_core::DataError> {
        Ok(Value::new(
            self.0
                .read()
                .unwrap_or_else(|poisoned| poisoned.into_inner())
                .view(monotonic_ns()),
        ))
    }
}

struct SocketCleanup {
    path: PathBuf,
    inode: u64,
}
impl Drop for SocketCleanup {
    fn drop(&mut self) {
        if std::fs::symlink_metadata(&self.path).is_ok_and(|metadata| metadata.ino() == self.inode)
        {
            let _ = std::fs::remove_file(&self.path);
        }
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Native IPC initializes process-wide handlers lazily. Initialize it before
    // installing this application's handlers; later native nodes reuse the
    // singleton and cannot displace Tokio's SIGINT/SIGTERM streams.
    #[cfg(feature = "fault-lifecycle")]
    let _ = iceoryx2_bb_posix::signal::SignalHandler::last_signal();
    let mut interrupt = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::interrupt())?;
    let mut terminate = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())?;
    let mut args = std::env::args().skip(1);
    let mut socket = None;
    let mut base_uri = "http://127.0.0.1:7691/sovd".to_owned();
    let mut listen = "127.0.0.1:7691".to_owned();
    let mut speed_ms: u64 = 1000;
    let mut heartbeat_ms: u64 = 500;
    let mut fault_storage = None;
    let mut startup_ms: u64 = 2000;
    let mut debounce_ms: u64 = 100;
    let mut recovery_ms: u64 = 150;
    let mut poll_ms: u64 = 25;
    let mut query_ms: u64 = 50;
    while let Some(flag) = args.next() {
        let value = args.next().ok_or("each option requires a value")?;
        match flag.as_str() {
            "--socket" => socket = Some(PathBuf::from(value)),
            "--base-uri" => base_uri = value,
            "--listen" => listen = value,
            "--speed-timeout-ms" => speed_ms = value.parse()?,
            "--heartbeat-timeout-ms" => heartbeat_ms = value.parse()?,
            "--fault-storage" => fault_storage = Some(PathBuf::from(value)),
            "--startup-grace-ms" => startup_ms = value.parse()?,
            "--failure-debounce-ms" => debounce_ms = value.parse()?,
            "--recovery-hold-ms" => recovery_ms = value.parse()?,
            "--monitor-poll-ms" => poll_ms = value.parse()?,
            "--fault-query-ms" => query_ms = value.parse()?,
            _ => return Err(format!("unknown option {flag}").into()),
        }
    }
    if speed_ms == 0 || heartbeat_ms == 0 {
        return Err("budgets must be positive".into());
    }
    let budgets = Budgets {
        speed_ns: speed_ms
            .checked_mul(1_000_000)
            .ok_or("speed budget overflow")?,
        heartbeat_ns: heartbeat_ms
            .checked_mul(1_000_000)
            .ok_or("heartbeat budget overflow")?,
    };
    let socket = socket.ok_or("--socket is required; existing sockets are never removed")?;
    let datagrams = UnixDatagram::bind(&socket)?;
    let _cleanup = SocketCleanup {
        path: socket.clone(),
        inode: std::fs::symlink_metadata(&socket)?.ino(),
    };
    std::fs::set_permissions(&socket, std::fs::Permissions::from_mode(0o600))?;
    let boot_id = std::fs::read_to_string("/proc/sys/kernel/random/boot_id")?
        .trim()
        .to_owned();
    let cache = Arc::new(RwLock::new(Cache::new(boot_id, budgets)));
    let nanos = |ms: u64| ms.checked_mul(1_000_000).ok_or("policy budget overflow");
    let policy = sdv_receiver_diagnostics::monitor::Policy {
        timeout_ns: budgets.speed_ns,
        startup_grace_ns: nanos(startup_ms)?,
        failure_debounce_ns: nanos(debounce_ms)?,
        recovery_hold_ns: nanos(recovery_ms)?,
        poll_ns: nanos(poll_ms)?,
        query_ns: nanos(query_ms)?,
    };
    sdv_receiver_diagnostics::monitor::Monitor::new(policy)?;
    #[cfg(not(feature = "fault-lifecycle"))]
    if fault_storage.is_some() {
        return Err("--fault-storage requires the fault-lifecycle feature and exported upstream storage patch".into());
    }
    #[cfg(feature = "fault-lifecycle")]
    let fault_runtime = match fault_storage {
        Some(directory) => {
            std::fs::create_dir_all(&directory)?;
            std::fs::set_permissions(&directory, std::fs::Permissions::from_mode(0o700))?;
            Some(sdv_receiver_diagnostics::faults::FaultRuntime::start(
                directory,
                Arc::clone(&cache),
                policy,
            )?)
        }
        None => None,
    };
    let receiving_cache = Arc::clone(&cache);
    let receiver = tokio::spawn(async move {
        let mut bytes = [0u8; 4097];
        loop {
            let count = match datagrams.recv(&mut bytes).await {
                Ok(count) => count,
                Err(_) => break,
            };
            let parsed = if count > 4096 {
                None
            } else {
                serde_json::from_slice::<Observation>(&bytes[..count]).ok()
            };
            let mut cache = receiving_cache
                .write()
                .unwrap_or_else(|poisoned| poisoned.into_inner());
            match parsed {
                Some(obs) => {
                    let _ = cache.accept(obs, monotonic_ns());
                }
                None => cache.reject_datagram(),
            }
        }
    });
    let provider = DataProviderBuilder::new().read_data(
        "cc.observation",
        "Receiving-side Cruise Control observation",
        &DataCategory::CurrentData,
        ReceiverResource(cache),
    );
    #[cfg(feature = "fault-lifecycle")]
    let provider = match &fault_runtime {
        Some(runtime) => provider.read_data(
            "cc.fault-history",
            "Native DFM fault evidence (data fallback)",
            &DataCategory::CurrentData,
            FaultResource(Arc::clone(&runtime.cache)),
        ),
        None => provider,
    };
    let provider = provider.build()?;
    let topology = Topology::new();
    {
        let mut topology = topology.write().await;
        topology.add_component(Component::new("score-host", "S-CORE target"));
        topology.add_app(
            App::new("cruise-control", "Cruise Control")
                .with_component_id("score-host")
                .with_data_provider(provider),
        );
    }
    let listener = TcpListener::bind(&listen).await?;
    let server = Server::builder()
        .base_uri(base_uri)?
        .listener(listener)
        .topology(topology)
        .build()?;
    eprintln!(
        "receiver diagnostics listening at {listen}; budgets are provisional; native faults unavailable"
    );
    tokio::select! {
        result = server.serve() => result?,
        _ = interrupt.recv() => {},
        _ = terminate.recv() => {},
    }
    receiver.abort();
    Ok(())
}
