// SPDX-License-Identifier: Apache-2.0
//! Demo gateway for the cruise control: opensovd_server → sovd_adapter →
//! cruise diag → CruiseLink. The link is either
//!   CRUISE_LINK=sim     (default) the stand-in cruise control app in process, or
//!   CRUISE_LINK=bridge  the S-CORE path: cruise_bridge (mw::com) → gatewayd → someipd →
//!                       SOME/IP → cruise control ECU, see demo/score/.
//!
//! Environment:
//!   SCORE_GATEWAY_ADDRESS        listen address, default 127.0.0.1:7690
//!   CRUISE_BRIDGE_ADDR           cruise_bridge address for CRUISE_LINK=bridge, default 127.0.0.1:7700
//!   CRUISE_DEBOUNCE_FAILED_MS    cruise diag: stuck must hold this long, default 5000
//!   CRUISE_DEBOUNCE_PASSED_MS    cruise diag: healthy must hold this long, default 2000
//!   CRUISE_SIM_FAULT_MS          stand-in app: frozen signal until unavailable, default 5000
//!   CRUISE_SIM_RESUME_MS         stand-in app: driver resumes this long after repair, default 3000, 0 = never
//!   CRUISE_SIM_PERIOD_MS         stand-in app: status event period, default 100

use cruise_diag::{CruiseDiag, CruiseLink, TimeBased};
use opensovd_core::Component;
use opensovd_server::{Server, Topology};
use sovd_adapter::{DataResourceRegistry, SovdDataProvider};
use std::sync::Arc;
use std::time::Duration;
use tokio::net::TcpListener;

mod bridge_link;

const DEFAULT_ADDRESS: &str = "127.0.0.1:7690";

fn millis_from_env(name: &str, default: u64) -> Duration {
    Duration::from_millis(std::env::var(name).ok().and_then(|v| v.parse().ok()).unwrap_or(default))
}

async fn topology(link: Arc<dyn CruiseLink>, debounce: TimeBased) -> Result<Topology, Box<dyn std::error::Error>> {
    let mut registry = DataResourceRegistry::new();
    CruiseDiag::new(link, debounce).register(&mut registry)?;
    let topology = Topology::new();
    topology
        .write()
        .await
        .add_component(Component::new("cruise", "Cruise control").with_data_provider(SovdDataProvider::new(registry)));
    Ok(topology)
}

