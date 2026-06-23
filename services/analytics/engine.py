import logging
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from config.settings import Settings
from models.crowd_snapshot import CrowdSnapshot, ZoneStatus
from models.track import TrackBatch
from services.analytics.density import DensityEstimator
from services.analytics.heatmap import HeatmapAccumulator
from services.analytics.zones import ZoneManager

logger = logging.getLogger(__name__)

SnapshotCallback = Callable[[CrowdSnapshot], None]


class AnalyticsEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.density_estimator = DensityEstimator(
            grid_scale=settings.density_grid_scale,
            bandwidth=settings.density_bandwidth,
        )
        self.heatmap_accumulator = HeatmapAccumulator(
            decay=settings.heatmap_decay,
            save_interval=settings.heatmap_save_interval,
            output_dir=Path(settings.output_dir) / "heatmaps",
        )
        self.zone_manager = ZoneManager(
            config_path=settings.zones_config_path,
        )
        self._callback: Optional[SnapshotCallback] = None

    def set_snapshot_callback(self, callback: SnapshotCallback):
        self._callback = callback

    def process(self, frame: np.ndarray, track_batch: TrackBatch) -> CrowdSnapshot:
        frame_h, frame_w = frame.shape[:2]

        centroids = [t.centroid for t in track_batch.tracks]

        density_matrix, density_score = self.density_estimator.compute(
            centroids, frame_w, frame_h
        )

        heatmap, heatmap_path = self.heatmap_accumulator.update(
            density_matrix, frame, track_batch.camera_id
        )

        zone_statuses = self.zone_manager.evaluate(track_batch.tracks)

        # Append a whole-scene zone status for site-wide alerting (if enabled)
        try:
            scene_enabled = bool(self.settings.alert_scene_enabled)
        except Exception:
            scene_enabled = True

        if scene_enabled:
            scene_count = track_batch.person_count
            scene_threshold = int(getattr(self.settings, "alert_scene_threshold", 10))
            scene_zone = ZoneStatus(
                zone_id="scene",
                zone_name="Whole Scene",
                count=scene_count,
                threshold=scene_threshold,
                is_violated=scene_count >= scene_threshold,
            )
            zone_statuses.append(scene_zone)

        snapshot = CrowdSnapshot(
            camera_id=track_batch.camera_id,
            frame_number=track_batch.frame_number,
            timestamp=track_batch.timestamp,
            person_count=track_batch.person_count,
            density_score=density_score,
            zone_statuses=zone_statuses,
            heatmap_path=heatmap_path,
        )

        if self._callback:
            self._callback(snapshot)

        return snapshot

    def get_heatmap(self) -> Optional[np.ndarray]:
        return self.heatmap_accumulator._heatmap
