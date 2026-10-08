# Eclipse SDV Hackathon 2026 - Full Environment Setup Guide

## Complete Manual Setup: Layer 0 to Layer 6

This guide walks you through setting up the **entire stack** from scratch in a new folder.

---

## Prerequisites

### Required Software

```bash
# Check prerequisites
rustc --version      # Rust 1.75+
cargo --version      # Cargo 1.75+
g++ --version        # GCC 11+ or Clang 14+
bazel --version      # Bazel 6.0+
docker --version     # Docker 24+
python3 --version    # Python 3.10+
node --version       # Node.js 18+ (optional, for diagrams)
```

### Install Missing Tools (macOS)

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Bazel
brew install bazel

# Docker
brew install --cask docker

# Python packages
pip3 install aiohttp requests pytest
```

### Install Missing Tools (Ubuntu/Linux)

```bash
# Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Bazel
sudo apt install apt-transport-https curl gnupg
curl -fsSL https://bazel.build/bazel-release.pub.gpg | gpg --dearmor > bazel.gpg
sudo mv bazel.gpg /etc/apt/trusted.gpg.d/
echo "deb [arch=amd64] https://storage.googleapis.com/bazel-apt stable jdk1.8" | sudo tee /etc/apt/sources.list.d/bazel.list
sudo apt update && sudo apt install bazel

# Docker
sudo apt install docker.io docker-compose
sudo usermod -aG docker $USER

# Build tools
sudo apt install build-essential cmake libboost-all-dev
```

---

## Step 1: Create Project Structure

```bash
# Create main project folder
mkdir -p ~/Projects/EclipseSDV-Hackathon-2026
cd ~/Projects/EclipseSDV-Hackathon-2026

# Create layer folders
mkdir -p layer0-ecu/{cruise-control,car-simulation}
mkdir -p layer1-score/{middleware,config}
mkdir -p layer2-gateway/{gatewayd,someipd}
mkdir -p layer3-diagnostics/{cruise-diag,cruise-bridge}
mkdir -p layer4-adapter/{sovd-adapter}
mkdir -p layer5-sovd/{opensovd-server,api-fixes}
mkdir -p layer6-dashboard/{web,static}
mkdir -p testing/{opendut,integration,unit}
mkdir -p docker/{compose,images}
mkdir -p docs
mkdir -p evidence/runs

# Verify structure
tree -L 2
```

Expected structure:
```
EclipseSDV-Hackathon-2026/
├── layer0-ecu/
│   ├── cruise-control/
│   └── car-simulation/
├── layer1-score/
│   ├── middleware/
│   └── config/
├── layer2-gateway/
│   ├── gatewayd/
│   └── someipd/
├── layer3-diagnostics/
│   ├── cruise-diag/
│   └── cruise-bridge/
├── layer4-adapter/
│   └── sovd-adapter/
├── layer5-sovd/
│   ├── opensovd-server/
│   └── api-fixes/
├── layer6-dashboard/
│   ├── web/
│   └── static/
├── testing/
├── docker/
├── docs/
└── evidence/
```

---

## Step 2: Layer 0 - Cruise Control ECU & Car Simulation

### 2.1 Create Cruise Control ECU (C++)

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer0-ecu/cruise-control
```

#### Create cruise_control.h

```bash
cat > cruise_control.h << 'EOF'
#ifndef CRUISE_CONTROL_H
#define CRUISE_CONTROL_H

#include <cstdint>
#include <atomic>

namespace cruise {

enum class CruiseState {
    STANDBY = 0,
    ACTIVE = 1,
    DISABLING = 2,
    DISABLED = 3
};

struct CruiseStatus {
    CruiseState state;
    float current_speed;
    float target_speed;
    float throttle_output;
    bool fault_active;
    uint32_t dtc_count;
};

class CruiseController {
public:
    CruiseController();
    ~CruiseController() = default;

    // Control
    void enable(float target_speed);
    void disable();
    void update(float current_speed, float dt_ms);

    // Fault handling
    void inject_fault();
    void clear_fault();

    // Getters
    CruiseStatus get_status() const;
    CruiseState get_state() const { return state_; }
    float get_throttle() const { return throttle_output_; }

private:
    // PID parameters
    static constexpr float Kp = 0.25f;
    static constexpr float Ki = 0.03f;
    static constexpr float Kd = 0.12f;

    // State
    std::atomic<CruiseState> state_{CruiseState::STANDBY};
    float target_speed_{0.0f};
    float current_speed_{0.0f};
    float throttle_output_{0.0f};

    // PID state
    float integral_{0.0f};
    float prev_error_{0.0f};

    // Fault state
    std::atomic<bool> fault_active_{false};
    uint32_t dtc_count_{0};

    // PID calculation
    float compute_pid(float error, float dt);
    void reset_pid();
};

} // namespace cruise

#endif // CRUISE_CONTROL_H
EOF
```

#### Create cruise_control.cpp

```bash
cat > cruise_control.cpp << 'EOF'
#include "cruise_control.h"
#include <algorithm>
#include <cmath>

namespace cruise {

CruiseController::CruiseController() {
    reset_pid();
}

void CruiseController::enable(float target_speed) {
    if (state_ == CruiseState::STANDBY && !fault_active_) {
        target_speed_ = std::clamp(target_speed, 0.0f, 200.0f);
        state_ = CruiseState::ACTIVE;
        reset_pid();
    }
}

void CruiseController::disable() {
    state_ = CruiseState::DISABLING;
    throttle_output_ = 0.0f;
}

void CruiseController::update(float current_speed, float dt_ms) {
    current_speed_ = current_speed;
    float dt = dt_ms / 1000.0f;  // Convert to seconds

    switch (state_) {
        case CruiseState::ACTIVE:
            if (fault_active_) {
                state_ = CruiseState::DISABLING;
                dtc_count_++;
            } else {
                float error = target_speed_ - current_speed_;
                throttle_output_ = compute_pid(error, dt);
                throttle_output_ = std::clamp(throttle_output_, -1.0f, 1.0f);
            }
            break;

        case CruiseState::DISABLING:
            // Gradual deceleration
            throttle_output_ = std::max(throttle_output_ - 0.02f, -0.5f);
            if (current_speed_ < 5.0f) {
                state_ = CruiseState::DISABLED;
                throttle_output_ = 0.0f;
            }
            break;

        case CruiseState::DISABLED:
            if (!fault_active_) {
                state_ = CruiseState::STANDBY;
            }
            break;

        case CruiseState::STANDBY:
        default:
            throttle_output_ = 0.0f;
            break;
    }
}

float CruiseController::compute_pid(float error, float dt) {
    if (dt <= 0.0f) return throttle_output_;

    // Proportional
    float p_term = Kp * error;

    // Integral with anti-windup
    integral_ += error * dt;
    integral_ = std::clamp(integral_, -10.0f, 10.0f);
    float i_term = Ki * integral_;

    // Derivative
    float derivative = (error - prev_error_) / dt;
    float d_term = Kd * derivative;
    prev_error_ = error;

    return p_term + i_term + d_term;
}

void CruiseController::reset_pid() {
    integral_ = 0.0f;
    prev_error_ = 0.0f;
}

void CruiseController::inject_fault() {
    fault_active_ = true;
}

void CruiseController::clear_fault() {
    fault_active_ = false;
    if (state_ == CruiseState::DISABLED) {
        state_ = CruiseState::STANDBY;
    }
}

CruiseStatus CruiseController::get_status() const {
    return CruiseStatus{
        .state = state_.load(),
        .current_speed = current_speed_,
        .target_speed = target_speed_,
        .throttle_output = throttle_output_,
        .fault_active = fault_active_.load(),
        .dtc_count = dtc_count_
    };
}

} // namespace cruise
EOF
```

#### Create main.cpp

```bash
cat > main.cpp << 'EOF'
#include "cruise_control.h"
#include <iostream>
#include <thread>
#include <chrono>
#include <csignal>

std::atomic<bool> running{true};

void signal_handler(int) {
    running = false;
}

int main() {
    std::signal(SIGINT, signal_handler);
    std::signal(SIGTERM, signal_handler);

    cruise::CruiseController controller;
    float simulated_speed = 0.0f;

    std::cout << "Cruise Control ECU started" << std::endl;
    std::cout << "Commands: e=enable, d=disable, f=fault, c=clear, q=quit" << std::endl;

    // Enable cruise at 120 km/h
    controller.enable(120.0f);

    while (running) {
        // Simulate vehicle dynamics
        auto status = controller.get_status();

        if (status.state == cruise::CruiseState::ACTIVE) {
            // Simple vehicle model: speed changes based on throttle
            simulated_speed += status.throttle_output * 2.0f;
            simulated_speed = std::max(0.0f, simulated_speed);
        } else if (status.state == cruise::CruiseState::DISABLING) {
            simulated_speed = std::max(0.0f, simulated_speed - 1.0f);
        }

        // Update controller
        controller.update(simulated_speed, 50.0f);  // 50ms loop

        // Print status
        std::cout << "\rState: " << static_cast<int>(status.state)
                  << " | Speed: " << simulated_speed
                  << " | Target: " << status.target_speed
                  << " | Throttle: " << status.throttle_output
                  << " | Fault: " << (status.fault_active ? "YES" : "NO")
                  << " | DTCs: " << status.dtc_count
                  << "     " << std::flush;

        std::this_thread::sleep_for(std::chrono::milliseconds(50));
    }

    std::cout << "\nCruise Control ECU stopped" << std::endl;
    return 0;
}
EOF
```

