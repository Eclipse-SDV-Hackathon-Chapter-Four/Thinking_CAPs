# publisher.py
# ------------------------------------------------------------
# CARLA → LiveKit Publisher (RGB Camera, Ego Vehicle Only)
# ------------------------------------------------------------
# Responsibilities:
# - Load runtime configuration from config.yaml
# - Connect to a LiveKit server using server-side credentials
# - Create and publish a single RGB video track
# - Bridge CARLA camera frames into LiveKit
# - Start and supervise the CARLA camera manager
# - Keep the process alive indefinitely
# ------------------------------------------------------------

import asyncio
import os
import threading
import yaml

from livekit import rtc
from livekit.api import AccessToken, VideoGrants

from carla_camera import CarlaCamera
from carla_video_source import CarlaVideoSource


# ------------------------------------------------------------
# Configuration loading
# ------------------------------------------------------------

CONFIG_PATH = os.getenv("PUBLISHER_CONFIG", "config.yaml")

if not os.path.exists(CONFIG_PATH):
    raise RuntimeError(f"Configuration file not found: {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    CONFIG = yaml.safe_load(f)

# ------------------------------------------------------------
# LiveKit configuration
# ------------------------------------------------------------

LIVEKIT_URL = CONFIG["livekit"]["url"]
LIVEKIT_API_KEY = CONFIG["livekit"]["api_key"]
LIVEKIT_API_SECRET = CONFIG["livekit"]["api_secret"]
LIVEKIT_ROOM = CONFIG["livekit"]["room"]

# ------------------------------------------------------------
# CARLA configuration
# ------------------------------------------------------------

CARLA_HOST = CONFIG["carla"]["host"]
CARLA_PORT = int(CONFIG["carla"]["port"])

# ------------------------------------------------------------
# Camera configuration
# ------------------------------------------------------------

CAMERA_WIDTH = int(CONFIG["camera"]["width"])
CAMERA_HEIGHT = int(CONFIG["camera"]["height"])
CAMERA_FOV = float(CONFIG["camera"]["fov"])
CAMERA_FPS = int(CONFIG["camera"]["fps"])

CAMERA_POSITION = CONFIG["camera"]["position"]
CAMERA_ROTATION = CONFIG["camera"]["rotation"]


# ------------------------------------------------------------
# Main async entrypoint
# ------------------------------------------------------------

async def main() -> None:
    """
    Main publisher lifecycle.
    """

    # --------------------------------------------------------
    # Connect to LiveKit
    # --------------------------------------------------------

    room = rtc.Room()

    token = (
        AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity("carla-publisher")
        .with_name("CARLA RGB Publisher")
        .with_grants(
            VideoGrants(
                room_join=True,
                room=LIVEKIT_ROOM,
                can_publish=True,
                can_subscribe=False,
            )
        )
        .to_jwt()
    )

    await room.connect(LIVEKIT_URL, token)
    print(f"✅ Connected to LiveKit room: {room.name}")

    # --------------------------------------------------------
    # Create video source and track
    # --------------------------------------------------------

    video_source = CarlaVideoSource(
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        max_fps=CAMERA_FPS,
    )

    video_track = rtc.LocalVideoTrack.create_video_track(
        name="carla-rgb",
        source=video_source,
    )

    await room.local_participant.publish_track(video_track)
    print("🎥 CARLA RGB video track published")

    # --------------------------------------------------------
    # Start CARLA camera manager in background thread
    # --------------------------------------------------------

    carla_camera = CarlaCamera(
        host=CARLA_HOST,
        port=CARLA_PORT,
        width=CAMERA_WIDTH,
        height=CAMERA_HEIGHT,
        fov=CAMERA_FOV,
        position=CAMERA_POSITION,
        rotation=CAMERA_ROTATION,
    )

    camera_thread = threading.Thread(
        target=carla_camera.run,
        args=(video_source.on_carla_image,),
        daemon=True,
    )
    camera_thread.start()

    print("✅ CARLA camera manager started")

    # --------------------------------------------------------
    # Keep process alive
    # --------------------------------------------------------

    await asyncio.Event().wait()


# ------------------------------------------------------------
# Script entrypoint
# ------------------------------------------------------------

if __name__ == "__main__":
    asyncio.run(main())