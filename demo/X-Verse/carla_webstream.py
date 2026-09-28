#!/usr/bin/env python3
import carla
import numpy as np
from turbojpeg import TurboJPEG
from flask import Flask, Response
from waitress import serve
import threading
import atexit
import time

app = Flask(__name__)

# Global variables
camera = None
world = None
latest_frame = None
callbacks = []

# TurboJPEG for high‑performance JPEG encoding
jpeg = TurboJPEG()


def cleanup():
    """Destroy the camera sensor on exit to prevent ghost actors in CARLA."""
    global camera
    if camera is not None:
        print("[Cleanup] Stopping camera...")
        try:
            camera.stop()
            camera.destroy()
            print("[Cleanup] Camera destroyed.")
        except Exception as e:
            print("[Cleanup] Error destroying camera:", e)


# Ensure cleanup runs when the script terminates (CTRL+C or normal exit)
atexit.register(cleanup)


def carla_thread():
    """Connect to CARLA and set up an optimized RGB camera for streaming."""
    global world, camera, latest_frame, callbacks

    print("[CARLA] Connecting to CARLA...")
    client = carla.Client("localhost", 2000)
    client.set_timeout(5.0)
    world = client.get_world()

    # Wait until at least one vehicle exists in the scene
    actors = world.get_actors().filter("vehicle.*")
    while len(actors) == 0:
        print("[CARLA] Waiting for a vehicle to spawn...")
        time.sleep(1)
        actors = world.get_actors().filter("vehicle.*")

    vehicle = actors[0]
    print(f"[CARLA] Using vehicle {vehicle.id} for camera attachment.")

    # Configure camera blueprint
    bp = world.get_blueprint_library().find("sensor.camera.rgb")
    bp.set_attribute("image_size_x", "800")
    bp.set_attribute("image_size_y", "600")
    bp.set_attribute("fov", "90")

    # sensor_tick=0.0 → highest possible update frequency (no artificial delay)
    bp.set_attribute("sensor_tick", "0.0")

    # Camera position relative to the vehicle
    transform = carla.Transform(
        carla.Location(x=0.5, z=1.8),
        carla.Rotation(pitch=0)
    )

    camera = world.spawn_actor(bp, transform, attach_to=vehicle)
    print("[CARLA] Camera actor created.")

    def callback(image):
        """
        Convert CARLA raw image to JPEG using TurboJPEG.
        This callback is optimized for low latency and low CPU usage.
        """
        global latest_frame
        try:
            array = np.frombuffer(image.raw_data, dtype=np.uint8)
            array = array.reshape((image.height, image.width, 4))[:, :, :3]
            latest_frame = jpeg.encode(array, quality=80)
        except Exception as e:
            print("[Callback] Error encoding frame:", e)

    # Store callback reference to prevent garbage collection
    callbacks.append(callback)

    # Start listening for new frames
    camera.listen(callback)
    print("[CARLA] Camera streaming started.")


def generate_stream():
    """
    MJPEG generator with minimal latency and reduced CPU load.
    Only sends a frame when a new one is available.
    """
    global latest_frame
    last = None

    while True:
        if latest_frame is not None and latest_frame != last:
            frame = latest_frame
            last = frame
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame +
                b"\r\n"
            )
        else:
            time.sleep(0.005)  # Prevent busy-looping


@app.route("/carla_stream")
def carla_stream():
    """HTTP endpoint that provides the MJPEG video stream."""
    return Response(
        generate_stream(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )


if __name__ == "__main__":
    # Launch CARLA camera thread
    t = threading.Thread(target=carla_thread, daemon=True)
    t.start()

    print("[WEB] Starting web server on http://0.0.0.0:8080/carla_stream")
    serve(app, host="0.0.0.0", port=8080)
