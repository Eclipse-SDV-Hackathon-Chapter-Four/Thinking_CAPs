# SWE.5 Integration Test Specification

| Document ID | INC-DIAG-16-SWE5-IT |
|-------------|---------------------|
| Issue | #16 |
| Component | opensovd-gateway |
| Date | 2026-10-07 |

---

## 1. Test Scope

Integration tests verify the full stack:
- opensovd-server HTTP handling
- SovdDataProvider dispatching
- CruiseDiag resource implementation
- opensovd-client API

---

## 2. Test Environment

### 2.1 Test Setup

```rust
async fn start(debounce: TimeBased) -> Client {
    // Bind to ephemeral port (0)
    let listener = TcpListener::bind("127.0.0.1:0").await?;
    let address = listener.local_addr()?;

    // Build topology with cruise resources
    let topology = topology(debounce).await?;

    // Start server in background task
    let server = Server::builder()
        .base_uri(format!("http://{address}/sovd"))?
        .listener(listener)
        .topology(topology)
        .build()?;
    tokio::spawn(server.serve());

    // Connect client and wait for ready
    let client = Client::connect(&format!("http://{address}/sovd/v1"))?;
    // Poll until reachable
    Ok(client)
}
```

### 2.2 Test Teardown

Server task is dropped when test completes.

---

## 3. Integration Test Cases

### 3.1 Component and Resource Discovery

| Test ID | IT-DISC-001 |
|---------|-------------|
| Name | `serves_diag_api_resources_not_demo_data` |
| Objective | Verify cruise component replaces demo |
| Preconditions | Gateway started with cruise resources |
| Steps | 1. List components<br>2. List data for cruise component |
| Expected | Components: ["cruise"]<br>Data: ["vehicle_speed", "cruise_state", "speed_sensor_fault_status", "speed_sensor_stuck"]<br>All have groups: ["cruise"] |

### 3.2 Fault Injection Scenario

| Test ID | IT-FAULT-001 |
|---------|--------------|
| Name | `injected_fault_is_debounced_then_reported` |
| Objective | Verify debounce timing for fault qualification |
| Preconditions | Gateway started with 200ms debounce |
| Steps | 1. Read fault status (expect passed)<br>2. Write stuck=true<br>3. Read fault status (expect prefailed)<br>4. Wait 250ms<br>5. Read fault status (expect failed)<br>6. Write stuck=false<br>7. Wait 250ms<br>8. Read fault status (expect passed) |
| Expected | Status transitions: passed -> prefailed -> failed -> prepassed -> passed |

### 3.3 Read-Only Enforcement

| Test ID | IT-RO-001 |
|---------|-----------|
| Name | `read_only_resource_rejects_writes` |
| Objective | Verify read-only resources reject writes |
| Preconditions | Gateway started |
| Steps | 1. Attempt to write to vehicle_speed |
| Expected | Error response (write rejected) |

---

## 4. Test Sequence Diagram

```
┌────────┐     ┌──────────┐     ┌─────────────────┐
│ Client │     │  Server  │     │   CruiseDiag    │
└───┬────┘     └────┬─────┘     └───────┬─────────┘
    │               │                    │
    │ list_components                    │
    │──────────────>│                    │
    │ ["cruise"]    │                    │
    │<──────────────│                    │
    │               │                    │
    │ list_data("cruise")                │
    │──────────────>│                    │
    │ [4 resources] │                    │
    │<──────────────│                    │
    │               │                    │
    │ read("speed_sensor_fault_status")  │
    │──────────────>│ read()             │
    │               │───────────────────>│
    │               │ {"status":"passed"}│
    │ {"status":... │<───────────────────│
    │<──────────────│                    │
    │               │                    │
    │ write("speed_sensor_stuck", true)  │
    │──────────────>│ write()            │
    │               │───────────────────>│
    │               │ Ok                 │
    │ 200 OK        │<───────────────────│
    │<──────────────│                    │
    │               │                    │
```

---

## 5. Pass/Fail Criteria

| Criterion | Requirement |
|-----------|-------------|
| All assertions pass | Test marked as passed |
| Gateway reachable within 1s | Startup successful |
| Correct HTTP status codes | 200 for success, 4xx/5xx for errors |
| JSON response matches schema | Correct field names and types |

---

## 6. Test Execution

```bash
# Run integration tests
bazel test //score/opensovd-gateway:opensovd-gateway_test

# With verbose output
bazel test //score/opensovd-gateway:opensovd-gateway_test --test_output=all
```

---

## 7. Coverage Summary

| Scenario | Tests | Status |
|----------|-------|--------|
| Component discovery | 1 | Covered |
| Resource listing | 1 | Covered |
| Fault injection flow | 1 | Covered |
| Read-only enforcement | 1 | Covered |
| **Total** | **3** | |

---

*Prepared by: EP1991 | Thinking_CAPs | Eclipse SDV Hackathon Chapter 4 2026*
