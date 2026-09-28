
# Module Relations Documentation

## References

|Name| repo|
|-------|-------|
|Carla-Client| [carla-simulator-bridge](https://github.com/The-Xverse/carla-simulator-bridge/blob/steering_control_integrated/examples/manual_control_steeringwheel_zenoh.py)|
|EGOVehicle| [zenoh-core](https://github.com/The-Xverse/zenoh-core/blob/main/vehicle/src/main.rs)|
|Simulink_Python| [simulink-vecu](https://github.com/The-Xverse/simulink-vecu/tree/delta_based_controller)|
|Android| [chat](#3-conversation-with-the-x-verse-team)|
|ADAS| [Interface](#2-interface-germany-team-s-core-adas)|

---

## 1. Dependency Matrix (by Interface name)

| Provider ↓ \ Consumer→ | Carla-Client | EGOVehicle | Simulink | Android |
|--|-------|------------|----------|---------|
| **Carla-Client** | <span style="color: red;">cc_engage</span> | <span style="color: red;">cc_engage</span> | braking_status<br>cc_delta_speed |  |
| **EGOVehicle** |  |  | clock_status<br>velocity_status | velocity_status |
| **Simulink** |  | actuation_cmd |  | <span style="color: red;">cc_target_speed</span> |
| **Android** |  | <span style="color: red;">cc_engage</span> | <span style="color: red;">cc_engage</span> | <span style="color: red;">cc_target_speed</span><br><span style="color: red;">cc_engage</span> |

### Detected Ambiguities: 
The <span style="color: red;">cc_engage </span>and <span style="color: red;">cc_target_speed</span> are present in 2 providers.
#### Explanation 
For cc_engage is because the CC can be engage in Carla-Client (steering wheel) and in Android touchscreen. For the cc_target_speed Simulink and Android needs a explanation.
#### Remarks
This is very common in MQTT protocol but usually avoided in Zenoh protocol [[Bug](https://github.com/eclipse-zenoh/zenoh/issues/503)].

For SOME/IP protocol this is not possible because one service → one provider.

---
## 2. Interface Germany Team S-CORE ADAS
```
//-------------------- Input ----------------------------
struct EgoKinematics {
    float speed_kmh{0.0f};    // Current vehicle speed in km/h
    int64_t timestamp_ns{0};  // Timestamp in nanoseconds
};
 
// HMI -> Controller command
struct CruiseControlCommand {
    bool engaged{false};           // Cruise control engagement state (true = enabled)
    float target_speed_kmh{0.0f};  // Target speed set by user in km/h
    int64_t timestamp_ns{0};       // Timestamp in nanoseconds
};
 
//--------------------Output----------------
struct LongitudinalRequest {
    float desired_accel_mps2{0.0f};  // Desired acceleration in m/s^2
};
```
---
## 3. Conversation with the X-Verse team
```
Android APP atual, antes do use case da BMW:
 
Publish
- target_speed: 'adas/cruise_control/target_speed' 
    TODO: deve mudar para delta_speed: 'adas/cruise_control/delta_speed' pra ficar de acordo com a versão mais estável
- cc_enable: 'adas/cruise_control/engage'
 
Subscribe
- target_speed: 'adas/cruise_control/target_speed'
- cc_enable: 'adas/cruise_control/engage'
- velocity_status: 'vehicle/status/velocity_status'
```

# Architecture diagrams
[Open the architecture diagram](BMW_Cruise_Control.drawio)



