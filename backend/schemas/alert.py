from pydantic import BaseModel


class AlertResponse(BaseModel):
    id: int
    time: str
    camera_id: str
    zone_id: str
    zone_name: str
    count: int
    threshold: int
    severity: str
    message: str
    resolved_at: str | None = None


class AlertListResponse(BaseModel):
    items: list[AlertResponse]
    total: int
