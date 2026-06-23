import numpy as np
import pytest

from models.detection import Detection
from models.track import TrackBatch, TrackedPerson


class TestTrackSchemas:
    def test_tracked_person_fields(self):
        tp = TrackedPerson(
            track_id=3,
            bbox=(10.0, 20.0, 100.0, 200.0),
            centroid=(55.0, 110.0),
            confidence=0.92,
            camera_id="cam_1",
            frame_number=42,
        )
        assert tp.track_id == 3
        assert tp.bbox == (10.0, 20.0, 100.0, 200.0)
        assert tp.centroid == (55.0, 110.0)

    def test_track_batch_person_count(self):
        batch = TrackBatch(
            camera_id="cam_1",
            frame_number=10,
            timestamp=0.0,
            tracks=[
                TrackedPerson(track_id=1, bbox=(0, 0, 10, 20), centroid=(5, 10), confidence=0.9),
                TrackedPerson(track_id=2, bbox=(5, 5, 15, 25), centroid=(10, 15), confidence=0.8),
            ],
        )
        assert batch.person_count == 2

    def test_track_batch_empty(self):
        batch = TrackBatch(
            camera_id="cam_1",
            frame_number=10,
            timestamp=0.0,
            tracks=[],
        )
        assert batch.person_count == 0


class TestTrackerWrapper:
    def test_tracker_init_missing_boxmot(self):
        from services.vision.tracker import Tracker, TrackerError

        import sys
        orig = sys.modules.get("services.vision.tracker.ByteTracker")
        if orig is None:
            with pytest.raises(TrackerError, match="boxmot is not installed"):
                Tracker()

    def test_update_empty_detections_returns_empty(self):
        from services.vision.tracker import Tracker, TrackerError

        try:
            tracker = Tracker()
        except TrackerError:
            pytest.skip("boxmot not installed")
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        tracks = tracker.update([], frame)
        assert tracks == []

    def test_output_schema_correct_types(self):
        from services.vision.tracker import Tracker, TrackerError

        try:
            tracker = Tracker()
        except TrackerError:
            pytest.skip("boxmot not installed")

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        dets = [
            Detection(
                class_id=0,
                class_name="person",
                confidence=0.9,
                bbox=(50, 60, 150, 200),
                centroid=(100, 130),
                camera_id="cam_1",
                frame_number=1,
            )
        ]
        tracks = tracker.update(dets, frame)

        if tracks:
            t = tracks[0]
            assert isinstance(t.track_id, int)
            assert isinstance(t.bbox, tuple)
            assert isinstance(t.centroid, tuple)
            assert isinstance(t.confidence, float)
            assert len(t.bbox) == 4
            assert len(t.centroid) == 2
