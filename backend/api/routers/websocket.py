from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from jose import JWTError, jwt

from backend.services.websocket_manager import ws_manager
from config.settings import Settings

router = APIRouter(tags=["websocket"])
settings = Settings()


@router.websocket("/ws/stream/{camera_id}")
async def stream(ws: WebSocket, camera_id: str):
    token = ws.query_params.get("token")
    if not token:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    try:
        jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await ws_manager.connect(ws, camera_id)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(ws, camera_id)
