// SPDX-License-Identifier: Apache-2.0
//! cruise_bridge: the mw::com end of link ④ on the vehicle computer.
//!
//! - consumes `sdv/cruise_status` (offered by gatewayd, mirrored from the
//!   cruise control app's SOME/IP event) and keeps the latest value;
//! - offers `sdv/diag_injection` and publishes `inject_fault`, which gatewayd
//!   forwards to the cruise control app over SOME/IP;
//! - serves the SOVD gateway (built with Cargo, outside S-CORE's Bazel world)
//!   over a local TCP line protocol:
//!     bridge → gateway  {"type":"status","speed":99.8,"set_speed":100.0,"state":"active","seq":7}
//!     gateway → bridge  inject 1 | inject 0 | stats
//!
//! Usage: cruise_bridge [--config etc/mw_com_config.json] [--listen 0.0.0.0:7700] [--stats FILE]

use cruise_api::{CruiseStatus, InjectFaultSample, SdvCruiseStatusInterface, SdvDiagInjectionInterface};
use score_com::{
    Builder, FindServiceSpecifier, InstanceSpecifier, LolaRuntimeBuilderImpl, Producer, Publisher, Runtime,
    RuntimeBuilder, SampleContainer, SampleMaybeUninit, SampleMut, ServiceDiscovery, Subscriber, Subscription,
};
use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::path::Path;
use std::sync::atomic::{AtomicBool, AtomicU64, AtomicUsize, Ordering};
use std::sync::mpsc::{self, Receiver, Sender};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant, SystemTime, UNIX_EPOCH};

const STATUS_SPECIFIER: &str = "/sdv/cruise_status";
const INJECTION_SPECIFIER: &str = "/sdv/diag_injection";
const TICK: Duration = Duration::from_millis(20);
const REPUBLISH: Duration = Duration::from_millis(500);

#[derive(Default)]
struct Shared {
    latest: Mutex<Option<(CruiseStatus, u64)>>, // status, sequence number
    seq: AtomicU64,
    samples: AtomicU64,
    injects: AtomicU64,
    inject: AtomicBool,
    subscribed: AtomicBool,
    offered: AtomicBool,
    clients: AtomicUsize,
    last_sample_ms: AtomicU64, // unix ms of the last sample
}

fn unix_ms() -> u64 {
    SystemTime::now().duration_since(UNIX_EPOCH).map(|d| d.as_millis() as u64).unwrap_or(0)
}

fn status_json(s: &CruiseStatus, seq: u64) -> String {
    let set = s.set_speed_kmh.map_or("null".to_string(), |v| format!("{v:.1}"));
    format!(
        "{{\"type\":\"status\",\"speed\":{:.1},\"set_speed\":{},\"state\":\"{}\",\"seq\":{}}}",
        s.speed_kmh,
        set,
        s.state.as_str(),
        seq
    )
}

fn stats_json(sh: &Shared) -> String {
    let last = sh.last_sample_ms.load(Ordering::Relaxed);
    let age = if last == 0 { "null".to_string() } else { unix_ms().saturating_sub(last).to_string() };
    let latest = sh
        .latest
        .lock()
        .ok()
        .and_then(|l| l.map(|(s, seq)| status_json(&s, seq)))
        .unwrap_or_else(|| "null".to_string());
    format!(
        "{{\"type\":\"stats\",\"subscribed\":{},\"offered\":{},\"samples_received\":{},\"injects_published\":{},\
\"inject\":{},\"clients\":{},\"last_sample_age_ms\":{},\"latest\":{},\"at_ms\":{}}}",
        sh.subscribed.load(Ordering::Relaxed),
        sh.offered.load(Ordering::Relaxed),
        sh.samples.load(Ordering::Relaxed),
        sh.injects.load(Ordering::Relaxed),
        sh.inject.load(Ordering::Relaxed),
        sh.clients.load(Ordering::Relaxed),
        age,
        latest,
        unix_ms()
    )
}

/// One SOVD gateway connection: push every new status, accept commands.
fn serve_client(stream: TcpStream, sh: Arc<Shared>, tx: Sender<bool>) {
    let peer = stream.peer_addr().map(|a| a.to_string()).unwrap_or_default();
    println!("[cruise_bridge] client {peer} connected");
    sh.clients.fetch_add(1, Ordering::Relaxed);
    let reader_stream = match stream.try_clone() {
        Ok(s) => s,
        Err(_) => return,
    };
    let (rtx, rsh) = (tx, sh.clone());
    let mut writer = stream.try_clone().ok();
    thread::spawn(move || {
        for line in BufReader::new(reader_stream).lines() {
            let Ok(line) = line else { break };
            match line.trim() {
                "inject 1" => {
                    let _ = rtx.send(true);
                }
                "inject 0" => {
                    let _ = rtx.send(false);
                }
                "stats" => {
                    if let Some(w) = writer.as_mut() {
                        let _ = writeln!(w, "{}", stats_json(&rsh));
                    }
                }
                other => eprintln!("[cruise_bridge] ignored command {other:?}"),
            }
        }
    });
    let mut stream = stream;
    let mut sent = 0;
    loop {
        let current = sh.latest.lock().ok().and_then(|l| *l);
        if let Some((s, seq)) = current {
            if seq != sent {
                if writeln!(stream, "{}", status_json(&s, seq)).is_err() {
                    break;
                }
                sent = seq;
            }
        }
        thread::sleep(TICK);
    }
    sh.clients.fetch_sub(1, Ordering::Relaxed);
    println!("[cruise_bridge] client {peer} disconnected");
}

