from pydantic import BaseModel


class Detection(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[float, float, float, float]
    centroid: tuple[float, float]
    camera_id: str = ""
    frame_number: int = 0
    timestamp: float = 0.0


class DetectionBatch(BaseModel):
    camera_id: str
    frame_number: int
    timestamp: float
    detections: list[Detection]
