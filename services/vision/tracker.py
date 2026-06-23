import logging
from typing import Optional

import numpy as np

from models.detection import Detection
from models.track import TrackedPerson

logger = logging.getLogger(__name__)

try:
    from boxmot import ByteTracker
except Exception:
    try:
        # newer boxmot exposes ByteTrack in trackers
        from boxmot.trackers import ByteTrack as ByteTracker
    except Exception:
        try:
            # fallback to direct module path
            from boxmot.trackers.bbox.bytetrack.bytetrack import ByteTrack as ByteTracker
        except Exception:
            ByteTracker = None


class TrackerError(Exception):
    pass


class Tracker:
    def __init__(
        self,
        tracker_name: str = "bytetrack",
        track_buffer: int = 30,
        match_thresh: float = 0.8,
        min_hits: int = 1,
        device: str = "cpu",
    ):
        if ByteTracker is None:
            raise TrackerError(
                "boxmot is not installed. Run: pip install boxmot>=10.0.0"
            )

        self.tracker_name = tracker_name
        self.track_buffer = track_buffer
        self.match_thresh = match_thresh
        self.min_hits = min_hits
        self.device = device

        self._tracker = ByteTracker(
            track_high_thresh=0.5,
            track_low_thresh=0.1,
            new_track_thresh=0.6,
            track_buffer=track_buffer,
            match_thresh=match_thresh,
            frame_rate=30,
            min_hits=min_hits,
        )

        logger.info(
            "Tracker initialized (name=%s buffer=%d match_thresh=%.2f min_hits=%d)",
            tracker_name,
            track_buffer,
            match_thresh,
            min_hits,
        )

    def update(
        self,
        detections: list[Detection],
        frame: np.ndarray,
    ) -> list[TrackedPerson]:
        if not detections:
            empty = np.empty((0, 6), dtype=np.float32)
            raw = self._tracker.update(empty, frame)
            return []

        dets_np = np.array(
            [
                [d.bbox[0], d.bbox[1], d.bbox[2], d.bbox[3], d.confidence, float(d.class_id)]
                for d in detections
            ],
            dtype=np.float32,
        )

        raw_tracks = self._tracker.update(dets_np, frame)

        tracked: list[TrackedPerson] = []
        for t in raw_tracks:
            x1, y1, x2, y2, track_id, conf, cls_id = t[:7]
            cx = float((x1 + x2) / 2)
            cy = float((y1 + y2) / 2)
            tracked.append(
                TrackedPerson(
                    track_id=int(track_id),
                    bbox=(float(x1), float(y1), float(x2), float(y2)),
                    centroid=(cx, cy),
                    confidence=float(conf),
                    class_id=int(cls_id),
                    camera_id=detections[0].camera_id if detections else "",
                    frame_number=detections[0].frame_number if detections else 0,
                    timestamp=detections[0].timestamp if detections else 0.0,
                )
            )

        return tracked
