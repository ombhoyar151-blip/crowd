import logging

import numpy as np
from scipy.stats import gaussian_kde

logger = logging.getLogger(__name__)


class DensityEstimator:
    def __init__(
        self,
        grid_scale: float = 0.1,
        bandwidth: str | float = "scott",
    ):
        self.grid_scale = grid_scale
        self.bandwidth = bandwidth

    def compute(
        self,
        centroids: list[tuple[float, float]],
        frame_width: int,
        frame_height: int,
    ) -> tuple[np.ndarray, float]:
        if len(centroids) < 2:
            grid_h = max(1, int(frame_height * self.grid_scale))
            grid_w = max(1, int(frame_width * self.grid_scale))
            return np.zeros((grid_h, grid_w), dtype=np.float32), 0.0

        points = np.array(centroids).T

        try:
            kde = gaussian_kde(points, bw_method=self.bandwidth)
        except np.linalg.LinAlgError:
            grid_h = max(1, int(frame_height * self.grid_scale))
            grid_w = max(1, int(frame_width * self.grid_scale))
            return np.zeros((grid_h, grid_w), dtype=np.float32), 0.0

        grid_h = max(1, int(frame_height * self.grid_scale))
        grid_w = max(1, int(frame_width * self.grid_scale))

        grid_x = np.linspace(0, frame_width, grid_w)
        grid_y = np.linspace(0, frame_height, grid_h)
        mesh_x, mesh_y = np.meshgrid(grid_x, grid_y)
        grid_coords = np.vstack([mesh_x.ravel(), mesh_y.ravel()])

        density = kde(grid_coords).reshape(grid_h, grid_w).astype(np.float32)

        max_val = density.max()
        if max_val > 0:
            density = density / max_val

        density_score = float(density.mean())

        return density, density_score
