#!/usr/bin/env python3
"""Live X-Verse + CARLA integration test for the AZ3166 lighting controller.

Run while the X-Verse stack (`run_autoverse.py --enable-camera-display
--vcu-zenoh`), a Zenoh router on 7447 and the Zenoh2CAN bridge with the SLCAN
profile are up. The test operates Vehicle Manual Control like a driver: it
presses the brake (S) and reverse toggle (Q) keys in that window through
XTEST. It then follows the real chain:

  Manual Control -> X-Verse VCU -> Zenoh2CAN -> SLCAN/UART -> ThreadX on AZ3166
  -> Zenoh2CAN -> X-Verse virtual vehicle -> CARLA actor light state

Each step records Zenoh samples, the CARLA light mask and a rear camera image.
Keys are sent only while the Manual Control window has the input focus.
"""
import argparse
import json
import queue
import sys
import threading
import time
from pathlib import Path

import carla
import zenoh
from Xlib import X, XK, display as xdisplay
from Xlib.ext import xtest
from Xlib.protocol import event as xevent

WINDOW_TITLE = "Vehicle Manual Control"
REVERSE, BRAKE = int(carla.VehicleLightState.Reverse), int(carla.VehicleLightState.Brake)


def wait_for(predicate, timeout=10.0, step=0.02):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        value = predicate()
        if value:
            return value
        time.sleep(step)
    raise AssertionError(f"timed out after {timeout}s")