#[tokio::main(flavor = "current_thread")]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let address = std::env::var("SCORE_GATEWAY_ADDRESS").unwrap_or_else(|_| DEFAULT_ADDRESS.to_owned());
    let listener = TcpListener::bind(&address).await?;
    let link: Arc<dyn CruiseLink> = match std::env::var("CRUISE_LINK").as_deref() {
        Ok("bridge") => {
            let addr = std::env::var("CRUISE_BRIDGE_ADDR").unwrap_or_else(|_| "127.0.0.1:7700".to_owned());
            eprintln!("cruise link: S-CORE path via cruise_bridge at {addr}");
            bridge_link::spawn(addr)
        }
        Ok("sim") | Err(_) => {
            eprintln!("cruise link: stand-in cruise control app in process");
            cruise_sim::spawn(
                millis_from_env("CRUISE_SIM_FAULT_MS", 5000),
                Some(millis_from_env("CRUISE_SIM_RESUME_MS", 3000)).filter(|d| !d.is_zero()),
                millis_from_env("CRUISE_SIM_PERIOD_MS", 100),
            )
        }
        Ok(other) => return Err(format!("CRUISE_LINK must be sim or bridge, not {other}").into()),
    };
    let debounce = TimeBased {
        failed_duration: millis_from_env("CRUISE_DEBOUNCE_FAILED_MS", 5000),
        passed_duration: millis_from_env("CRUISE_DEBOUNCE_PASSED_MS", 2000),
    };
    let server = Server::builder()
        .base_uri(format!("http://{address}/sovd"))?
        .listener(listener)
        .topology(topology(link, debounce).await?)
        .build()?;
    server.serve().await?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use opensovd_client::Client;
    use tokio::time::sleep;

    const MS: Duration = Duration::from_millis(1);

    /// Starts the gateway with a fast stand-in app on an ephemeral port.
    async fn start() -> Client {
        let listener = TcpListener::bind("127.0.0.1:0").await.expect("listener");
        let address = listener.local_addr().expect("local address");
        let link = cruise_sim::spawn(200 * MS, None, 10 * MS);
        let debounce = TimeBased {
            failed_duration: 200 * MS,
            passed_duration: 100 * MS,
        };
        let server = Server::builder()
            .base_uri(format!("http://{address}/sovd"))
            .expect("base URI")
            .listener(listener)
            .topology(topology(link, debounce).await.expect("topology"))
            .build()
            .expect("server");
        tokio::spawn(async move { server.serve().await.expect("server task") });

        let client = Client::connect(&format!("http://{address}/sovd/v1")).expect("client");
        for _ in 0..40 {
            if client.list_components().send().await.is_ok() {
                sleep(30 * MS).await; // first status event
                return client;
            }
            sleep(25 * MS).await;
        }
        panic!("gateway did not become reachable");
    }

    async fn field(client: &Client, id: &str, key: &str) -> serde_json::Value {
        let reply = client.component("cruise").data(id).read().send().await.expect(id);
        reply.data[key].clone()
    }

    async fn stuck(client: &Client, on: bool) {
        client
            .component("cruise")
            .data("speed_sensor_stuck")
            .write(&serde_json::json!({ "stuck": on }))
            .expect("body")
            .send()
            .await
            .expect("write");
    }

    #[tokio::test(flavor = "current_thread")]
    async fn serves_the_four_cruise_resources() {
        let client = start().await;
        let components = client.list_components().send().await.expect("components");
        let ids: Vec<_> = components.data.items.iter().map(|c| c.id.as_str()).collect();
        assert_eq!(ids, ["cruise"]);
        let data = client.component("cruise").list_data().send().await.expect("data list");
        let ids: Vec<_> = data.data.items.iter().map(|m| m.id.as_str()).collect();
        assert_eq!(
            ids,
            ["vehicle_speed", "cruise_state", "speed_sensor_fault_status", "speed_sensor_stuck"]
        );
    }

    #[tokio::test(flavor = "current_thread")]
    async fn scenes_one_to_four() {
        let client = start().await;
        assert_eq!(field(&client, "cruise_state", "state").await, "active");
        assert_eq!(field(&client, "speed_sensor_fault_status", "status").await, "passed");

        stuck(&client, true).await;
        assert_eq!(field(&client, "speed_sensor_fault_status", "status").await, "prefailed");
        sleep(260 * MS).await;
        assert_eq!(field(&client, "speed_sensor_fault_status", "status").await, "failed");
        assert_eq!(field(&client, "cruise_state", "state").await, "unavailable");
        let a = field(&client, "vehicle_speed", "value").await;
        sleep(60 * MS).await;
        assert_eq!(field(&client, "vehicle_speed", "value").await, a, "speed is frozen");

        stuck(&client, false).await;
        assert_eq!(field(&client, "speed_sensor_fault_status", "status").await, "prepassed");
        sleep(150 * MS).await;
        assert_eq!(field(&client, "speed_sensor_fault_status", "status").await, "passed");
        assert_eq!(field(&client, "cruise_state", "state").await, "standby");
    }

    #[tokio::test(flavor = "current_thread")]
    async fn read_only_resource_rejects_writes() {
        let client = start().await;
        let result = client
            .component("cruise")
            .data("cruise_state")
            .write(&serde_json::json!(1))
            .expect("body")
            .send()
            .await;
        assert!(result.is_err());
    }
}
