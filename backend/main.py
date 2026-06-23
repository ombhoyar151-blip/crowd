import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routers import alerts, analytics, auth, cameras, heatmap, websocket, ingest
from backend.db.session import create_engine_and_session
from backend.services.alert_broadcaster import AlertBroadcaster
from backend.services.backend_service import backend_service
from backend.worker.celery_app import celery_app
from config.settings import Settings

settings = Settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

engine = None
session_factory = None


def _make_redis_client():
    """Return a real Redis client or a NullRedis stub if no Redis is configured."""
    if settings.redis_url.startswith("memory://") or not settings.redis_url.startswith(
        ("redis://", "rediss://", "unix://")
    ):
        logger.info("Redis not configured — using in-process NullRedis stub")
        from services.alerts.null_redis import NullRedis
        return NullRedis()

    import redis.asyncio as redis
    return redis.from_url(settings.redis_url, decode_responses=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global engine, session_factory

    logger.info("Starting backend (port=%d)", settings.backend_port)

    engine, session_factory = create_engine_and_session(settings)

    loop = asyncio.get_running_loop()

    backend_service.setup(
        loop=loop,
        session_factory=session_factory,
        celery_app=celery_app,
    )

    redis_client = _make_redis_client()
    from backend.services.websocket_manager import ws_manager

    alert_broadcaster = AlertBroadcaster(redis_client, ws_manager)
    asyncio.ensure_future(alert_broadcaster.run())

    logger.info("Backend ready — visit http://localhost:%d/docs", settings.backend_port)

    yield

    logger.info("Shutting down backend")
    if engine:
        await engine.dispose()
    if hasattr(redis_client, "aclose"):
        await redis_client.aclose()


app = FastAPI(
    title="CrowdSense AI — Crowd Management API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception(request: Request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
async def health():
    return {"status": "ok", "redis": not settings.redis_url.startswith("memory://")}


app.include_router(auth.router, prefix=settings.api_prefix)
app.include_router(cameras.router, prefix=settings.api_prefix)
app.include_router(analytics.router, prefix=settings.api_prefix)
app.include_router(heatmap.router, prefix=settings.api_prefix)
app.include_router(alerts.router, prefix=settings.api_prefix)
app.include_router(websocket.router)
app.include_router(ingest.router, prefix=settings.api_prefix)
