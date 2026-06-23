from pydantic import BaseModel


class CameraResponse(BaseModel):
    id: str
    name: str
    source_type: str
    source_url: str
    is_active: bool
