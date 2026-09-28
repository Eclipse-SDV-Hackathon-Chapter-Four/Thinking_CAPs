# carla_camera.py
# ------------------------------------------------------------
# CARLA Ego Vehicle Camera Manager
# ------------------------------------------------------------
# Responsibilities:
# - Locate ego_vehicle in the CARLA world
# - Spawn and attach an RGB camera sensor
# - Reattach camera on vehicle respawn
# - Emit camera frames via callback
# ------------------------------------------------------------

import carla
import time
from typing import Callable, Optional


class CarlaCamera:
    def __init__(
        self,
        host: str,
        port: int,
        width: int,
        height: int,
        fov: float,
        position: dict,
        rotation: dict,
        poll_interval: float = 1.0,
    ):
        self.client = carla.Client(host, port)
        self.client.set_timeout(10.0)

        self.world = self.client.get_world()
        self.blueprints = self.world.get_blueprint_library()

        self.width = width
        self.height = height
        self.fov = fov
        self.position = position
        self.rotation = rotation
        self.poll_interval = poll_interval

        self.vehicle: Optional[carla.Actor] = None
        self.vehicle_id: Optional[int] = None
        self.camera: Optional[carla.Actor] = None

        self.on_frame: Optional[Callable] = None

    def _find_ego_vehicle(self) -> Optional[carla.Actor]:
        vehicles = self.world.get_actors().filter("vehicle.*")
        for vehicle in vehicles:
            if vehicle.attributes.get("role_name") == "ego_vehicle":
                return vehicle
        return None

    def _spawn_camera(self, vehicle: carla.Actor) -> carla.Actor:
        camera_bp = self.blueprints.find("sensor.camera.rgb")
        camera_bp.set_attribute("image_size_x", str(self.width))
        camera_bp.set_attribute("image_size_y", str(self.height))
        camera_bp.set_attribute("fov", str(self.fov))
        camera_bp.set_attribute("sensor_tick", "0.0")

        transform = carla.Transform(
            carla.Location(
                x=self.position["x"],
                y=self.position["y"],
                z=self.position["z"],
            ),
            carla.Rotation(
                pitch=self.rotation["pitch"],
                yaw=self.rotation["yaw"],
                roll=self.rotation["roll"],
            ),
        )

        camera = self.world.spawn_actor(
            camera_bp,
            transform,
            attach_to=vehicle,
        )

        camera.listen(self.on_frame)
        print(f"📷 Camera attached to ego_vehicle (id={vehicle.id})")
        return camera

    def _destroy_camera(self):
        if self.camera:
            try:
                self.camera.stop()
                self.camera.destroy()
            except RuntimeError:
                pass
            self.camera = None

    def run(self, on_frame: Callable):
        self.on_frame = on_frame
        print("🔍 CarlaCamera waiting for ego_vehicle...")

        while True:
            try:
                ego = self._find_ego_vehicle()

                if ego is None:
                    if self.vehicle:
                        print("⚠️ ego_vehicle disappeared")
                        self._destroy_camera()
                        self.vehicle = None
                        self.vehicle_id = None
                else:
                    if self.vehicle_id != ego.id:
                        print(f"✅ New ego_vehicle detected (id={ego.id})")
                        self._destroy_camera()
                        self.vehicle = ego
                        self.vehicle_id = ego.id
                        self.camera = self._spawn_camera(ego)

            except RuntimeError as err:
                print(f"⚠️ CarlaCamera runtime error: {err}")
                self._destroy_camera()
                self.vehicle = None
                self.vehicle_id = None
                self.world = self.client.get_world()

            time.sleep(self.poll_interval)
