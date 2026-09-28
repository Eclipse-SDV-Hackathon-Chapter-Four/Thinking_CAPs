# carla_video_source.py
# ------------------------------------------------------------
# CARLA → LiveKit Video Adapter
# ------------------------------------------------------------
# Responsibilities:
# - Receive RGB camera images from CARLA
# - Enforce fixed resolution
# - Throttle frame delivery to a fixed FPS
# - Convert BGRA frames to RGB24
# ------------------------------------------------------------

import time
import numpy as np
from livekit import rtc


class CarlaVideoSource(rtc.VideoSource):
    def __init__(self, width: int, height: int, max_fps: int):
        super().__init__(width, height)

        self.width = width
        self.height = height

        self.max_fps = max_fps
        self._min_interval = 1.0 / float(max_fps)
        self._last_publish_ts = 0.0

    def on_carla_image(self, image) -> None:
        if image.width != self.width or image.height != self.height:
            return

        now = time.monotonic()
        if now - self._last_publish_ts < self._min_interval:
            return

        self._last_publish_ts = now

        bgra = np.frombuffer(image.raw_data, dtype=np.uint8)
        if bgra.size != self.width * self.height * 4:
            return

        bgra = bgra.reshape((self.height, self.width, 4))
        rgb = bgra[:, :, :3][:, :, ::-1]

        frame = rtc.VideoFrame(
            self.width,
            self.height,
            rtc.VideoBufferType.RGB24,
            rgb.tobytes(),
        )

        self.capture_frame(frame)