#### Create BUILD.bazel

```bash
cat > BUILD.bazel << 'EOF'
cc_library(
    name = "cruise_control_lib",
    srcs = ["cruise_control.cpp"],
    hdrs = ["cruise_control.h"],
    visibility = ["//visibility:public"],
)

cc_binary(
    name = "cruise_ecu",
    srcs = ["main.cpp"],
    deps = [":cruise_control_lib"],
)

cc_test(
    name = "cruise_control_test",
    srcs = ["cruise_control_test.cpp"],
    deps = [
        ":cruise_control_lib",
        "@com_google_googletest//:gtest_main",
    ],
)
EOF
```

#### Create cruise_control_test.cpp

```bash
cat > cruise_control_test.cpp << 'EOF'
#include "cruise_control.h"
#include <gtest/gtest.h>

namespace cruise {

TEST(CruiseControlTest, InitialState) {
    CruiseController controller;
    EXPECT_EQ(controller.get_state(), CruiseState::STANDBY);
    EXPECT_FLOAT_EQ(controller.get_throttle(), 0.0f);
}

TEST(CruiseControlTest, EnableDisable) {
    CruiseController controller;
    controller.enable(100.0f);
    EXPECT_EQ(controller.get_state(), CruiseState::ACTIVE);

    controller.disable();
    EXPECT_EQ(controller.get_state(), CruiseState::DISABLING);
}

TEST(CruiseControlTest, FaultInjection) {
    CruiseController controller;
    controller.enable(100.0f);
    EXPECT_EQ(controller.get_state(), CruiseState::ACTIVE);

    controller.inject_fault();
    controller.update(100.0f, 50.0f);

    EXPECT_EQ(controller.get_state(), CruiseState::DISABLING);
    EXPECT_TRUE(controller.get_status().fault_active);
}

TEST(CruiseControlTest, PIDConvergence) {
    CruiseController controller;
    controller.enable(100.0f);

    float speed = 80.0f;
    for (int i = 0; i < 100; i++) {
        controller.update(speed, 50.0f);
        speed += controller.get_throttle() * 2.0f;
    }

    // Speed should converge towards target
    EXPECT_NEAR(speed, 100.0f, 10.0f);
}

} // namespace cruise
EOF
```

### 2.2 Create Car Simulation

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer0-ecu/car-simulation
```

#### Create car_simulation.h

```bash
cat > car_simulation.h << 'EOF'
#ifndef CAR_SIMULATION_H
#define CAR_SIMULATION_H

#include <cstdint>
#include <functional>

namespace car_sim {

struct VehicleState {
    float speed_kmh;
    float acceleration;
    float engine_rpm;
    float brake_pressure;
    bool speed_sensor_ok;
    uint64_t timestamp_ms;
};

class CarSimulation {
public:
    CarSimulation();

    // Simulation control
    void start();
    void stop();
    void update(float throttle, float brake, float dt_ms);

    // Fault injection
    void fail_speed_sensor();
    void restore_speed_sensor();

    // Getters
    VehicleState get_state() const;
    float get_speed() const { return speed_; }

    // Callback for SOME/IP events
    using SpeedCallback = std::function<void(float speed, uint64_t timestamp)>;
    void set_speed_callback(SpeedCallback cb) { speed_callback_ = cb; }

private:
    float speed_{0.0f};
    float acceleration_{0.0f};
    float engine_rpm_{800.0f};
    bool speed_sensor_ok_{true};
    uint64_t timestamp_{0};

    SpeedCallback speed_callback_;

    // Vehicle dynamics parameters
    static constexpr float MASS_KG = 1500.0f;
    static constexpr float DRAG_COEFF = 0.3f;
    static constexpr float MAX_ENGINE_FORCE = 5000.0f;
    static constexpr float MAX_BRAKE_FORCE = 10000.0f;
};

} // namespace car_sim

#endif // CAR_SIMULATION_H
EOF
```

#### Create car_simulation.cpp

```bash
cat > car_simulation.cpp << 'EOF'
#include "car_simulation.h"
#include <algorithm>
#include <cmath>
#include <chrono>

namespace car_sim {

CarSimulation::CarSimulation() {
    timestamp_ = std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()
    ).count();
}

void CarSimulation::start() {
    speed_ = 0.0f;
    acceleration_ = 0.0f;
    engine_rpm_ = 800.0f;
    speed_sensor_ok_ = true;
}

void CarSimulation::stop() {
    speed_ = 0.0f;
    acceleration_ = 0.0f;
}

void CarSimulation::update(float throttle, float brake, float dt_ms) {
    float dt = dt_ms / 1000.0f;

    // Calculate forces
    float engine_force = throttle * MAX_ENGINE_FORCE;
    float brake_force = brake * MAX_BRAKE_FORCE;

    // Aerodynamic drag (F = 0.5 * Cd * A * rho * v^2)
    float speed_ms = speed_ / 3.6f;  // km/h to m/s
    float drag_force = 0.5f * DRAG_COEFF * 2.2f * 1.225f * speed_ms * speed_ms;

    // Net force and acceleration
    float net_force = engine_force - brake_force - drag_force;
    acceleration_ = net_force / MASS_KG;

    // Update speed
    speed_ += acceleration_ * dt * 3.6f;  // m/s^2 to km/h change
    speed_ = std::clamp(speed_, 0.0f, 250.0f);

    // Update engine RPM (simplified)
    engine_rpm_ = 800.0f + (speed_ / 250.0f) * 6000.0f;

    // Update timestamp
    timestamp_ += static_cast<uint64_t>(dt_ms);

    // Send speed event (if sensor ok and callback set)
    if (speed_sensor_ok_ && speed_callback_) {
        speed_callback_(speed_, timestamp_);
    }
}

void CarSimulation::fail_speed_sensor() {
    speed_sensor_ok_ = false;
}

void CarSimulation::restore_speed_sensor() {
    speed_sensor_ok_ = true;
}

VehicleState CarSimulation::get_state() const {
    return VehicleState{
        .speed_kmh = speed_,
        .acceleration = acceleration_,
        .engine_rpm = engine_rpm_,
        .brake_pressure = 0.0f,
        .speed_sensor_ok = speed_sensor_ok_,
        .timestamp_ms = timestamp_
    };
}

} // namespace car_sim
EOF
```

#### Create BUILD.bazel

```bash
cat > BUILD.bazel << 'EOF'
cc_library(
    name = "car_simulation_lib",
    srcs = ["car_simulation.cpp"],
    hdrs = ["car_simulation.h"],
    visibility = ["//visibility:public"],
)

cc_binary(
    name = "car_sim",
    srcs = ["main.cpp"],
    deps = [":car_simulation_lib"],
)
EOF
```

---

## Step 3: Layer 1 - S-CORE Middleware Configuration

### 3.1 Create S-CORE Docker Configuration

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer1-score/config
```

#### Create someip_config.json

```bash
cat > someip_config.json << 'EOF'
{
    "unicast": "172.17.0.2",
    "logging": {
        "level": "debug",
        "console": true,
        "file": {
            "enable": true,
            "path": "/var/log/vsomeip"
        }
    },
    "applications": [
        {
            "name": "cruise_ecu",
            "id": "0x1001"
        },
        {
            "name": "car_sim",
            "id": "0x1002"
        },
        {
            "name": "cruise_bridge",
            "id": "0x1003"
        }
    ],
    "services": [
        {
            "service": "0x1234",
            "instance": "0x5678",
            "unreliable": 30509,
            "events": [
                {
                    "event": "0x8001",
                    "is_field": false
                }
            ],
            "eventgroups": [
                {
                    "eventgroup": "0x0001",
                    "events": ["0x8001"]
                }
            ]
        }
    ],
    "routing": "cruise_ecu",
    "service-discovery": {
        "enable": true,
        "multicast": "224.244.224.245",
        "port": 30490,
        "protocol": "udp"
    }
}
EOF
```

#### Create lola_config.yaml

```bash
cat > lola_config.yaml << 'EOF'
# S-CORE LoLa (Low Latency) IPC Configuration
lola:
  version: "1.0"

  shared_memory:
    base_path: "/dev/shm/score"
    max_size_mb: 256

  channels:
    - name: "cruise_speed"
      id: 0x1001
      type: "event"
      max_payload: 64

    - name: "cruise_state"
      id: 0x1002
      type: "field"
      max_payload: 128

    - name: "dtc_events"
      id: 0x1003
      type: "event"
      max_payload: 256

  routing:
    mode: "local"
    gateway_port: 7700
EOF
```

### 3.2 Clone S-CORE (Reference Only)

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer1-score/middleware

# Clone S-CORE (reference - we use Docker image)
git clone https://github.com/eclipse-score/score.git --depth 1

# Note: We'll use the Docker image for actual deployment
```

---

## Step 4: Layer 2 - Gateway Configuration

### 4.1 Create Gateway Docker Files

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer2-gateway
```

#### Create gatewayd configuration

