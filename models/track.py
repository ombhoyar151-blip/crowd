from pydantic import BaseModel


class TrackedPerson(BaseModel):
    track_id: int
    bbox: tuple[float, float, float, float]
    centroid: tuple[float, float]
    confidence: float
    class_id: int = 0
    camera_id: str = ""
    frame_number: int = 0
    timestamp: float = 0.0


class TrackBatch(BaseModel):
    camera_id: str
    frame_number: int
    timestamp: float
    tracks: list[TrackedPerson]

    @property
    def person_count(self) -> int:
        return len(self.tracks)
