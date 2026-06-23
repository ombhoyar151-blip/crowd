import logging
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import cv2
import numpy as np

from config.settings import Settings
from models.detection import DetectionBatch
from models.track import TrackBatch
from services.vision.annotator import Annotator
from services.vision.detector import Detector
from services.vision.ingestion import StreamIngestion
from services.vision.tracker import Tracker

logger = logging.getLogger(__name__)

TrackCallback = Callable[[np.ndarray, TrackBatch], None]


class Pipeline:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.ingestion: Optional[StreamIngestion] = None
        self.detector: Optional[Detector] = None
        self.tracker: Optional[Tracker] = None
        self.annotator = Annotator()
        self._callback: Optional[TrackCallback] = None
        self._running = False

    def initialize(self):
        output_dir = Path(self.settings.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        source_type = self.settings.video_source
        self.ingestion = StreamIngestion(
            source_type=source_type,
            max_queue_size=self.settings.max_queue_size,
            target_fps=self.settings.target_fps,
            source_path=self.settings.video_path,
            rtsp_url=self.settings.rtsp_url,
            webcam_id=self.settings.webcam_id,
        )

        self.detector = Detector(
            model_path=self.settings.model_path,
            conf_threshold=self.settings.conf_threshold,
            iou_threshold=self.settings.iou_threshold,
            device=self.settings.device,
            class_filter=self.settings.class_filter,
        )

        self.tracker = Tracker(
            tracker_name=self.settings.tracker_name,
            track_buffer=self.settings.track_buffer,
            match_thresh=self.settings.match_thresh,
            min_hits=self.settings.min_hits,
            device=self.settings.device,
        )

        logger.info("Pipeline initialized")

    def set_callback(self, callback: TrackCallback):
        self._callback = callback

    def run(self, stop_event: Optional[threading.Event] = None):
        if not self.ingestion or not self.detector or not self.tracker:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")

        self.ingestion.start()
        self._running = True
        camera_id = (
            Path(self.settings.video_path).stem
            if self.settings.video_source == "file"
            else "stream"
        )

        logger.info("Pipeline running (camera=%s)", camera_id)

        while self._running:
            if stop_event and stop_event.is_set():
                break

            frame = self.ingestion.read()
            if frame is None:
                time.sleep(0.001)
                continue

            frame_number = self.ingestion.frame_count
            timestamp = time.time()

            detections = self.detector.detect(
                frame,
                camera_id=camera_id,
                frame_number=frame_number,
            )

            det_batch = DetectionBatch(
                camera_id=camera_id,
                frame_number=frame_number,
                timestamp=timestamp,
                detections=detections,
            )

            tracks = self.tracker.update(detections, frame)

            track_batch = TrackBatch(
                camera_id=camera_id,
                frame_number=frame_number,
                timestamp=timestamp,
                tracks=tracks,
            )

            annotated = self.annotator.draw(frame, track_batch)

            if self._callback:
                self._callback(annotated, track_batch)

        self.ingestion.stop()
        self._running = False
        logger.info("Pipeline stopped")

    def stop(self):
        self._running = False
