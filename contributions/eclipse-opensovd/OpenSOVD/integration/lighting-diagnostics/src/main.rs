use async_trait::async_trait;
use opensovd_core::{App, Component};
use opensovd_models::data::DataCategory;
use opensovd_providers::data::{DataProviderBuilder, ReadableDataResource, Value};
use opensovd_server::{Server, Topology};
use serde_json::{Value as Json, json};
use std::path::PathBuf;
use tokio::net::TcpListener;

struct LightingResource {
    path: PathBuf,
    history: bool,
}

#[async_trait]
impl ReadableDataResource for LightingResource {
    type Value = Value<Json>;
    async fn read(&self) -> Result<Self::Value, opensovd_core::DataError> {
        let mut view: Json = std::fs::read(&self.path)
            .ok()
            .and_then(|data| serde_json::from_slice(&data).ok())
            .unwrap_or_else(|| json!({"controller_state": "unknown", "lights": null}));
        let boot = std::fs::read_to_string("/proc/sys/kernel/random/boot_id").unwrap_or_default();
        let mut ts = libc::timespec {
            tv_sec: 0,
            tv_nsec: 0,
        };
        let clock_ok = unsafe { libc::clock_gettime(libc::CLOCK_MONOTONIC, &mut ts) } == 0;
        let now = ts.tv_sec as u64 * 1_000_000_000 + ts.tv_nsec as u64;
        let age = view["observed_at_monotonic_ns"]
            .as_u64()
            .and_then(|stamp| now.checked_sub(stamp));
        if !clock_ok
            || view["boot_id"].as_str() != Some(boot.trim())
            || age.is_none_or(|a| a > 3_000_000_000)
        {
            view["controller_state"] = json!("unavailable");
            view["lights"] = Json::Null;
        }
        view["assessment_source"] =
            json!("actual ThreadX process observations; integration-owned journal");
        view["native_dfm_faults"] = json!(false);
        if self.history {
            view = json!({"active_faults": view["active_faults"], "history": view["fault_history"],
                          "controller_state": view["controller_state"],
                          "assessment_source": view["assessment_source"], "native_dfm_faults": false});
        }
        Ok(Value::new(view))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut args = std::env::args().skip(1);
    let mut state = None;
    let mut listen = "127.0.0.1:7692".to_owned();
    let mut base = "http://127.0.0.1:7692/sovd".to_owned();
    while let Some(flag) = args.next() {
        let value = args.next().ok_or("option requires a value")?;
        match flag.as_str() {
            "--state" => state = Some(PathBuf::from(value)),
            "--listen" => listen = value,
            "--base-uri" => base = value,
            _ => return Err(format!("unknown option {flag}").into()),
        }
    }
    let state = state.ok_or("--state is required")?;
    let provider = DataProviderBuilder::new()
        .read_data(
            "lighting.observation",
            "ThreadX zonal lighting observation",
            &DataCategory::CurrentData,
            LightingResource {
                path: state.clone(),
                history: false,
            },
        )
        .read_data(
            "lighting.fault-history",
            "Integration-owned lighting fault journal",
            &DataCategory::CurrentData,
            LightingResource {
                path: state,
                history: true,
            },
        )
        .build()?;
    let topology = Topology::new();
    {
        let mut t = topology.write().await;
        t.add_component(Component::new("autosd-host", "AutoSD vehicle computer"));
        t.add_app(
            App::new("zonal-lighting", "ThreadX zonal lighting")
                .with_component_id("autosd-host")
                .with_data_provider(provider),
        );
    }
    let server = Server::builder()
        .base_uri(base)?
        .listener(TcpListener::bind(&listen).await?)
        .topology(topology)
        .build()?;
    let mut terminate = tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())?;
    tokio::select! {
        result = server.serve() => result?,
        _ = tokio::signal::ctrl_c() => (),
        _ = terminate.recv() => (),
    }
    Ok(())
}
