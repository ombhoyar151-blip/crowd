import logging
from pathlib import Path
from typing import Any

import cv2
import numpy as np
import yaml

from models.crowd_snapshot import ZoneStatus
from models.track import TrackedPerson

logger = logging.getLogger(__name__)


class ZoneConfig:
    def __init__(self, data: dict[str, Any]):
        self.id: str = data["id"]
        self.name: str = data.get("name", data["id"])
        self.polygon: np.ndarray = np.array(data["polygon"], dtype=np.int32)
        self.threshold: int = int(data.get("threshold", 10))
        self.color: tuple[int, int, int] = tuple(data.get("color", [0, 0, 255]))

    def contains(self, centroid: tuple[float, float]) -> bool:
        pt = (float(centroid[0]), float(centroid[1]))
        return cv2.pointPolygonTest(self.polygon, pt, measureDist=False) >= 0


class ZoneManager:
    def __init__(self, config_path: str | Path = "config/zones.yaml"):
        self.config_path = Path(config_path)
        self.zones: list[ZoneConfig] = []
        self._load_config()

    def _load_config(self):
        if not self.config_path.exists():
            logger.warning("Zones config not found at %s", self.config_path)
            return

        with open(self.config_path) as f:
            data = yaml.safe_load(f)

        raw_zones = data.get("zones", [])
        self.zones = [ZoneConfig(z) for z in raw_zones]
        logger.info("Loaded %d zones from %s", len(self.zones), self.config_path)

    def evaluate(self, tracks: list[TrackedPerson]) -> list[ZoneStatus]:
        results: list[ZoneStatus] = []

        for zone in self.zones:
            count = 0
            for t in tracks:
                if zone.contains(t.centroid):
                    count += 1

            results.append(
                ZoneStatus(
                    zone_id=zone.id,
                    zone_name=zone.name,
                    count=count,
                    threshold=zone.threshold,
                    is_violated=count > zone.threshold,
                )
            )

        return results
