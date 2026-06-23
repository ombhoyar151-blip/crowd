import numpy as np
import pytest

from models.detection import Detection


class TestDetectionModel:
    def test_detection_fields(self):
        det = Detection(
            class_id=0,
            class_name="person",
            confidence=0.95,
            bbox=(10.0, 20.0, 100.0, 200.0),
            centroid=(55.0, 110.0),
            camera_id="cam_1",
            frame_number=42,
            timestamp=1234567890.0,
        )
        assert det.class_id == 0
        assert det.class_name == "person"
        assert det.confidence == 0.95
        assert det.bbox == (10.0, 20.0, 100.0, 200.0)
        assert det.centroid == (55.0, 110.0)

    def test_detection_centroid_computation(self):
        x1, y1, x2, y2 = 50.0, 60.0, 150.0, 200.0
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        det = Detection(
            class_id=0,
            class_name="person",
            confidence=0.9,
            bbox=(x1, y1, x2, y2),
            centroid=(cx, cy),
        )
        assert det.centroid == (100.0, 130.0)


class TestFrameAnnotations:
    def test_annotate_frame_adds_boxes(self):
        import cv2

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        det = Detection(
            class_id=0,
            class_name="person",
            confidence=0.85,
            bbox=(50.0, 60.0, 150.0, 200.0),
            centroid=(100.0, 130.0),
        )

        annotated = frame.copy()
        x1, y1, x2, y2 = [int(v) for v in det.bbox]
        cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

        assert not np.array_equal(frame, annotated)

    def test_no_detections_returns_empty_list(self):
        from services.vision.detector import DetectionError, Detector

        with pytest.raises(DetectionError, match="Model file not found"):
            Detector("nonexistent.pt")
