import numpy as np
import pytest

from services.analytics.density import DensityEstimator


class TestDensityEstimator:
    def test_empty_centroids(self):
        de = DensityEstimator(grid_scale=0.1)
        density, score = de.compute([], 1280, 720)
        assert density.shape == (72, 128)
        assert np.allclose(density, 0.0)
        assert score == 0.0

    def test_single_centroid(self):
        de = DensityEstimator(grid_scale=0.1)
        density, score = de.compute([(640.0, 360.0)], 1280, 720)
        assert density.shape == (72, 128)
        assert score == 0.0
        assert density.max() == 0.0

    def test_multiple_centroids(self):
        de = DensityEstimator(grid_scale=0.05)
        centroids = [(100, 200), (300, 400), (500, 600), (700, 100), (900, 500)]
        density, score = de.compute(centroids, 1280, 720)
        assert density.shape == (36, 64)
        assert 0.0 <= score <= 1.0

    def test_density_score_range(self):
        de = DensityEstimator(grid_scale=0.1)
        centroids = [(100, 200), (300, 400), (600, 500)]
        _, score = de.compute(centroids, 1280, 720)
        assert 0.0 <= score <= 1.0

    def test_grid_scale_shapes(self):
        de = DensityEstimator(grid_scale=0.2)
        density, _ = de.compute([(100, 200), (300, 400)], 640, 480)
        assert density.shape == (96, 128)
