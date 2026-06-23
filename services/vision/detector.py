import logging
from pathlib import Path
from typing import Optional

import numpy as np
from ultralytics import YOLO

from models.detection import Detection

logger = logging.getLogger(__name__)

COCO_CLASSES: dict[int, str] = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
}


class DetectionError(Exception):
    pass


class Detector:
    def __init__(
        self,
        model_path: str | Path,
        conf_threshold: float = 0.5,
        iou_threshold: float = 0.45,
        device: str = "cpu",
        class_filter: Optional[list[int]] = None,
    ):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.device = device
        self.class_filter = class_filter or [0]

        model_path = Path(model_path)
        if not model_path.exists():
            raise DetectionError(f"Model file not found: {model_path}")

        self._model = YOLO(str(model_path))
        logger.info(
            "Detector loaded model=%s device=%s conf=%.2f iou=%.2f classes=%s",
            model_path.name,
            device,
            conf_threshold,
            iou_threshold,
            self.class_filter,
        )

    def detect(self, frame: np.ndarray, camera_id: str = "", frame_number: int = 0) -> list[Detection]:
        if frame is None:
            return []

        results = self._model(
            frame,
            conf=self.conf_threshold,
            iou=self.iou_threshold,
            device=self.device,
            verbose=False,
        )[0]

        detections: list[Detection] = []
        if results.boxes is None:
            return detections

        boxes = results.boxes.xyxy.cpu().numpy()
        confs = results.boxes.conf.cpu().numpy()
        cls_ids = results.boxes.cls.cpu().numpy().astype(int)

        for box, conf, cls_id in zip(boxes, confs, cls_ids):
            if self.class_filter and cls_id not in self.class_filter:
                continue

            x1, y1, x2, y2 = box
            cx = float((x1 + x2) / 2)
            cy = float((y1 + y2) / 2)
            class_name = COCO_CLASSES.get(cls_id, f"class_{cls_id}")

            detections.append(
                Detection(
                    class_id=int(cls_id),
                    class_name=class_name,
                    confidence=float(conf),
                    bbox=(float(x1), float(y1), float(x2), float(y2)),
                    centroid=(cx, cy),
                    camera_id=camera_id,
                    frame_number=frame_number,
                    timestamp=0.0,
                )
            )

        return detections

    @property
    def model_name(self) -> str:
        return self._model.model_name

    def to(self, device: str):
        self._model.to(device)
        self.device = device
