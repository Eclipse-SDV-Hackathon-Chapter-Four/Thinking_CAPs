// SPDX-License-Identifier: Apache-2.0
//! `CruiseLink` over the S-CORE path: talks to `cruise_bridge` (demo/score), which
//! holds the mw::com side of link ④. The bridge is built with S-CORE's Bazel
//! toolchain, this gateway with Cargo, so they meet over a local TCP line protocol:
//!   bridge → us   {"type":"status","speed":99.8,"set_speed":100.0,"state":"active","seq":7}
//!   us → bridge   inject 1 | inject 0

use cruise_diag::{CruiseLink, CruiseState, CruiseStatus};
use std::io::{BufRead, BufReader, Write};
use std::net::TcpStream;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

#[derive(Default)]
pub struct BridgeLink {
    latest: Mutex<Option<(CruiseStatus, Instant)>>,
    writer: Mutex<Option<TcpStream>>,
    inject: AtomicBool,
}

fn parse(line: &str) -> Option<CruiseStatus> {
    let v: serde_json::Value = serde_json::from_str(line).ok()?;
    if v["type"] != "status" {
        return None;
    }
    let state = match v["state"].as_str()? {
        "standby" => CruiseState::Standby,
        "active" => CruiseState::Active,
        "unavailable" => CruiseState::Unavailable,
        _ => return None,
    };
    Some(CruiseStatus {
        speed_kmh: v["speed"].as_f64()?,
        state,
        set_speed_kmh: v["set_speed"].as_f64(),
    })
}

impl BridgeLink {
    fn send(&self, stuck: bool) {
        if let Ok(mut w) = self.writer.lock() {
            if let Some(stream) = w.as_mut() {
                if writeln!(stream, "inject {}", u8::from(stuck)).is_err() {
                    *w = None;
                }
            }
        }
    }

    fn session(&self, addr: &str) -> std::io::Result<()> {
        let stream = TcpStream::connect(addr)?;
        stream.set_nodelay(true)?;
        *self.writer.lock().map_err(|_| std::io::ErrorKind::Other)? = Some(stream.try_clone()?);
        eprintln!("[bridge_link] connected to cruise_bridge at {addr}");
        // The bridge keeps the value it last got; restate ours after a reconnect.
        self.send(self.inject.load(Ordering::SeqCst));
        for line in BufReader::new(stream).lines() {
            if let Some(status) = parse(&line?) {
                if let Ok(mut l) = self.latest.lock() {
                    *l = Some((status, Instant::now()));
                }
            }
        }
        Ok(())
    }
}

impl CruiseLink for BridgeLink {
    fn latest(&self) -> Option<(CruiseStatus, Instant)> {
        self.latest.lock().ok().and_then(|l| *l)
    }

    fn publish_inject_fault(&self, stuck: bool) {
        self.inject.store(stuck, Ordering::SeqCst);
        self.send(stuck);
    }
}

/// Connects to the bridge on a background thread and reconnects when it goes away.
pub fn spawn(addr: String) -> Arc<BridgeLink> {
    let link = Arc::new(BridgeLink::default());
    let worker = link.clone();
    thread::Builder::new()
        .name("bridge-link".into())
        .spawn(move || loop {
            if let Err(e) = worker.session(&addr) {
                eprintln!("[bridge_link] {addr}: {e}; retrying");
            }
            if let Ok(mut w) = worker.writer.lock() {
                *w = None;
            }
            thread::sleep(Duration::from_millis(500));
        })
        .expect("spawn bridge-link thread");
    link
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::net::TcpListener;

    #[test]
    fn parses_status_lines() {
        let s = parse(r#"{"type":"status","speed":99.8,"set_speed":100.0,"state":"active","seq":7}"#).unwrap();
        assert_eq!(s.state, CruiseState::Active);
        assert_eq!(s.speed_kmh, 99.8);
        assert_eq!(s.set_speed_kmh, Some(100.0));
        let s = parse(r#"{"type":"status","speed":99.8,"set_speed":null,"state":"unavailable","seq":8}"#).unwrap();
        assert_eq!(s.set_speed_kmh, None);
        assert!(parse(r#"{"type":"stats"}"#).is_none());
        assert!(parse("garbage").is_none());
    }

    #[test]
    fn talks_the_bridge_protocol() {
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let addr = listener.local_addr().unwrap().to_string();
        let fake_bridge = thread::spawn(move || {
            let (mut s, _) = listener.accept().unwrap();
            let mut r = BufReader::new(s.try_clone().unwrap());
            let mut line = String::new();
            r.read_line(&mut line).unwrap();
            assert_eq!(line.trim(), "inject 0", "link restates its value on connect");
            writeln!(s, r#"{{"type":"status","speed":42.5,"set_speed":null,"state":"standby","seq":1}}"#).unwrap();
            line.clear();
            r.read_line(&mut line).unwrap();
            line
        });
        let link = spawn(addr);
        for _ in 0..100 {
            if link.latest().is_some() {
                break;
            }
            thread::sleep(Duration::from_millis(10));
        }
        assert_eq!(link.latest().unwrap().0.speed_kmh, 42.5);
        link.publish_inject_fault(true);
        assert_eq!(fake_bridge.join().unwrap().trim(), "inject 1");
    }
}
