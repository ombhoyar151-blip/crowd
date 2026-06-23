from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    project_root: Path = Path(__file__).resolve().parent.parent

    video_source: Literal["file", "rtsp", "webcam"] = "file"
    video_path: str = ""
    rtsp_url: str = ""
    webcam_id: int = 0

    model_path: Path = Path("models/yolo11n.pt")
    model_name: str = "yolo11n"
    conf_threshold: float = 0.5
    iou_threshold: float = 0.45
    device: str = "cpu"
    class_filter: list[int] = [0]

    frame_width: int = 1280
    frame_height: int = 720
    target_fps: int = 30
    max_queue_size: int = 64

    tracker_name: str = "bytetrack"
    track_buffer: int = 30
    match_thresh: float = 0.8
    min_hits: int = 1

    density_grid_scale: float = 0.1
    density_bandwidth: str = "scott"
    heatmap_decay: float = 0.97
    heatmap_save_interval: int = 30
    zones_config_path: Path = Path("config/zones.yaml")

    database_url: str = "postgresql+asyncpg://crowd:crowd@localhost:5432/crowd"
    database_pool_size: int = 20
    redis_url: str = "redis://localhost:6379/0"

    jwt_secret_key: str = "changeme"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    cors_origins: list[str] = ["http://localhost:5173"]
    api_prefix: str = "/api/v1"
    backend_port: int = 8000

    log_level: str = "INFO"
    output_dir: Path = Path("output")

    alert_cooldown_seconds: int = 60
    alert_critical_ratio: float = 2.0

    alert_email_enabled: bool = False
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    alert_email_from: str = ""
    alert_email_to: list[str] = []

    # Whole-scene alerting (treat the entire frame as a single zone)
    alert_scene_enabled: bool = True
    alert_scene_threshold: int = 10

    alert_telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""


settings = Settings()