```bash
cat > gatewayd/config.yaml << 'EOF'
# S-CORE gatewayd configuration
gateway:
  name: "cruise-gateway"

  lola:
    enable: true
    shm_path: "/dev/shm/score"

  someip:
    enable: true
    config_file: "/etc/vsomeip/someip_config.json"

  routing:
    - source: "someip:0x1234:0x5678"
      target: "lola:cruise_speed"

    - source: "lola:cruise_state"
      target: "someip:0x1234:0x5679"

  tcp_bridge:
    enable: true
    port: 7700
    allowed_clients:
      - "172.17.0.0/16"
EOF
```

#### Create someipd configuration

```bash
cat > someipd/vsomeipd.json << 'EOF'
{
    "unicast": "0.0.0.0",
    "netmask": "255.255.0.0",
    "logging": {
        "level": "info",
        "console": true
    },
    "service-discovery": {
        "enable": true,
        "multicast": "224.244.224.245",
        "port": 30490,
        "protocol": "udp",
        "initial_delay_min": 10,
        "initial_delay_max": 100,
        "repetitions_base_delay": 200,
        "repetitions_max": 3,
        "ttl": 3,
        "cyclic_offer_delay": 2000
    }
}
EOF
```

---

## Step 5: Layer 3 - Diagnostics (cruise_diag & cruise_bridge)

### 5.1 Create cruise_diag Rust Crate

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer3-diagnostics/cruise-diag
cargo init --lib
```

#### Update Cargo.toml

```bash
cat > Cargo.toml << 'EOF'
[package]
name = "cruise_diag"
version = "0.1.0"
edition = "2021"
description = "Cruise Control Diagnostics - Fault Monitor & DTC Storage"

