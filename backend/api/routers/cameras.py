from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.db.models import UserORM
from backend.schemas.camera import CameraResponse
from backend.services.camera_service import get_camera, get_cameras

router = APIRouter(prefix="/cameras", tags=["cameras"])


@router.get("", response_model=list[CameraResponse])
async def list_cameras(
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    cameras = await get_cameras(db)
    return [
        CameraResponse(
            id=c.id,
            name=c.name,
            source_type=c.source_type,
            source_url=c.source_url,
            is_active=c.is_active,
        )
        for c in cameras
    ]


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera_by_id(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    cam = await get_camera(db, camera_id)
    if not cam:
        raise HTTPException(status_code=404, detail="Camera not found")
    return CameraResponse(
        id=cam.id,
        name=cam.name,
        source_type=cam.source_type,
        source_url=cam.source_url,
        is_active=cam.is_active,
    )
