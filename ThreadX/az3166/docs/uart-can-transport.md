# UART-simulated CAN transport (SLCAN)

The AZ3166 has no CAN transceiver. The controller instead exchanges CAN frames
with X-Verse over the ST-LINK virtual COM port, using the Lawicell **SLCAN**
ASCII protocol. SLCAN is the de-facto serial-line CAN adapter protocol. That
means the frames reach X-Verse through stock components:

- python-can's `slcan` interface, which the unchanged Zenoh2CAN bridge loads
  with `"bus_type": "slcan"`.
- Linux `slcand`, which exposes the board as a regular SocketCAN interface
  (`slcan0`).

The lighting payload contract is unchanged; see the
[CAN lighting contract](../../docs/can-lighting-contract.md). The firmware
compiles the same `../src/lights_protocol.c` as the Linux controller.

```text
X-Verse VCU ─ Zenoh ─▶ Zenoh2CAN bridge ─ python-can slcan ─▶ /dev/ttyACM*
                                                               │ USB (ST-LINK VCP)
                                                               ▼
                       AZ3166 USART6 ◀─ "t1F18…\r" ─ ThreadX ingress thread
CARLA lights ◀─ Zenoh ◀─ bridge ◀─ "t1F48…\r" ◀─ ThreadX control thread ─▶ LEDs/OLED
```

## Serial link

| Setting | Value |
| --- | --- |
| Port | ST-LINK/V2-1 virtual COM port (`/dev/serial/by-id/usb-STMicroelectronics_STM32_STLink_*-if02`) |
| MCU side | USART6, PA11 TX / PA12 RX |
| Format | 115200 baud, 8N1, no flow control |
| Line terminator | `\r` (a `\n` is ignored, so CRLF terminals work) |

The port has a single owner. Run the bridge, `slcand`, the hardware test or a
terminal, but only one at a time. Opening the port does not reset the MCU.

## Supported SLCAN subset

| Host sends | Meaning | Board replies |
| --- | --- | --- |
| `O` | Open the channel (X-Verse link up) | `\r`, then the current `0x1F4` command frame. Idempotent. |
| `C` | Close the channel | `\r`. Lamps go off locally (fail-safe). Idempotent. |
| `S0`–`S8`, `sXXXX` | Nominal bitrate or BTR | `\r` while closed, BELL while open. Stored only; the UART does not emulate bit timing. |
| `Z0` | Timestamps off | `\r` while closed. `Z1` is not supported (BELL). |
| `V` | Version | `V1010\r` |
| `N` | Serial number | `NAZ31\r` |
| `F` | Status flags | `F00\r`, or `F08\r` (data overrun) if any frame or byte was lost since the last `F`. BELL while closed. |
| `tIIIL<data>` / `TIIIIIIIIL<data>` | Standard / extended data frame onto the bus | `z\r` / `Z\r` while open; BELL while closed |
| `rIIIL` / `RIIIIIIIIL` | Remote frame | `z\r` / `Z\r` while open; never actuates |
| anything else, or more than 26 characters | — | BELL (`\a`) |

The simulated bus has two nodes: the host and the controller. Every
well-formed frame the host sends while the channel is open is acknowledged,
then passed to `lights_decode()`. Only a standard, 8-byte, non-remote `0x1F1`
frame actuates; all other frames are counted as *rejected*.

## Frames from the board

| ID | DLC | When | Content |
| --- | --- | --- | --- |
| `0x1F4` | 8 | On channel open, on every accepted `0x1F1`, and on input timeout (if enabled) | Byte 0 bit 0 reverse, bit 1 brake; other bytes zero (unchanged contract) |
| `0x1F5` | 8 | Every second while open (ThreadX timer) | Diagnostic heartbeat, below |

`0x1F5` diagnostic heartbeat. The Zenoh2CAN profile has no mapping for this ID,
so the bridge ignores it.

| Byte | Content |
| --- | --- |
| 0 | bit 0 reverse, bit 1 brake, bit 2 stale (input timeout), bit 3 losses seen (UART overrun, ingress/queue overflow or TX drop), bit 4 OLED working |
| 1–2 | Accepted `0x1F1` frames, little-endian, modulo 65536 |
| 3 | Rejected frames, modulo 256 |
| 4 | Protocol line errors (BELL replies), modulo 256 |
| 5–7 | Uptime in seconds, little-endian |

## Link and safety behaviour

- **Boot:** lamps are off and the channel is closed. Nothing is transmitted until a host sends `O`.
- **Open:** the board immediately reports its current `0x1F4` command, so a newly started bridge publishes a defined light state to Zenoh.
- **Hold:** as on Linux, the last command is held until the next input. Build with `-DZONAL_TIMEOUT_MS=N` to turn the lamps off after N ms without input, for periodic sources only.
- **Close:** when python-can shuts down (bridge stop) it sends `C`. The board turns both lamps off and transmits nothing more. This replaces the Linux SIGTERM path. On the MCU, a lost host is the shutdown event, because there is no process signal.
- **Fault:** ThreadX stack overflow, a failed ThreadX call, a CPU fault or an unexpected interrupt stops the board with the RGB LED blue and the lamps off.

## Timing (measured on the board, see [evidence](../../artifacts/az3166-uart-can/results.json))

- `0x1F1` → `0x1F4` round trip through USB, UART and ThreadX: median 3.5 ms, max 4.5 ms over all 256 status values.
- Zenoh `vcu/control/status` → Zenoh `vehicle/lights/*` through the real bridge and board: about 10 ms.
- Heartbeat period: 0.994 s. The core runs from the factory-trimmed HSI RC oscillator (±1%), which is ~0.6% fast on this board. That is well within UART tolerance and irrelevant for lamp control.