[dependencies]
tokio = { version = "1.35", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
chrono = { version = "0.4", features = ["serde"] }
tracing = "0.1"
thiserror = "1.0"

[dev-dependencies]
tokio-test = "0.4"
EOF
```

#### Create src/lib.rs

```bash
cat > src/lib.rs << 'EOF'
//! Cruise Control Diagnostics Module
//!
//! Implements fault detection, debounce logic, and DTC storage
//! for the Cruise Control ADAS system.

use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use std::time::Duration;
use tokio::sync::RwLock;
use thiserror::Error;

/// DTC (Diagnostic Trouble Code) identifier
pub type DtcId = String;

/// Fault detection states
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub enum FaultState {
    /// No fault detected
    Ok,
    /// Fault detected, awaiting confirmation (debounce)
    Pending,
    /// Fault confirmed after debounce period
    Confirmed,
    /// Fault healing, awaiting clear
    Healing,
}

/// ISO 14229-1 DTC Status Bits
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DtcStatus {
    pub test_failed: bool,
    pub test_failed_this_cycle: bool,
    pub pending_dtc: bool,
    pub confirmed_dtc: bool,
    pub test_not_completed_since_clear: bool,
    pub test_failed_since_clear: bool,
    pub test_not_completed_this_cycle: bool,
    pub warning_indicator_requested: bool,
}

impl Default for DtcStatus {
    fn default() -> Self {
        Self {
            test_failed: false,
            test_failed_this_cycle: false,
            pending_dtc: false,
            confirmed_dtc: false,
            test_not_completed_since_clear: true,
            test_failed_since_clear: false,
            test_not_completed_this_cycle: true,
            warning_indicator_requested: false,
        }
    }
}

/// DTC Entry stored in memory
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DtcEntry {
    pub id: DtcId,
    pub description: String,
    pub status: DtcStatus,
    pub occurrence_count: u32,
    pub first_occurrence: DateTime<Utc>,
    pub last_occurrence: DateTime<Utc>,
    pub freeze_frame: Option<FreezeFrame>,
}

/// Freeze frame data captured at fault time
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FreezeFrame {
    pub speed_kmh: f64,
    pub engine_rpm: f64,
    pub timestamp: DateTime<Utc>,
    pub additional_data: HashMap<String, serde_json::Value>,
}

/// Debounce configuration
#[derive(Debug, Clone)]
pub struct DebounceConfig {
    /// Time to confirm a fault (ms)
    pub confirm_time_ms: u64,
    /// Time to heal a fault (ms)
    pub heal_time_ms: u64,
}

impl Default for DebounceConfig {
    fn default() -> Self {
        Self {
            confirm_time_ms: 5000,  // 5 seconds to confirm
            heal_time_ms: 2000,     // 2 seconds to heal
        }
    }
}

/// Fault Monitor for a single signal
#[derive(Debug)]
pub struct FaultMonitor {
    name: String,
    dtc_id: DtcId,
    state: FaultState,
    config: DebounceConfig,
    pending_start: Option<std::time::Instant>,
    healing_start: Option<std::time::Instant>,
    last_value: Option<f64>,
}

impl FaultMonitor {
    pub fn new(name: &str, dtc_id: &str, config: DebounceConfig) -> Self {
        Self {
            name: name.to_string(),
            dtc_id: dtc_id.to_string(),
            state: FaultState::Ok,
            config,
            pending_start: None,
            healing_start: None,
            last_value: None,
        }
    }

    /// Check signal and update fault state
    /// Returns Some(DtcId) if a new fault is confirmed
    pub fn check_signal(&mut self, value: Option<f64>) -> Option<DtcId> {
        let now = std::time::Instant::now();
        self.last_value = value;

        match (self.state, value) {
            // Signal lost - start pending
            (FaultState::Ok, None) => {
                self.state = FaultState::Pending;
                self.pending_start = Some(now);
                self.healing_start = None;
                None
            }

            // Still pending - check debounce
            (FaultState::Pending, None) => {
                if let Some(start) = self.pending_start {
                    if now.duration_since(start) >= Duration::from_millis(self.config.confirm_time_ms) {
                        self.state = FaultState::Confirmed;
                        self.pending_start = None;
                        return Some(self.dtc_id.clone());
                    }
                }
                None
            }

            // Signal restored while pending - return to OK
            (FaultState::Pending, Some(_)) => {
                self.state = FaultState::Ok;
                self.pending_start = None;
                None
            }

            // Confirmed fault, signal still lost
            (FaultState::Confirmed, None) => {
                self.healing_start = None;
                None
            }

            // Confirmed fault, signal restored - start healing
            (FaultState::Confirmed, Some(_)) => {
                self.state = FaultState::Healing;
                self.healing_start = Some(now);
                None
            }

            // Healing - check debounce
            (FaultState::Healing, Some(_)) => {
                if let Some(start) = self.healing_start {
                    if now.duration_since(start) >= Duration::from_millis(self.config.heal_time_ms) {
                        self.state = FaultState::Ok;
                        self.healing_start = None;
                    }
                }
                None
            }

            // Healing but signal lost again - back to confirmed
            (FaultState::Healing, None) => {
                self.state = FaultState::Confirmed;
                self.healing_start = None;
                None
            }

            // Normal operation
            (FaultState::Ok, Some(_)) => None,
        }
    }

    pub fn get_state(&self) -> FaultState {
        self.state
    }

    pub fn get_dtc_id(&self) -> &str {
        &self.dtc_id
    }
}

/// DTC Storage - manages all DTCs
#[derive(Debug)]
pub struct DtcStorage {
    entries: Arc<RwLock<HashMap<DtcId, DtcEntry>>>,
}

impl DtcStorage {
    pub fn new() -> Self {
        Self {
            entries: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Store a new DTC or update existing
    pub async fn store_dtc(&self, dtc_id: &str, description: &str, freeze_frame: Option<FreezeFrame>) {
        let mut entries = self.entries.write().await;
        let now = Utc::now();

        if let Some(entry) = entries.get_mut(dtc_id) {
            // Update existing
            entry.occurrence_count += 1;
            entry.last_occurrence = now;
            entry.status.confirmed_dtc = true;
            entry.status.test_failed = true;
            entry.status.warning_indicator_requested = true;
            if freeze_frame.is_some() {
                entry.freeze_frame = freeze_frame;
            }
        } else {
            // Create new
            let mut status = DtcStatus::default();
            status.confirmed_dtc = true;
            status.test_failed = true;
            status.pending_dtc = true;
            status.warning_indicator_requested = true;

            entries.insert(dtc_id.to_string(), DtcEntry {
                id: dtc_id.to_string(),
                description: description.to_string(),
                status,
                occurrence_count: 1,
                first_occurrence: now,
                last_occurrence: now,
                freeze_frame,
            });
        }
    }

    /// Get all DTCs
    pub async fn get_all_dtcs(&self) -> Vec<DtcEntry> {
        let entries = self.entries.read().await;
        entries.values().cloned().collect()
    }

    /// Get specific DTC
    pub async fn get_dtc(&self, dtc_id: &str) -> Option<DtcEntry> {
        let entries = self.entries.read().await;
        entries.get(dtc_id).cloned()
    }

    /// Clear specific DTC
    pub async fn clear_dtc(&self, dtc_id: &str) -> bool {
        let mut entries = self.entries.write().await;
        entries.remove(dtc_id).is_some()
    }

    /// Clear all DTCs
    pub async fn clear_all_dtcs(&self) -> usize {
        let mut entries = self.entries.write().await;
        let count = entries.len();
        entries.clear();
        count
    }

    /// Get DTC count
    pub async fn count(&self) -> usize {
        let entries = self.entries.read().await;
        entries.len()
    }
}

impl Default for DtcStorage {
    fn default() -> Self {
        Self::new()
    }
}

/// Error types
#[derive(Error, Debug)]
pub enum DiagError {
    #[error("DTC not found: {0}")]
    DtcNotFound(String),

    #[error("Invalid operation: {0}")]
    InvalidOperation(String),

    #[error("Storage error: {0}")]
    StorageError(String),
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_fault_monitor_signal_loss() {
        let config = DebounceConfig {
            confirm_time_ms: 100,
            heal_time_ms: 50,
        };
        let mut monitor = FaultMonitor::new("speed", "U0100", config);

        // Initial state
        assert_eq!(monitor.get_state(), FaultState::Ok);

        // Signal lost - should go to pending
        monitor.check_signal(None);
        assert_eq!(monitor.get_state(), FaultState::Pending);

        // Signal restored quickly - should return to OK
        monitor.check_signal(Some(100.0));
        assert_eq!(monitor.get_state(), FaultState::Ok);
    }

    #[tokio::test]
    async fn test_dtc_storage() {
        let storage = DtcStorage::new();

        // Store DTC
        storage.store_dtc("U0100", "Speed sensor communication lost", None).await;

        // Verify stored
        let dtcs = storage.get_all_dtcs().await;
        assert_eq!(dtcs.len(), 1);
        assert_eq!(dtcs[0].id, "U0100");
        assert!(dtcs[0].status.confirmed_dtc);

        // Clear DTC
        let cleared = storage.clear_dtc("U0100").await;
        assert!(cleared);
        assert_eq!(storage.count().await, 0);
    }
}
EOF
```

### 5.2 Create cruise_bridge Rust Crate

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer3-diagnostics/cruise-bridge
cargo init --lib
```

#### Update Cargo.toml

```bash
cat > Cargo.toml << 'EOF'
[package]
name = "cruise_bridge"
version = "0.1.0"
edition = "2021"
description = "mw::com Bridge - Connects to S-CORE middleware via TCP"

[dependencies]
tokio = { version = "1.35", features = ["full", "net"] }
tokio-util = { version = "0.7", features = ["codec"] }
bytes = "1.5"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tracing = "0.1"
thiserror = "1.0"
futures = "0.3"

[dev-dependencies]
tokio-test = "0.4"
EOF
```

#### Create src/lib.rs

```bash
cat > src/lib.rs << 'EOF'
//! Cruise Bridge - mw::com Consumer
//!
//! Connects to S-CORE gatewayd via TCP to receive speed events
//! and publish cruise control state.

use bytes::{Buf, BufMut, BytesMut};
use futures::StreamExt;
use serde::{Deserialize, Serialize};
use std::io;
use std::net::SocketAddr;
use thiserror::Error;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::TcpStream;
use tokio::sync::mpsc;
use tokio_util::codec::{Decoder, Encoder, Framed};
use tracing::{debug, error, info, warn};

/// Message types for mw::com protocol
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(tag = "type")]
pub enum MwComMessage {
    /// Subscribe to an event
    Subscribe { channel_id: u32 },

    /// Unsubscribe from an event
    Unsubscribe { channel_id: u32 },

    /// Event notification
    Event {
        channel_id: u32,
        payload: Vec<u8>,
        timestamp_ms: u64,
    },

    /// Field read request
    ReadField { field_id: u32 },

    /// Field read response
    FieldValue {
        field_id: u32,
        payload: Vec<u8>,
    },

    /// Field write request
    WriteField {
        field_id: u32,
        payload: Vec<u8>,
    },

    /// Acknowledgement
    Ack { request_id: u32, success: bool },

    /// Error
    Error { code: u32, message: String },
}

/// Speed event payload
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SpeedEvent {
    pub speed_kmh: f64,
    pub timestamp_ms: u64,
    pub valid: bool,
}

/// Cruise state for publishing
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CruiseState {
    pub state: u8,  // 0=STANDBY, 1=ACTIVE, 2=DISABLING, 3=DISABLED
    pub target_speed: f64,
    pub fault_active: bool,
    pub dtc_count: u32,
}

/// Channel IDs (must match gatewayd config)
pub mod channels {
    pub const CRUISE_SPEED: u32 = 0x1001;
    pub const CRUISE_STATE: u32 = 0x1002;
    pub const DTC_EVENTS: u32 = 0x1003;
}

/// Bridge configuration
#[derive(Debug, Clone)]
pub struct BridgeConfig {
    pub gateway_addr: SocketAddr,
    pub reconnect_delay_ms: u64,
    pub event_buffer_size: usize,
}

impl Default for BridgeConfig {
    fn default() -> Self {
        Self {
            gateway_addr: "127.0.0.1:7700".parse().unwrap(),
            reconnect_delay_ms: 1000,
            event_buffer_size: 100,
        }
    }
}

/// Message codec for TCP framing
pub struct MwComCodec;

impl Decoder for MwComCodec {
    type Item = MwComMessage;
    type Error = io::Error;

    fn decode(&mut self, src: &mut BytesMut) -> Result<Option<Self::Item>, Self::Error> {
        if src.len() < 4 {
            return Ok(None);
        }

        let len = (&src[..4]).get_u32() as usize;
        if src.len() < 4 + len {
            return Ok(None);
        }

        src.advance(4);
        let data = src.split_to(len);

        serde_json::from_slice(&data)
            .map(Some)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))
    }
}

impl Encoder<MwComMessage> for MwComCodec {
    type Error = io::Error;

    fn encode(&mut self, item: MwComMessage, dst: &mut BytesMut) -> Result<(), Self::Error> {
        let data = serde_json::to_vec(&item)
            .map_err(|e| io::Error::new(io::ErrorKind::InvalidData, e))?;

        dst.put_u32(data.len() as u32);
        dst.extend_from_slice(&data);
        Ok(())
    }
}

/// Bridge errors
#[derive(Error, Debug)]
pub enum BridgeError {
    #[error("Connection failed: {0}")]
    ConnectionFailed(#[from] io::Error),

    #[error("Protocol error: {0}")]
    ProtocolError(String),

    #[error("Channel closed")]
    ChannelClosed,
}

/// mw::com Bridge
pub struct MwComBridge {
    config: BridgeConfig,
    speed_tx: mpsc::Sender<SpeedEvent>,
    speed_rx: Option<mpsc::Receiver<SpeedEvent>>,
}

impl MwComBridge {
    pub fn new(config: BridgeConfig) -> Self {
        let (speed_tx, speed_rx) = mpsc::channel(config.event_buffer_size);
        Self {
            config,
            speed_tx,
            speed_rx: Some(speed_rx),
        }
    }

    /// Take the speed event receiver (can only be called once)
    pub fn take_speed_receiver(&mut self) -> Option<mpsc::Receiver<SpeedEvent>> {
        self.speed_rx.take()
    }

    /// Connect to gateway and start receiving events
    pub async fn connect(&self) -> Result<(), BridgeError> {
        info!("Connecting to gateway at {}", self.config.gateway_addr);

        let stream = TcpStream::connect(self.config.gateway_addr).await?;
        let mut framed = Framed::new(stream, MwComCodec);

        // Subscribe to speed events
        let subscribe_msg = MwComMessage::Subscribe {
            channel_id: channels::CRUISE_SPEED,
        };

        use futures::SinkExt;
        framed.send(subscribe_msg).await
            .map_err(|e| BridgeError::ProtocolError(e.to_string()))?;

        info!("Subscribed to speed channel");

        // Process incoming messages
        while let Some(result) = framed.next().await {
            match result {
                Ok(msg) => self.handle_message(msg).await?,
                Err(e) => {
                    error!("Receive error: {}", e);
                    return Err(BridgeError::ConnectionFailed(e));
                }
            }
        }

        Ok(())
    }

    async fn handle_message(&self, msg: MwComMessage) -> Result<(), BridgeError> {
        match msg {
            MwComMessage::Event { channel_id, payload, timestamp_ms } => {
                if channel_id == channels::CRUISE_SPEED {
                    if let Ok(speed_event) = serde_json::from_slice::<SpeedEvent>(&payload) {
                        debug!("Speed event: {:?}", speed_event);
                        self.speed_tx.send(speed_event).await
                            .map_err(|_| BridgeError::ChannelClosed)?;
                    }
                }
            }
            MwComMessage::Ack { request_id, success } => {
                debug!("Ack for request {}: {}", request_id, success);
            }
            MwComMessage::Error { code, message } => {
                warn!("Gateway error {}: {}", code, message);
            }
            _ => {}
        }
        Ok(())
    }

    /// Publish cruise state to gateway
    pub async fn publish_state(&self, state: CruiseState) -> Result<(), BridgeError> {
        // In real implementation, would send via framed connection
        debug!("Publishing state: {:?}", state);
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_message_serialization() {
        let msg = MwComMessage::Subscribe { channel_id: 0x1001 };
        let json = serde_json::to_string(&msg).unwrap();
        assert!(json.contains("Subscribe"));

        let parsed: MwComMessage = serde_json::from_str(&json).unwrap();
        match parsed {
            MwComMessage::Subscribe { channel_id } => {
                assert_eq!(channel_id, 0x1001);
            }
            _ => panic!("Wrong message type"),
        }
    }

    #[test]
    fn test_speed_event() {
        let event = SpeedEvent {
            speed_kmh: 120.5,
            timestamp_ms: 1234567890,
            valid: true,
        };
        let json = serde_json::to_string(&event).unwrap();
        let parsed: SpeedEvent = serde_json::from_str(&json).unwrap();
        assert_eq!(parsed.speed_kmh, 120.5);
    }
}
EOF
```

---

## Step 6: Layer 4 - SOVD Adapter (PR #16)

### 6.1 Create sovd_adapter Rust Crate

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer4-adapter/sovd-adapter
cargo init --lib
```

#### Update Cargo.toml

```bash
cat > Cargo.toml << 'EOF'
[package]
name = "sovd_adapter"
version = "0.1.0"
edition = "2021"
description = "SOVD Adapter - Bridge between S-CORE diag_api and OpenSOVD"

[dependencies]
tokio = { version = "1.35", features = ["full"] }
async-trait = "0.1"
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"
tracing = "0.1"
thiserror = "1.0"
uuid = { version = "1.6", features = ["v4"] }

# Reference to local crates
cruise_diag = { path = "../../layer3-diagnostics/cruise-diag" }

[dev-dependencies]
tokio-test = "0.4"
EOF
```

#### Create src/lib.rs

```bash
cat > src/lib.rs << 'EOF'
//! SOVD Adapter - PR #16
//!
//! Bridges Eclipse S-CORE diag_api to Eclipse OpenSOVD
//! Implements DataProvider trait for SOVD server integration.

use async_trait::async_trait;
use cruise_diag::{DtcEntry, DtcStorage, FaultMonitor, FaultState};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use thiserror::Error;
use tokio::sync::RwLock;
use tracing::{debug, info};

/// SOVD Component identifier
pub type ComponentId = String;

/// SOVD Data resource
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataResource {
    pub id: String,
    pub name: String,
    pub value: serde_json::Value,
    pub readable: bool,
    pub writable: bool,
    pub category: DataCategory,
}

/// Data resource categories (ISO 17978-3)
#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum DataCategory {
    Current,
    Stored,
    Static,
}

/// SOVD Fault entry (ISO 17978-3 format)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SovdFault {
    pub id: String,
    pub dtc: String,
    pub description: String,
    pub status: SovdFaultStatus,
    pub occurrence_count: u32,
    pub first_occurrence: String,
    pub last_occurrence: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub freeze_frame: Option<serde_json::Value>,
}

/// SOVD Fault status (ISO 14229-1 mapping)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SovdFaultStatus {
    #[serde(rename = "testFailed")]
    pub test_failed: bool,
    #[serde(rename = "pendingDtc")]
    pub pending_dtc: bool,
    #[serde(rename = "confirmedDtc")]
    pub confirmed_dtc: bool,
    #[serde(rename = "warningIndicator")]
    pub warning_indicator: bool,
}

