from pydantic import BaseModel


class SnapshotResponse(BaseModel):
    id: int
    time: str
    camera_id: str
    frame_number: int
    person_count: int
    density_score: float
    heatmap_path: str | None = None


class SnapshotListResponse(BaseModel):
    items: list[SnapshotResponse]
    total: int


class SummaryResponse(BaseModel):
    camera_id: str
    interval: str
    avg_person_count: float
    max_person_count: int
    min_person_count: int
    total_snapshots: int
