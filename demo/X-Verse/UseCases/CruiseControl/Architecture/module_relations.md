
# Module Relations Documentation

## References

|Name| repo|
|-------|-------|
|Carla-Client| [carla-simulator-bridge](https://github.com/The-Xverse/carla-simulator-bridge/blob/steering_control_integrated/examples/manual_control_steeringwheel_zenoh.py)|
|EGOVehicle| [zenoh-core](https://github.com/The-Xverse/zenoh-core/blob/main/vehicle/src/main.rs)|
|Simulink_Python| [simulink-vecu](https://github.com/The-Xverse/simulink-vecu/tree/delta_based_controller)|
|Android| [chat](#2-conversation-with-the-x-verse-team)|


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
## 2. Conversation with the X-Verse team
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
[Open the architecture diagram](Autoverse_Cruise_Control_US.drawio)