impl From<&cruise_diag::DtcStatus> for SovdFaultStatus {
    fn from(status: &cruise_diag::DtcStatus) -> Self {
        Self {
            test_failed: status.test_failed,
            pending_dtc: status.pending_dtc,
            confirmed_dtc: status.confirmed_dtc,
            warning_indicator: status.warning_indicator_requested,
        }
    }
}

impl From<DtcEntry> for SovdFault {
    fn from(entry: DtcEntry) -> Self {
        Self {
            id: format!("fault-{}", entry.id),
            dtc: entry.id,
            description: entry.description,
            status: SovdFaultStatus::from(&entry.status),
            occurrence_count: entry.occurrence_count,
            first_occurrence: entry.first_occurrence.to_rfc3339(),
            last_occurrence: entry.last_occurrence.to_rfc3339(),
            freeze_frame: entry.freeze_frame.map(|ff| serde_json::json!({
                "speed": ff.speed_kmh,
                "rpm": ff.engine_rpm,
                "timestamp": ff.timestamp.to_rfc3339(),
            })),
        }
    }
}

/// SOVD Mode (ISO 17978-3 mandatory)
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SovdMode {
    pub id: String,
    pub name: String,
    pub value: String,  // Required by ISO 17978-3
    pub active: bool,
}

/// DataProvider trait - Interface for SOVD server
#[async_trait]
pub trait DataProvider: Send + Sync {
    /// Get data resource by ID
    async fn get_data(&self, resource_id: &str) -> Result<DataResource, AdapterError>;

    /// Set data resource value
    async fn set_data(&self, resource_id: &str, value: serde_json::Value) -> Result<(), AdapterError>;

    /// List all data resources
    async fn list_resources(&self) -> Vec<DataResource>;
}

/// FaultProvider trait - Interface for fault/DTC handling
#[async_trait]
pub trait FaultProvider: Send + Sync {
    /// Get all faults
    async fn get_faults(&self) -> Vec<SovdFault>;

    /// Get specific fault
    async fn get_fault(&self, fault_id: &str) -> Result<SovdFault, AdapterError>;

    /// Clear specific fault
    async fn clear_fault(&self, fault_id: &str) -> Result<(), AdapterError>;

    /// Clear all faults
    async fn clear_all_faults(&self) -> Result<usize, AdapterError>;
}

/// ModeProvider trait - Interface for mode handling
#[async_trait]
pub trait ModeProvider: Send + Sync {
    /// Get all modes
    async fn get_modes(&self) -> Vec<SovdMode>;

    /// Get specific mode
    async fn get_mode(&self, mode_id: &str) -> Result<SovdMode, AdapterError>;

    /// Activate mode
    async fn activate_mode(&self, mode_id: &str) -> Result<(), AdapterError>;
}

/// Adapter errors
#[derive(Error, Debug)]
pub enum AdapterError {
    #[error("Resource not found: {0}")]
    NotFound(String),

    #[error("Resource not writable: {0}")]
    NotWritable(String),

    #[error("Invalid value: {0}")]
    InvalidValue(String),

    #[error("Operation failed: {0}")]
    OperationFailed(String),
}

/// SOVD Adapter - Main adapter implementation
pub struct SovdAdapter {
    component_id: ComponentId,
    dtc_storage: Arc<DtcStorage>,
    data_resources: Arc<RwLock<HashMap<String, DataResource>>>,
    modes: Arc<RwLock<HashMap<String, SovdMode>>>,
}

