from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.dependencies import get_current_user, get_db
from backend.db.models import UserORM
from backend.services.analytics_service import get_current

router = APIRouter(prefix="/heatmap", tags=["heatmap"])


@router.get("/{camera_id}")
async def get_heatmap(
    camera_id: str,
    db: AsyncSession = Depends(get_db),
    user: UserORM = Depends(get_current_user),
):
    snap = await get_current(db, camera_id)
    if not snap or not snap.heatmap_path:
        raise HTTPException(status_code=404, detail="No heatmap available")

    from pathlib import Path
    path = Path(snap.heatmap_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Heatmap file not found on disk")

    return FileResponse(str(path), media_type="image/png")
