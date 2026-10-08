use std::sync::Arc;

use axum::{
    Json, Router,
    extract::{Path, Query, State},
    http::StatusCode,
    response::{IntoResponse, Response},
    routing::{get, post},
};
use cruise_diag::{
    CruiseFaultProvider, Fault, FaultError, FaultFilter, FaultObservation, FaultProvider,
};
use serde::{Deserialize, Serialize};

#[derive(Clone)]
struct ApiState {
    entity_id: Arc<str>,
    provider: Arc<CruiseFaultProvider>,
}

#[derive(Clone, Copy)]
pub enum FaultEntityKind {
    App,
    Component,
}

impl FaultEntityKind {
    const fn collection(self) -> &'static str {
        match self {
            Self::App => "apps",
            Self::Component => "components",
        }
    }
}

#[derive(Serialize)]
struct FaultItems {
    items: Vec<Fault>,
}

#[derive(Serialize)]
struct ClearedResponse {
    cleared: usize,
}

#[derive(Debug, Serialize)]
struct ErrorBody {
    vendor_code: &'static str,
    message: &'static str,
}

#[derive(Debug)]
struct ApiError {
    status: StatusCode,
    vendor_code: &'static str,
    message: &'static str,
}

impl From<FaultError> for ApiError {
    fn from(error: FaultError) -> Self {
        match error {
            FaultError::NotFound(_) => Self {
                status: StatusCode::NOT_FOUND,
                vendor_code: "fault-not-found",
                message: "Fault was not found",
            },
            FaultError::InvalidFilter | FaultError::InvalidDefinition(_) => Self {
                status: StatusCode::BAD_REQUEST,
                vendor_code: "invalid-fault-request",
                message: "Fault request is invalid",
            },
            FaultError::SourceStale => Self {
                status: StatusCode::SERVICE_UNAVAILABLE,
                vendor_code: "fault-data-stale",
                message: "Fault data is stale",
            },
        }
    }
}

impl IntoResponse for ApiError {
    fn into_response(self) -> Response {
        (
            self.status,
            Json(ErrorBody {
                vendor_code: self.vendor_code,
                message: self.message,
            }),
        )
            .into_response()
    }
}

pub fn fault_routes(
    entity_kind: FaultEntityKind,
    entity_id: impl Into<Arc<str>>,
    provider: Arc<CruiseFaultProvider>,
) -> Router {
    let state = ApiState {
        entity_id: entity_id.into(),
        provider,
    };
    let collection_path = format!(
        "/sovd/v1/{}/{entity_id}/faults",
        entity_kind.collection(),
        entity_id = "{entity_id}"
    );
    let detail_path = format!("{collection_path}/{{code}}");
    Router::new()
        .route(&collection_path, get(list_faults).delete(clear_all_faults))
        .route(&detail_path, get(read_fault).delete(clear_fault))
        .route("/internal/fault-observations", post(ingest_observation))
        .with_state(state)
}

async fn verify_entity(state: &ApiState, entity_id: &str) -> Result<(), ApiError> {
    if entity_id == state.entity_id.as_ref() {
        Ok(())
    } else {
        Err(ApiError {
            status: StatusCode::NOT_FOUND,
            vendor_code: "entity-not-found",
            message: "Entity was not found",
        })
    }
}

async fn list_faults(
    State(state): State<ApiState>,
    Path(entity_id): Path<String>,
    Query(filter): Query<FaultFilter>,
) -> Result<Json<FaultItems>, ApiError> {
    verify_entity(&state, &entity_id).await?;
    let items = state.provider.list(filter).await?;
    Ok(Json(FaultItems { items }))
}

async fn read_fault(
    State(state): State<ApiState>,
    Path((entity_id, code)): Path<(String, String)>,
) -> Result<Json<Fault>, ApiError> {
    verify_entity(&state, &entity_id).await?;
    Ok(Json(state.provider.read(&code).await?))
}