fn listen(addr: String, sh: Arc<Shared>, tx: Sender<bool>) {
    let listener = TcpListener::bind(&addr).unwrap_or_else(|e| panic!("bind {addr}: {e}"));
    println!("[cruise_bridge] listening on {addr}");
    for stream in listener.incoming().flatten() {
        let (sh, tx) = (sh.clone(), tx.clone());
        thread::spawn(move || serve_client(stream, sh, tx));
    }
}

fn write_stats(path: &Option<String>, sh: &Shared) {
    if let Some(p) = path {
        let tmp = format!("{p}.tmp");
        if std::fs::write(&tmp, stats_json(sh)).is_ok() {
            let _ = std::fs::rename(&tmp, p);
        }
    }
}

fn run<R: Runtime>(runtime: &R, sh: Arc<Shared>, rx: Receiver<bool>, stats_path: Option<String>) {
    // Offer inject_fault first: gatewayd searches for it and forwards it to SOME/IP.
    let spec = InstanceSpecifier::new(INJECTION_SPECIFIER).expect("injection specifier");
    let producer = runtime.producer_builder::<SdvDiagInjectionInterface>(spec).build().expect("build producer");
    let offered = producer.offer().expect("offer sdv/diag_injection");
    sh.offered.store(true, Ordering::Relaxed);
    println!("[cruise_bridge] offered {INJECTION_SPECIFIER}");

    let publish = |stuck: bool| {
        match offered.inject_fault_.allocate() {
            Ok(uninit) => {
                if let Err(e) = uninit.write(InjectFaultSample::new(stuck)).send() {
                    eprintln!("[cruise_bridge] send inject_fault failed: {e:?}");
                }
            }
            Err(e) => eprintln!("[cruise_bridge] allocate inject_fault failed: {e:?}"),
        }
    };

    let mut last_publish = Instant::now() - REPUBLISH;
    let mut last_stats = Instant::now();
    // Publishes inject_fault on change and every REPUBLISH, and writes the stats file.
    let mut housekeeping = || {
        let mut changed = false;
        while let Ok(stuck) = rx.try_recv() {
            if sh.inject.swap(stuck, Ordering::Relaxed) != stuck {
                println!("[cruise_bridge] inject_fault = {stuck}");
            }
            changed = true;
        }
        if changed || last_publish.elapsed() >= REPUBLISH {
            publish(sh.inject.load(Ordering::Relaxed));
            sh.injects.fetch_add(1, Ordering::Relaxed);
            last_publish = Instant::now();
        }
        if last_stats.elapsed() >= Duration::from_millis(500) {
            write_stats(&stats_path, &sh);
            last_stats = Instant::now();
        }
    };

    // Phase 1: wait until gatewayd offers cruise_status (the cruise ECU is up), then subscribe.
    let spec = InstanceSpecifier::new(STATUS_SPECIFIER).expect("status specifier");
    let discovery = runtime.find_service::<SdvCruiseStatusInterface>(FindServiceSpecifier::Specific(spec));
    let mut last_search = Instant::now() - Duration::from_secs(1);
    let subscription = loop {
        if last_search.elapsed() >= Duration::from_millis(500) {
            last_search = Instant::now();
            if let Some(builder) = discovery.get_available_instances().ok().and_then(|i| i.into_iter().next()) {
                match builder.build().and_then(|c| c.cruise_status_.subscribe(8)) {
                    Ok(sub) => break sub,
                    Err(e) => eprintln!("[cruise_bridge] subscribe failed: {e:?}"),
                }
            }
        }
        housekeeping();
        thread::sleep(TICK);
    };
    println!("[cruise_bridge] subscribed to {STATUS_SPECIFIER}");
    sh.subscribed.store(true, Ordering::Relaxed);

    // Phase 2: receive status samples.
    let mut samples = SampleContainer::new(8);
    loop {
        match subscription.try_receive(&mut samples, 8) {
            Ok(n) => {
                for _ in 0..n {
                    let Some(sample) = samples.pop_front() else { break };
                    if let Some(status) = CruiseStatus::decode(sample.payload()) {
                        let seq = sh.seq.fetch_add(1, Ordering::Relaxed) + 1;
                        if let Ok(mut l) = sh.latest.lock() {
                            *l = Some((status, seq));
                        }
                        sh.samples.fetch_add(1, Ordering::Relaxed);
                        sh.last_sample_ms.store(unix_ms(), Ordering::Relaxed);
                    }
                }
            }
            Err(e) => eprintln!("[cruise_bridge] receive failed: {e:?}"),
        }
        housekeeping();
        thread::sleep(TICK);
    }
}

fn arg(args: &[String], name: &str, default: Option<&str>) -> Option<String> {
    args.iter()
        .position(|a| a == name)
        .and_then(|i| args.get(i + 1).cloned())
        .or_else(|| default.map(str::to_string))
}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let config = arg(&args, "--config", Some("etc/mw_com_config.json")).unwrap_or_default();
    let listen_addr = arg(&args, "--listen", Some("0.0.0.0:7700")).unwrap_or_default();
    let stats_path = arg(&args, "--stats", None);

    let sh = Arc::new(Shared::default());
    let (tx, rx) = mpsc::channel();
    {
        let sh = sh.clone();
        thread::spawn(move || listen(listen_addr, sh, tx));
    }

    let mut builder: LolaRuntimeBuilderImpl = LolaRuntimeBuilderImpl::new();
    builder.load_config(Path::new(&config));
    let runtime = builder.build().expect("build LoLa runtime");
    println!("[cruise_bridge] mw::com runtime up ({config})");
    run(&runtime, sh, rx, stats_path);
}
