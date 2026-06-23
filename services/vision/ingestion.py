import logging
import queue
import threading
from pathlib import Path
from typing import Optional

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class StreamIngestionError(Exception):
    pass


class StreamIngestion:
    def __init__(
        self,
        source_type: str,
        max_queue_size: int = 64,
        target_fps: int = 30,
        source_path: str = "",
        rtsp_url: str = "",
        webcam_id: int = 0,
    ):
        self.source_type = source_type
        self.target_fps = target_fps
        self.frame_queue: queue.Queue = queue.Queue(maxsize=max_queue_size)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._cap: Optional[cv2.VideoCapture] = None
        self._source_path = source_path
        self._rtsp_url = rtsp_url
        self._webcam_id = webcam_id
        self.frame_count = 0
        self._fps_actual = 0.0

    def _open_capture(self) -> cv2.VideoCapture:
        if self.source_type == "file":
            path = self._source_path
            if not Path(path).exists():
                raise StreamIngestionError(f"Video file not found: {path}")
            cap = cv2.VideoCapture(str(path))
            if not cap.isOpened():
                raise StreamIngestionError(f"Failed to open video file: {path}")
            logger.info("Opened video file: %s", path)

        elif self.source_type == "rtsp":
            cap = cv2.VideoCapture(self._rtsp_url, cv2.CAP_FFMPEG)
            if not cap.isOpened():
                raise StreamIngestionError(
                    f"Failed to open RTSP stream: {self._rtsp_url}"
                )
            logger.info("Opened RTSP stream: %s", self._rtsp_url)

        elif self.source_type == "webcam":
            cap = cv2.VideoCapture(self._webcam_id)
            if not cap.isOpened():
                raise StreamIngestionError(
                    f"Failed to open webcam (id={self._webcam_id})"
                )
            logger.info("Opened webcam (id=%d)", self._webcam_id)

        else:
            raise StreamIngestionError(f"Unknown source type: {self.source_type}")

        return cap

    def _read_loop(self):
        self._cap = self._open_capture()
        self._running = True
        frame_interval = 1.0 / self.target_fps if self.target_fps > 0 else 0

        while self._running:
            ret, frame = self._cap.read()
            if not ret:
                logger.warning("End of stream or read failure")
                break

            self.frame_count += 1

            try:
                self.frame_queue.put(frame, block=True, timeout=1.0)
            except queue.Full:
                logger.warning("Frame queue full, dropping frame %d", self.frame_count)

            if self.source_type == "file" and frame_interval > 0:
                cv2.waitKey(int(frame_interval * 1000))

        self._cap.release()
        self._running = False

    def start(self):
        if self._thread and self._thread.is_alive():
            logger.warning("Ingestion thread already running")
            return
        self._thread = threading.Thread(target=self._read_loop, daemon=True)
        self._thread.start()
        logger.info(
            "Stream ingestion started (type=%s, fps=%d)",
            self.source_type,
            self.target_fps,
        )

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=5.0)
        logger.info("Stream ingestion stopped")

    def read(self) -> Optional[np.ndarray]:
        try:
            return self.frame_queue.get(block=False)
        except queue.Empty:
            return None

    @property
    def is_running(self) -> bool:
        return self._running

    @property
    def queue_size(self) -> int:
        return self.frame_queue.qsize()