async fn clear_fault(
    State(state): State<ApiState>,
    Path((entity_id, code)): Path<(String, String)>,
) -> Result<StatusCode, ApiError> {
    verify_entity(&state, &entity_id).await?;
    state.provider.clear(Some(&code)).await?;
    Ok(StatusCode::NO_CONTENT)
}

async fn clear_all_faults(
    State(state): State<ApiState>,
    Path(entity_id): Path<String>,
) -> Result<Json<ClearedResponse>, ApiError> {
    verify_entity(&state, &entity_id).await?;
    let cleared = state.provider.clear(None).await?;
    Ok(Json(ClearedResponse { cleared }))
}

#[derive(Deserialize)]
struct ObservationRequest {
    entity_id: String,
    #[serde(flatten)]
    observation: FaultObservation,
}

async fn ingest_observation(
    State(state): State<ApiState>,
    Json(request): Json<ObservationRequest>,
) -> Result<StatusCode, ApiError> {
    verify_entity(&state, &request.entity_id).await?;
    state.provider.observe(request.observation).await?;
    Ok(StatusCode::ACCEPTED)
}

#[cfg(test)]
mod tests {
    use axum::{body::Body, http::Request};
    use chrono::Utc;
    use cruise_diag::Severity;
    use http_body_util::BodyExt;
    use serde_json::json;
    use std::time::Duration;
    use tower::ServiceExt;

    use super::*;

    async fn setup() -> (Router, Arc<CruiseFaultProvider>) {
        let provider = Arc::new(
            CruiseFaultProvider::builder()
                .max_age(Duration::from_secs(30))
                .register(
                    "CC0001",
                    "Cruise input signal invalid",
                    Some(Severity::High),
                )
                .build()
                .unwrap(),
        );
        let app = fault_routes(FaultEntityKind::App, "cc-app", provider.clone());
        (app, provider)
    }

    #[tokio::test]
    async fn ingest_list_detail_filter_and_clear() {
        let (app, _) = setup().await;
        let observation = json!({
            "entity_id": "cc-app",
            "code": "CC0001",
            "status": 43,
            "timestamp": Utc::now(),
            "severity": "high",
            "environment_data": {
                "captured_at": Utc::now(),
                "signals": {"ego_velocity_kmh": 80.0}
            }
        });
        let response = app
            .clone()
            .oneshot(
                Request::builder()
                    .method("POST")
                    .uri("/internal/fault-observations")
                    .header("content-type", "application/json")
                    .body(Body::from(observation.to_string()))
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::ACCEPTED);

        let response = app
            .clone()
            .oneshot(
                Request::builder()
                    .uri("/sovd/v1/apps/cc-app/faults?statusMask=1&statusValue=1")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);
        let body = response.into_body().collect().await.unwrap().to_bytes();
        let value: serde_json::Value = serde_json::from_slice(&body).unwrap();
        assert_eq!(value["items"].as_array().unwrap().len(), 1);

        let response = app
            .clone()
            .oneshot(
                Request::builder()
                    .uri("/sovd/v1/apps/cc-app/faults/CC0001")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::OK);

        let response = app
            .oneshot(
                Request::builder()
                    .method("DELETE")
                    .uri("/sovd/v1/apps/cc-app/faults/CC0001")
                    .body(Body::empty())
                    .unwrap(),
            )
            .await
            .unwrap();
        assert_eq!(response.status(), StatusCode::NO_CONTENT);
    }

    #[tokio::test]
    async fn wrong_entity_and_unknown_fault_return_not_found() {
        let (app, _) = setup().await;
        for uri in [
            "/sovd/v1/apps/other/faults",
            "/sovd/v1/apps/cc-app/faults/UNKNOWN",
        ] {
            let response = app
                .clone()
                .oneshot(Request::builder().uri(uri).body(Body::empty()).unwrap())
                .await
                .unwrap();
            assert_eq!(response.status(), StatusCode::NOT_FOUND);
        }
    }
}