class Keyboard:
    """XTEST key events, delivered only to the Manual Control window."""

    def __init__(self, title):
        self.display = xdisplay.Display()
        assert self.display.has_extension("XTEST"), "X server lacks XTEST"
        self.window = self._find(title)
        assert self.window is not None, f"window '{title}' not found"

    def _find(self, title):
        root = self.display.screen().root
        utf8 = self.display.intern_atom("UTF8_STRING")
        names = (self.display.intern_atom("_NET_WM_NAME"), utf8)
        clients = root.get_full_property(self.display.intern_atom("_NET_CLIENT_LIST"), X.AnyPropertyType)
        for window_id in (clients.value if clients else []):
            window = self.display.create_resource_object("window", window_id)
            name = window.get_full_property(*names)
            if (name and name.value.decode(errors="replace") == title) or window.get_wm_name() == title:
                return window
        return None

    def _focused(self):
        focus = self.display.get_input_focus().focus
        while not isinstance(focus, int) and focus is not None:
            if focus.id == self.window.id:
                return True
            focus = focus.query_tree().parent
            if focus.id == self.display.screen().root.id:
                return False
        return False

    def focus(self):
        root = self.display.screen().root
        active = self.display.intern_atom("_NET_ACTIVE_WINDOW")
        event = xevent.ClientMessage(
            window=self.window, client_type=active, data=(32, [2, X.CurrentTime, 0, 0, 0]))
        root.send_event(event, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
        self.window.set_input_focus(X.RevertToParent, X.CurrentTime)
        self.display.sync()
        wait_for(self._focused, 3)

    def _key(self, name, kind):
        if not self._focused():
            self.focus()
        assert self._focused(), "Manual Control lost focus; refusing to type elsewhere"
        code = self.display.keysym_to_keycode(XK.string_to_keysym(name))
        xtest.fake_input(self.display, kind, code)
        self.display.sync()

    def press(self, name):
        self._key(name, X.KeyPress)

    def release(self, name):
        self._key(name, X.KeyRelease)

    def tap(self, name, hold=0.12):
        self.press(name)
        time.sleep(hold)
        self.release(name)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--carla-host", default="127.0.0.1")
    parser.add_argument("--carla-port", type=int, default=2000)
    parser.add_argument("--zenoh", default="tcp/127.0.0.1:7447")
    parser.add_argument("--role-name", default="hero")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "images").mkdir(exist_ok=True)

    conf = zenoh.Config()
    conf.insert_json5("mode", '"client"')
    conf.insert_json5("connect/endpoints", json.dumps([args.zenoh]))
    session = zenoh.open(conf)
    samples, latest, lock = [], {}, threading.Lock()

    def observe(sample):
        with lock:
            value = sample.payload.to_string()
            key = str(sample.key_expr)
            latest[key] = value
            samples.append({"t": round(time.monotonic(), 4), "key": key, "value": value})

    subscribers = [session.declare_subscriber(key, observe)
                   for key in ("vcu/control/brake_sts", "vcu/control/reverse_sts", "vehicle/lights/**")]

    client = carla.Client(args.carla_host, args.carla_port)
    client.set_timeout(20)
    world = client.get_world()
    vehicles = list(world.get_actors().filter("vehicle.*"))
    hero = [v for v in vehicles if v.attributes.get("role_name") == args.role_name] or vehicles
    assert len(hero) == 1, f"expected one X-Verse vehicle, found {[(v.id, v.attributes) for v in vehicles]}"
    vehicle = hero[0]

    frames = queue.Queue(maxsize=4)
    blueprint = world.get_blueprint_library().find("sensor.camera.rgb")
    for name, value in (("image_size_x", "960"), ("image_size_y", "540"), ("fov", "70")):
        blueprint.set_attribute(name, value)
    camera = world.spawn_actor(blueprint, carla.Transform(carla.Location(x=-6.5, z=2.2), carla.Rotation(pitch=-12)),
                               attach_to=vehicle)

    def on_image(image):
        if frames.full():
            frames.get_nowait()
        frames.put_nowait(image)
    camera.listen(on_image)

    keyboard = Keyboard(WINDOW_TITLE)
    receipt = {"component": "threadx-zonal-lights-az3166", "scenario": "x-verse-manual-control-carla",
               "carla_server": client.get_server_version(), "vehicle": {"id": vehicle.id, "type": vehicle.type_id},
               "started": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "steps": []}
    checks = receipt["checks"] = []

    def lights_cmd(reverse, brake):
        # The bridge publishes each light topic only on change; the aggregate
        # frame carries both commands from the board's latest 0x1F4.
        with lock:
            frame = json.loads(latest.get("vehicle/lights/frame", "{}"))
        return frame.get("bcm_reverse_lights_cmd") is reverse and frame.get("bcm_brake_lights_cmd") is brake

    def step(name, action, reverse, brake, vcu_key, vcu_value):
        expected = (REVERSE if reverse else 0) | (BRAKE if brake else 0)
        start = time.monotonic()
        action()
        wait_for(lambda: latest.get(vcu_key) == vcu_value)
        vcu_at = time.monotonic()
        wait_for(lambda: lights_cmd(reverse, brake))
        board_at = time.monotonic()
        wait_for(lambda: int(vehicle.get_light_state()) & (REVERSE | BRAKE) == expected)
        carla_at = time.monotonic()
        time.sleep(0.4)  # let the camera render the new light state
        while not frames.empty():
            frames.get_nowait()
        image = frames.get(timeout=5)
        path = args.output / "images" / f"{len(receipt['steps']) + 1}-{name}.png"
        image.save_to_disk(str(path))
        record = {"step": name, "reverse": reverse, "brake": brake,
                  "carla_light_mask": int(vehicle.get_light_state()), "expected_bits": expected,
                  "key_to_vcu_ms": round((vcu_at - start) * 1000, 1),
                  "key_to_board_lights_cmd_ms": round((board_at - start) * 1000, 1),
                  "key_to_carla_lights_ms": round((carla_at - start) * 1000, 1),
                  "image": str(path.relative_to(args.output))}
        receipt["steps"].append(record)
        print(json.dumps(record), flush=True)

    try:
        keyboard.focus()
        # Known start: brake released and reverse off (toggle with Q only if needed).
        if int(vehicle.get_light_state()) & REVERSE:
            keyboard.tap("q")
            wait_for(lambda: not int(vehicle.get_light_state()) & REVERSE)
        wait_for(lambda: int(vehicle.get_light_state()) & (REVERSE | BRAKE) == 0, 5)
        step("brake", lambda: keyboard.press("s"), False, True, "vcu/control/brake_sts", "true")
        step("brake-released", lambda: keyboard.release("s"), False, False, "vcu/control/brake_sts", "false")
        step("reverse", lambda: keyboard.tap("q"), True, False, "vcu/control/reverse_sts", "true")
        step("reverse-and-brake", lambda: keyboard.press("s"), True, True, "vcu/control/brake_sts", "true")
        step("reverse-brake-released", lambda: keyboard.release("s"), True, False, "vcu/control/brake_sts", "false")
        step("reverse-off", lambda: keyboard.tap("q"), False, False, "vcu/control/reverse_sts", "false")
        checks.append({"id": "manual-control-vcu-az3166-carla-four-light-states", "status": "passed"})
        receipt["status"] = "passed"
    except BaseException as error:
        receipt["status"] = "failed"
        receipt["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        try:
            keyboard.release("s")
        except Exception:
            pass
        camera.stop()
        removed = camera.destroy()
        checks.append({"id": "owned-camera-removed", "status": "passed" if removed else "failed"})
        for subscriber in subscribers:
            subscriber.undeclare()
        session.close()
        with lock:
            (args.output / "zenoh-samples.json").write_text(json.dumps(samples, indent=2) + "\n")
        (args.output / "results.json").write_text(json.dumps(receipt, indent=2) + "\n")
        print(json.dumps({"status": receipt.get("status"), "output": str(args.output)}))
    return 0 if receipt["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
