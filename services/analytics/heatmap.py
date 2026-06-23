import logging
from pathlib import Path

import cv2
import numpy as np

logger = logging.getLogger(__name__)


class HeatmapAccumulator:
    def __init__(
        self,
        decay: float = 0.97,
        save_interval: int = 30,
        output_dir: str | Path = "output/heatmaps",
    ):
        self.decay = decay
        self.save_interval = save_interval
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._heatmap: np.ndarray | None = None
        self._frame_count = 0

    def update(
        self,
        density_matrix: np.ndarray,
        frame: np.ndarray | None = None,
        camera_id: str = "",
    ) -> tuple[np.ndarray, str | None]:
        if self._heatmap is None:
            self._heatmap = density_matrix.astype(np.float32)
        else:
            target_h, target_w = density_matrix.shape[:2]
            if self._heatmap.shape != density_matrix.shape:
                self._heatmap = cv2.resize(
                    self._heatmap, (target_w, target_h)
                ).astype(np.float32)

            self._heatmap = (
                self._heatmap * self.decay + density_matrix * (1.0 - self.decay)
            )

        self._heatmap = np.clip(self._heatmap, 0.0, 1.0)

        self._frame_count += 1
        saved_path: str | None = None

        if self._frame_count % self.save_interval == 0:
            saved_path = self._save_heatmap(frame, camera_id)

        return self._heatmap.copy(), saved_path

    def _save_heatmap(
        self,
        frame: np.ndarray | None,
        camera_id: str,
    ) -> str:
        heatmap_colour = self.apply_colourmap(self._heatmap)

        if frame is not None and heatmap_colour.shape[:2] == frame.shape[:2]:
            overlay = cv2.addWeighted(frame, 0.6, heatmap_colour, 0.4, 0)
        else:
            overlay = heatmap_colour

        filename = f"{camera_id}_{self._frame_count:08d}.png"
        filepath = self.output_dir / filename
        cv2.imwrite(str(filepath), overlay)
        logger.debug("Heatmap saved to %s", filepath)
        return str(filepath)

    def apply_colourmap(self, heatmap: np.ndarray) -> np.ndarray:
        heat_uint8 = (np.clip(heatmap, 0.0, 1.0) * 255).astype(np.uint8)
        return cv2.applyColorMap(heat_uint8, cv2.COLORMAP_JET)

    def reset(self):
        self._heatmap = None
        self._frame_count = 0
