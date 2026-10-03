use std::{env, net::SocketAddr, sync::Arc, time::Duration};

use cruise_diag::{CruiseFaultProvider, Severity};
use tokio::net::TcpListener;
use tracing_subscriber::EnvFilter;

use cruise_gateway::FaultEntityKind;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt()
        .with_env_filter(EnvFilter::try_from_default_env().unwrap_or_else(|_| "info".into()))
        .init();

    let provider = Arc::new(
        CruiseFaultProvider::builder()
            .max_age(Duration::from_secs(5))
            .register(
                "CC0001",
                "Cruise input signal invalid",
                Some(Severity::High),
            )
            .register(
                "CC0002",
                "Cruise controller output unavailable",
                Some(Severity::Medium),
            )
            .build()?,
    );
    let app = cruise_gateway::fault_routes(FaultEntityKind::App, "cc-app", provider);
    let address: SocketAddr = env::var("SOVD_BIND_ADDR")
        .unwrap_or_else(|_| "127.0.0.1:7690".into())
        .parse()?;
    let listener = TcpListener::bind(address).await?;
    tracing::info!(%address, "Cruise diagnostic gateway listening");
    axum::serve(listener, app).await?;
    Ok(())
}
