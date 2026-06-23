from pydantic import BaseModel


class ZoneStatus(BaseModel):
    zone_id: str
    zone_name: str
    count: int
    threshold: int
    is_violated: bool


class CrowdSnapshot(BaseModel):
    camera_id: str
    frame_number: int
    timestamp: float
    person_count: int
    density_score: float
    zone_statuses: list[ZoneStatus]
    heatmap_path: str | None = None
    # Optional base64-encoded preview image (data URL), e.g. 'data:image/jpeg;base64,...'
    preview: str | None = None