impl SovdAdapter {
    pub fn new(component_id: &str, dtc_storage: Arc<DtcStorage>) -> Self {
        Self {
            component_id: component_id.to_string(),
            dtc_storage,
            data_resources: Arc::new(RwLock::new(HashMap::new())),
            modes: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Register a data resource
    pub async fn register_resource(&self, resource: DataResource) {
        let mut resources = self.data_resources.write().await;
        info!("Registering resource: {}", resource.id);
        resources.insert(resource.id.clone(), resource);
    }

    /// Register a mode
    pub async fn register_mode(&self, mode: SovdMode) {
        let mut modes = self.modes.write().await;
        info!("Registering mode: {}", mode.id);
        modes.insert(mode.id.clone(), mode);
    }

    /// Get component ID
    pub fn component_id(&self) -> &str {
        &self.component_id
    }
}

#[async_trait]
impl DataProvider for SovdAdapter {
    async fn get_data(&self, resource_id: &str) -> Result<DataResource, AdapterError> {
        let resources = self.data_resources.read().await;
        resources
            .get(resource_id)
            .cloned()
            .ok_or_else(|| AdapterError::NotFound(resource_id.to_string()))
    }

    async fn set_data(&self, resource_id: &str, value: serde_json::Value) -> Result<(), AdapterError> {
        let mut resources = self.data_resources.write().await;

        if let Some(resource) = resources.get_mut(resource_id) {
            if !resource.writable {
                return Err(AdapterError::NotWritable(resource_id.to_string()));
            }
            resource.value = value;
            debug!("Updated resource {}: {:?}", resource_id, resource.value);
            Ok(())
        } else {
            Err(AdapterError::NotFound(resource_id.to_string()))
        }
    }

    async fn list_resources(&self) -> Vec<DataResource> {
        let resources = self.data_resources.read().await;
        resources.values().cloned().collect()
    }
}

#[async_trait]
impl FaultProvider for SovdAdapter {
    async fn get_faults(&self) -> Vec<SovdFault> {
        let dtcs = self.dtc_storage.get_all_dtcs().await;
        dtcs.into_iter().map(SovdFault::from).collect()
    }

    async fn get_fault(&self, fault_id: &str) -> Result<SovdFault, AdapterError> {
        // Extract DTC ID from fault ID (format: "fault-{dtc_id}")
        let dtc_id = fault_id.strip_prefix("fault-").unwrap_or(fault_id);

        self.dtc_storage
            .get_dtc(dtc_id)
            .await
            .map(SovdFault::from)
            .ok_or_else(|| AdapterError::NotFound(fault_id.to_string()))
    }

    async fn clear_fault(&self, fault_id: &str) -> Result<(), AdapterError> {
        let dtc_id = fault_id.strip_prefix("fault-").unwrap_or(fault_id);

        if self.dtc_storage.clear_dtc(dtc_id).await {
            info!("Cleared fault: {}", fault_id);
            Ok(())
        } else {
            Err(AdapterError::NotFound(fault_id.to_string()))
        }
    }

    async fn clear_all_faults(&self) -> Result<usize, AdapterError> {
        let count = self.dtc_storage.clear_all_dtcs().await;
        info!("Cleared {} faults", count);
        Ok(count)
    }
}

#[async_trait]
impl ModeProvider for SovdAdapter {
    async fn get_modes(&self) -> Vec<SovdMode> {
        let modes = self.modes.read().await;
        modes.values().cloned().collect()
    }

    async fn get_mode(&self, mode_id: &str) -> Result<SovdMode, AdapterError> {
        let modes = self.modes.read().await;
        modes
            .get(mode_id)
            .cloned()
            .ok_or_else(|| AdapterError::NotFound(mode_id.to_string()))
    }

    async fn activate_mode(&self, mode_id: &str) -> Result<(), AdapterError> {
        let mut modes = self.modes.write().await;

        // Deactivate all other modes
        for mode in modes.values_mut() {
            mode.active = mode.id == mode_id;
        }

        if modes.contains_key(mode_id) {
            info!("Activated mode: {}", mode_id);
            Ok(())
        } else {
            Err(AdapterError::NotFound(mode_id.to_string()))
        }
    }
}

/// Create a pre-configured adapter for Cruise Control ECU
pub fn create_cruise_adapter(dtc_storage: Arc<DtcStorage>) -> SovdAdapter {
    let adapter = SovdAdapter::new("cruise-ecu", dtc_storage);

    // Resources will be registered at runtime
    adapter
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_adapter_creation() {
        let storage = Arc::new(DtcStorage::new());
        let adapter = create_cruise_adapter(storage);
        assert_eq!(adapter.component_id(), "cruise-ecu");
    }

    #[tokio::test]
    async fn test_data_provider() {
        let storage = Arc::new(DtcStorage::new());
        let adapter = create_cruise_adapter(storage);

        // Register resource
        adapter.register_resource(DataResource {
            id: "speed".to_string(),
            name: "Current Speed".to_string(),
            value: serde_json::json!(120.5),
            readable: true,
            writable: false,
            category: DataCategory::Current,
        }).await;

        // Get resource
        let resource = adapter.get_data("speed").await.unwrap();
        assert_eq!(resource.value, serde_json::json!(120.5));
    }

    #[tokio::test]
    async fn test_fault_provider() {
        let storage = Arc::new(DtcStorage::new());
        storage.store_dtc("U0100", "Speed sensor lost", None).await;

        let adapter = create_cruise_adapter(storage);

        let faults = adapter.get_faults().await;
        assert_eq!(faults.len(), 1);
        assert_eq!(faults[0].dtc, "U0100");
        assert!(faults[0].status.confirmed_dtc);
    }
}
EOF
```

---

## Step 7: Layer 5 - OpenSOVD Server (Issue #553 Fixes)

### 7.1 Clone and Setup OpenSOVD

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer5-sovd

# Clone OpenSOVD (our fork with fixes)
git clone https://github.com/eclipse-opendut/opensovd-core.git opensovd-server
cd opensovd-server

# Create branch for our fixes
git checkout -b issue-553-fixes
```

### 7.2 Document the API Fixes

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer5-sovd/api-fixes
```

#### Create issue_553_fixes.md

```bash
cat > issue_553_fixes.md << 'EOF'
# Issue #553 - API Compliance Fixes

## Summary
8 fixes for ISO 17978-3 compliance in OpenSOVD.

## Fixes Applied

### Fix 1: Mode.value Mandatory (data.rs)
**File:** `opensovd-core/src/data.rs`
```rust
// BEFORE
pub struct Mode {
    pub id: String,
    pub name: String,
    pub active: bool,
}

// AFTER
pub struct Mode {
    pub id: String,
    pub name: String,
    pub value: String,  // ISO 17978-3 §7.4 - MANDATORY
    pub active: bool,
}
```

### Fix 2: Bulk-data Category Enum (bulkdata.rs)
**File:** `opensovd-core/src/bulkdata.rs`
```rust
// BEFORE
pub category: String,

// AFTER
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "lowercase")]
pub enum BulkDataCategory {
    Measurement,
    Calibration,
    Logging,
    Freeze,
}
pub category: BulkDataCategory,
```

### Fix 3: Component Restart Endpoint (component.rs)
**File:** `opensovd-server/src/routes/entities/component.rs`
```rust
// ADDED
.route("/components/:id/status/restart", put(restart_component))

async fn restart_component(
    Path(id): Path<String>,
) -> Result<Json<RestartResponse>, ApiError> {
    // Implementation
}
```

### Fix 4-8: See detailed documentation
EOF
```

---

## Step 8: Layer 6 - Dashboard

### 8.1 Create Dashboard Web Application

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer6-dashboard/web
```

#### Create index.html

```bash
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cruise Control Dashboard - Eclipse SDV Hackathon 2026</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0a0a0a;
            color: #ffffff;
            min-height: 100vh;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 2px solid #00d4aa;
            padding-bottom: 20px;
        }

        .header h1 {
            font-size: 2.5em;
            color: #00d4aa;
        }

        .header .subtitle {
            color: #888;
            margin-top: 10px;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }

        .card {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 25px;
            border: 1px solid #333;
        }

        .card h2 {
            color: #00d4aa;
            margin-bottom: 20px;
            font-size: 1.3em;
            border-bottom: 1px solid #333;
            padding-bottom: 10px;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #222;
        }

        .metric:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #888;
        }

        .metric-value {
            font-size: 1.4em;
            font-weight: bold;
        }

        .metric-value.ok { color: #00d4aa; }
        .metric-value.warning { color: #ffaa00; }
        .metric-value.error { color: #ff4444; }

        .speed-display {
            text-align: center;
            padding: 30px;
        }

        .speed-value {
            font-size: 5em;
            font-weight: bold;
            color: #00d4aa;
        }

        .speed-unit {
            font-size: 1.5em;
            color: #888;
        }

        .state-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            text-transform: uppercase;
        }

        .state-badge.standby { background: #333; color: #888; }
        .state-badge.active { background: #00d4aa; color: #000; }
        .state-badge.disabling { background: #ffaa00; color: #000; }
        .state-badge.disabled { background: #ff4444; color: #fff; }

        .dtc-list {
            max-height: 200px;
            overflow-y: auto;
        }

        .dtc-item {
            background: #222;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 10px;
        }

        .dtc-code {
            color: #ff4444;
            font-weight: bold;
            font-family: monospace;
        }

        .dtc-desc {
            color: #aaa;
            font-size: 0.9em;
            margin-top: 5px;
        }

        .controls {
            display: flex;
            gap: 10px;
            margin-top: 20px;
        }

        button {
            flex: 1;
            padding: 12px 20px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            cursor: pointer;
            transition: all 0.3s;
        }

        button.primary {
            background: #00d4aa;
            color: #000;
        }

        button.danger {
            background: #ff4444;
            color: #fff;
        }

        button:hover {
            opacity: 0.8;
            transform: translateY(-2px);
        }

        .api-status {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #1a1a1a;
            padding: 10px 20px;
            border-radius: 8px;
            border: 1px solid #333;
        }

        .status-dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 8px;
        }

        .status-dot.connected { background: #00d4aa; }
        .status-dot.disconnected { background: #ff4444; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Cruise Control Dashboard</h1>
        <div class="subtitle">Eclipse SDV Hackathon 2026 | S-CORE ↔ OpenSOVD Demo</div>
    </div>

    <div class="dashboard">
        <!-- Speed Display -->
        <div class="card">
            <h2>Current Speed</h2>
            <div class="speed-display">
                <div class="speed-value" id="speed">---</div>
                <div class="speed-unit">km/h</div>
            </div>
        </div>

        <!-- Cruise Status -->
        <div class="card">
            <h2>Cruise Control Status</h2>
            <div class="metric">
                <span class="metric-label">State</span>
                <span class="state-badge standby" id="state">STANDBY</span>
            </div>
            <div class="metric">
                <span class="metric-label">Target Speed</span>
                <span class="metric-value" id="target">--- km/h</span>
            </div>
            <div class="metric">
                <span class="metric-label">Throttle Output</span>
                <span class="metric-value" id="throttle">0%</span>
            </div>
            <div class="controls">
                <button class="primary" onclick="enableCruise()">Enable</button>
                <button class="danger" onclick="disableCruise()">Disable</button>
            </div>
        </div>

        <!-- Fault Status -->
        <div class="card">
            <h2>Fault Status</h2>
            <div class="metric">
                <span class="metric-label">Fault Active</span>
                <span class="metric-value ok" id="fault-status">NO</span>
            </div>
            <div class="metric">
                <span class="metric-label">DTC Count</span>
                <span class="metric-value" id="dtc-count">0</span>
            </div>
            <div class="controls">
                <button class="danger" onclick="injectFault()">Inject Fault</button>
                <button class="primary" onclick="clearFault()">Clear Fault</button>
            </div>
        </div>

        <!-- DTC List -->
        <div class="card">
            <h2>Diagnostic Trouble Codes</h2>
            <div class="dtc-list" id="dtc-list">
                <div style="color: #888; text-align: center; padding: 20px;">
                    No active DTCs
                </div>
            </div>
            <div class="controls">
                <button class="primary" onclick="refreshDtcs()">Refresh DTCs</button>
                <button class="danger" onclick="clearAllDtcs()">Clear All</button>
            </div>
        </div>

        <!-- System Info -->
        <div class="card">
            <h2>System Information</h2>
            <div class="metric">
                <span class="metric-label">Component</span>
                <span class="metric-value">cruise-ecu</span>
            </div>
            <div class="metric">
                <span class="metric-label">SOVD API</span>
                <span class="metric-value ok">v1</span>
            </div>
            <div class="metric">
                <span class="metric-label">Protocol</span>
                <span class="metric-value">ISO 17978-3</span>
            </div>
        </div>

        <!-- API Endpoints -->
        <div class="card">
            <h2>REST API Endpoints</h2>
            <div class="metric">
                <span class="metric-label">Status</span>
                <code style="color: #00d4aa;">GET /sovd/v1/components/cruise-ecu</code>
            </div>
            <div class="metric">
                <span class="metric-label">Faults</span>
                <code style="color: #00d4aa;">GET /sovd/v1/components/cruise-ecu/faults</code>
            </div>
            <div class="metric">
                <span class="metric-label">Restart</span>
                <code style="color: #ffaa00;">PUT /sovd/v1/components/cruise-ecu/status/restart</code>
            </div>
        </div>
    </div>

    <div class="api-status">
        <span class="status-dot connected" id="status-dot"></span>
        <span id="connection-status">Connected to SOVD Gateway</span>
    </div>

    <script>
        const API_BASE = 'http://localhost:7690/sovd/v1';
        const COMPONENT = 'cruise-ecu';

        // State
        let currentState = {
            speed: 0,
            state: 'STANDBY',
            target: 0,
            throttle: 0,
            faultActive: false,
            dtcCount: 0
        };

        // Update UI
        function updateUI() {
            document.getElementById('speed').textContent = currentState.speed.toFixed(0);
            document.getElementById('target').textContent = `${currentState.target.toFixed(0)} km/h`;
            document.getElementById('throttle').textContent = `${(currentState.throttle * 100).toFixed(0)}%`;

            const stateEl = document.getElementById('state');
            stateEl.textContent = currentState.state;
            stateEl.className = `state-badge ${currentState.state.toLowerCase()}`;

            const faultEl = document.getElementById('fault-status');
            faultEl.textContent = currentState.faultActive ? 'YES' : 'NO';
            faultEl.className = `metric-value ${currentState.faultActive ? 'error' : 'ok'}`;

            document.getElementById('dtc-count').textContent = currentState.dtcCount;
        }

        // Fetch status from SOVD API
        async function fetchStatus() {
            try {
                const response = await fetch(`${API_BASE}/components/${COMPONENT}/data/status`);
                if (response.ok) {
                    const data = await response.json();
                    currentState = { ...currentState, ...data };
                    updateUI();
                    setConnected(true);
                }
            } catch (error) {
                console.error('Failed to fetch status:', error);
                setConnected(false);
            }
        }

        // Fetch DTCs
        async function refreshDtcs() {
            try {
                const response = await fetch(`${API_BASE}/components/${COMPONENT}/faults`);
                if (response.ok) {
                    const data = await response.json();
                    displayDtcs(data.faults || []);
                    currentState.dtcCount = (data.faults || []).length;
                    updateUI();
                }
            } catch (error) {
                console.error('Failed to fetch DTCs:', error);
            }
        }

        function displayDtcs(dtcs) {
            const list = document.getElementById('dtc-list');
            if (dtcs.length === 0) {
                list.innerHTML = '<div style="color: #888; text-align: center; padding: 20px;">No active DTCs</div>';
                return;
            }

            list.innerHTML = dtcs.map(dtc => `
                <div class="dtc-item">
                    <div class="dtc-code">${dtc.dtc}</div>
                    <div class="dtc-desc">${dtc.description}</div>
                </div>
            `).join('');
        }

        // Control functions
        async function enableCruise() {
            try {
                await fetch(`${API_BASE}/components/${COMPONENT}/data/target_speed`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ value: 120 })
                });
                await fetch(`${API_BASE}/components/${COMPONENT}/data/cruise_enable`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ value: true })
                });
            } catch (error) {
                console.error('Failed to enable cruise:', error);
            }
        }

        async function disableCruise() {
            try {
                await fetch(`${API_BASE}/components/${COMPONENT}/data/cruise_enable`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ value: false })
                });
            } catch (error) {
                console.error('Failed to disable cruise:', error);
            }
        }

        async function injectFault() {
            try {
                await fetch(`${API_BASE}/components/${COMPONENT}/data/inject_fault`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ value: true })
                });
            } catch (error) {
                console.error('Failed to inject fault:', error);
            }
        }

        async function clearFault() {
            try {
                await fetch(`${API_BASE}/components/${COMPONENT}/status/restart`, {
                    method: 'PUT'
                });
            } catch (error) {
                console.error('Failed to clear fault:', error);
            }
        }

        async function clearAllDtcs() {
            try {
                await fetch(`${API_BASE}/components/${COMPONENT}/faults`, {
                    method: 'DELETE'
                });
                refreshDtcs();
            } catch (error) {
                console.error('Failed to clear DTCs:', error);
            }
        }

        function setConnected(connected) {
            const dot = document.getElementById('status-dot');
            const status = document.getElementById('connection-status');
            if (connected) {
                dot.className = 'status-dot connected';
                status.textContent = 'Connected to SOVD Gateway';
            } else {
                dot.className = 'status-dot disconnected';
                status.textContent = 'Disconnected';
            }
        }

        // Polling
        setInterval(fetchStatus, 500);
        setInterval(refreshDtcs, 2000);

        // Initial load
        fetchStatus();
        refreshDtcs();
    </script>
</body>
</html>
EOF
```

#### Create server.py

```bash
cat > server.py << 'EOF'
#!/usr/bin/env python3
"""
Dashboard HTTP Server
Serves the dashboard and proxies API requests to SOVD gateway
"""

import asyncio
import json
from aiohttp import web, ClientSession

SOVD_GATEWAY = "http://localhost:7690"
PORT = 8080

# Simulated state (for demo without full backend)
demo_state = {
    "speed": 0.0,
    "state": "STANDBY",
    "target": 120.0,
    "throttle": 0.0,
    "faultActive": False,
    "dtcCount": 0
}

demo_dtcs = []

async def index(request):
    """Serve main dashboard"""
    with open("index.html", "r") as f:
        return web.Response(text=f.read(), content_type="text/html")

async def get_status(request):
    """Get current status"""
    return web.json_response(demo_state)

async def get_faults(request):
    """Get all faults"""
    return web.json_response({"faults": demo_dtcs})

async def inject_fault(request):
    """Inject a fault"""
    global demo_state, demo_dtcs
    demo_state["faultActive"] = True
    demo_state["state"] = "DISABLING"
    demo_dtcs.append({
        "id": "fault-U0100",
        "dtc": "U0100",
        "description": "Lost Communication with Speed Sensor",
        "status": {
            "testFailed": True,
            "pendingDtc": True,
            "confirmedDtc": True,
            "warningIndicator": True
        }
    })
    demo_state["dtcCount"] = len(demo_dtcs)
    return web.json_response({"success": True})

async def clear_fault(request):
    """Clear fault and restart"""
    global demo_state, demo_dtcs
    demo_state["faultActive"] = False
    demo_state["state"] = "STANDBY"
    demo_state["speed"] = 0.0
    demo_dtcs.clear()
    demo_state["dtcCount"] = 0
    return web.json_response({"success": True})

async def simulation_loop():
    """Simulate vehicle dynamics"""
    global demo_state
    while True:
        if demo_state["state"] == "ACTIVE" and not demo_state["faultActive"]:
            # Speed converges to target
            error = demo_state["target"] - demo_state["speed"]
            demo_state["throttle"] = min(1.0, max(-1.0, error * 0.1))
            demo_state["speed"] += demo_state["throttle"] * 2.0
            demo_state["speed"] = max(0.0, demo_state["speed"])
        elif demo_state["state"] == "DISABLING":
            demo_state["speed"] = max(0.0, demo_state["speed"] - 1.0)
            demo_state["throttle"] = 0.0
            if demo_state["speed"] < 5.0:
                demo_state["state"] = "DISABLED"
                demo_state["speed"] = 0.0

        await asyncio.sleep(0.05)  # 50ms loop

async def start_simulation(app):
    """Start simulation task"""
    asyncio.create_task(simulation_loop())

app = web.Application()
app.router.add_get("/", index)
app.router.add_get("/sovd/v1/components/cruise-ecu/data/status", get_status)
app.router.add_get("/sovd/v1/components/cruise-ecu/faults", get_faults)
app.router.add_put("/sovd/v1/components/cruise-ecu/data/inject_fault", inject_fault)
app.router.add_put("/sovd/v1/components/cruise-ecu/status/restart", clear_fault)
app.router.add_put("/sovd/v1/components/cruise-ecu/data/cruise_enable",
    lambda r: web.json_response({"success": True}))
app.router.add_static("/static", "static")

app.on_startup.append(start_simulation)

if __name__ == "__main__":
    print(f"Dashboard running at http://localhost:{PORT}")
    web.run_app(app, port=PORT)
EOF
```

---

## Step 9: Docker Compose Setup

### 9.1 Create Docker Compose File

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/docker/compose
```

#### Create docker-compose.yaml

```bash
cat > docker-compose.yaml << 'EOF'
version: '3.8'

services:
  # Layer 0: Car Simulation + Cruise ECU
  car-sim:
    build:
      context: ../../layer0-ecu/car-simulation
      dockerfile: Dockerfile
    networks:
      - score-network
    volumes:
      - /dev/shm:/dev/shm

  cruise-ecu:
    build:
      context: ../../layer0-ecu/cruise-control
      dockerfile: Dockerfile
    networks:
      - score-network
    volumes:
      - /dev/shm:/dev/shm
    depends_on:
      - someipd

  # Layer 1-2: S-CORE Middleware
  someipd:
    image: ghcr.io/eclipse-score/someipd:latest
    networks:
      - score-network
    volumes:
      - ../../layer1-score/config/someip_config.json:/etc/vsomeip/vsomeip.json
      - /dev/shm:/dev/shm
    ports:
      - "30509:30509/udp"

  gatewayd:
    image: ghcr.io/eclipse-score/gatewayd:latest
    networks:
      - score-network
    volumes:
      - ../../layer2-gateway/gatewayd/config.yaml:/etc/gatewayd/config.yaml
      - /dev/shm:/dev/shm
    ports:
      - "7700:7700"
    depends_on:
      - someipd

  # Layer 3-4: Bridge + Adapter
  cruise-bridge:
    build:
      context: ../..
      dockerfile: docker/images/cruise-bridge.Dockerfile
    networks:
      - score-network
    environment:
      - GATEWAY_ADDR=gatewayd:7700
      - SOVD_ADDR=sovd-gateway:7690
    depends_on:
      - gatewayd
      - sovd-gateway

  # Layer 5: SOVD Gateway
  sovd-gateway:
    build:
      context: ../../layer5-sovd/opensovd-server
      dockerfile: Dockerfile
    networks:
      - score-network
    ports:
      - "7690:7690"
    environment:
      - RUST_LOG=info

  # Layer 6: Dashboard
  dashboard:
    build:
      context: ../../layer6-dashboard/web
      dockerfile: Dockerfile
    networks:
      - score-network
    ports:
      - "8080:8080"
    depends_on:
      - sovd-gateway

networks:
  score-network:
    driver: bridge
EOF
```

### 9.2 Create Dockerfiles

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/docker/images
```

#### Create cruise-bridge.Dockerfile

```bash
cat > cruise-bridge.Dockerfile << 'EOF'
FROM rust:1.75-slim as builder

WORKDIR /app
COPY layer3-diagnostics/cruise-diag ./cruise-diag
COPY layer3-diagnostics/cruise-bridge ./cruise-bridge
COPY layer4-adapter/sovd-adapter ./sovd-adapter

WORKDIR /app/cruise-bridge
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /app/cruise-bridge/target/release/cruise_bridge /usr/local/bin/
CMD ["cruise_bridge"]
EOF
```

#### Create dashboard.Dockerfile

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer6-dashboard/web

cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["python3", "server.py"]
EOF

echo "aiohttp>=3.9.0" > requirements.txt
```

---

## Step 10: Testing with openDuT

### 10.1 Create Test Configuration

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/testing/opendut
```

#### Create test_scenario.yaml

```bash
cat > test_scenario.yaml << 'EOF'
# openDuT Test Scenario for Cruise Control Diagnostics
name: cruise-control-fault-injection
description: "Test speed signal loss detection and DTC storage"

topology:
  devices:
    - id: cruise-ecu
      type: ecu
      image: cruise-ecu:latest

    - id: car-sim
      type: simulator
      image: car-sim:latest

    - id: sovd-gateway
      type: service
      image: opensovd-gateway:latest

  connections:
    - from: car-sim
      to: cruise-ecu
      protocol: someip

    - from: cruise-ecu
      to: sovd-gateway
      protocol: tcp

test_cases:
  - name: TC001_NormalOperation
    description: "Verify cruise control operates normally"
    steps:
      - action: enable_cruise
        target: cruise-ecu
        params:
          speed: 120
      - wait: 5s
      - assert:
          target: cruise-ecu
          condition: state == ACTIVE
      - assert:
          target: sovd-gateway
          condition: faults.count == 0

  - name: TC002_SpeedSignalLoss
    description: "Verify fault detection on speed signal loss"
    steps:
      - action: enable_cruise
        target: cruise-ecu
        params:
          speed: 120
      - wait: 2s
      - action: fail_sensor
        target: car-sim
        params:
          sensor: speed
      - wait: 6s  # Wait for debounce
      - assert:
          target: cruise-ecu
          condition: state == DISABLING
      - assert:
          target: sovd-gateway
          condition: faults.count == 1
      - assert:
          target: sovd-gateway
          condition: faults[0].dtc == "U0100"

  - name: TC003_Recovery
    description: "Verify system recovery after fault clear"
    steps:
      - action: restore_sensor
        target: car-sim
        params:
          sensor: speed
      - action: restart
        target: cruise-ecu
      - wait: 3s
      - assert:
          target: cruise-ecu
          condition: state == STANDBY
      - assert:
          target: sovd-gateway
          condition: faults.count == 0
EOF
```

---

## Step 11: Build & Run Everything

### 11.1 Build All Components

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026

# Build Layer 0 (C++)
cd layer0-ecu/cruise-control
bazel build :cruise_ecu

cd ../car-simulation
bazel build :car_sim

# Build Layer 3-4 (Rust)
cd ../../layer3-diagnostics/cruise-diag
cargo build --release

cd ../cruise-bridge
cargo build --release

cd ../../layer4-adapter/sovd-adapter
cargo build --release

# Build Layer 5 (if using local build)
cd ../../layer5-sovd/opensovd-server
cargo build --release

# Return to root
cd ../..
```

### 11.2 Run with Docker Compose

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/docker/compose

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop all
docker-compose down
```

### 11.3 Run Dashboard Standalone (for testing)

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026/layer6-dashboard/web
python3 server.py

# Open browser: http://localhost:8080
```

---

## Step 12: Verify Installation

### 12.1 Test API Endpoints

```bash
# Test SOVD Gateway
curl http://localhost:7690/sovd/v1/version

# Get component info
curl http://localhost:7690/sovd/v1/components/cruise-ecu

# Get faults
curl http://localhost:7690/sovd/v1/components/cruise-ecu/faults

# Restart component
curl -X PUT http://localhost:7690/sovd/v1/components/cruise-ecu/status/restart
```

### 12.2 Run Tests

```bash
cd ~/Projects/EclipseSDV-Hackathon-2026

# Rust tests
cd layer3-diagnostics/cruise-diag
cargo test

cd ../cruise-bridge
cargo test

cd ../../layer4-adapter/sovd-adapter
cargo test

# C++ tests
cd ../../layer0-ecu/cruise-control
bazel test :cruise_control_test
```

---

## Summary: Complete Directory Structure

```
EclipseSDV-Hackathon-2026/
├── layer0-ecu/
│   ├── cruise-control/
│   │   ├── cruise_control.h
│   │   ├── cruise_control.cpp
│   │   ├── main.cpp
│   │   ├── cruise_control_test.cpp
│   │   └── BUILD.bazel
│   └── car-simulation/
│       ├── car_simulation.h
│       ├── car_simulation.cpp
│       └── BUILD.bazel
├── layer1-score/
│   └── config/
│       ├── someip_config.json
│       └── lola_config.yaml
├── layer2-gateway/
│   ├── gatewayd/
│   │   └── config.yaml
│   └── someipd/
│       └── vsomeipd.json
├── layer3-diagnostics/
│   ├── cruise-diag/
│   │   ├── Cargo.toml
│   │   └── src/lib.rs
│   └── cruise-bridge/
│       ├── Cargo.toml
│       └── src/lib.rs
├── layer4-adapter/
│   └── sovd-adapter/
│       ├── Cargo.toml
│       └── src/lib.rs
├── layer5-sovd/
│   ├── opensovd-server/
│   └── api-fixes/
│       └── issue_553_fixes.md
├── layer6-dashboard/
│   └── web/
│       ├── index.html
│       ├── server.py
│       ├── requirements.txt
│       └── Dockerfile
├── testing/
│   └── opendut/
│       └── test_scenario.yaml
├── docker/
│   ├── compose/
│   │   └── docker-compose.yaml
│   └── images/
│       └── cruise-bridge.Dockerfile
└── docs/
```

---

## Quick Start Commands

```bash
# 1. Create project
mkdir -p ~/Projects/EclipseSDV-Hackathon-2026 && cd $_

# 2. Run setup script (creates all files above)
# (Copy this entire document and run the commands)

# 3. Build everything
./build_all.sh

# 4. Start services
docker-compose -f docker/compose/docker-compose.yaml up -d

# 5. Open dashboard
open http://localhost:8080

# 6. Run tests
cargo test --workspace
bazel test //...
```

---

*Document prepared for Eclipse SDV Hackathon 2026*
