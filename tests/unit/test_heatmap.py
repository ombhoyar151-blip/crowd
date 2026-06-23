import numpy as np

from services.analytics.heatmap import HeatmapAccumulator


class TestHeatmapAccumulator:
    def test_initial_state(self):
        ha = HeatmapAccumulator(decay=0.97, save_interval=1000)
        assert ha._heatmap is None

    def test_update_increases_value(self):
        ha = HeatmapAccumulator(decay=0.97, save_interval=1000)
        density = np.ones((10, 10), dtype=np.float32) * 0.5
        heatmap, _ = ha.update(density)
        assert heatmap.max() > 0.0

    def test_decay_applied(self):
        ha = HeatmapAccumulator(decay=0.5, save_interval=1000)
        density = np.ones((10, 10), dtype=np.float32)
        ha.update(density)
        zero = np.zeros((10, 10), dtype=np.float32)
        heatmap, _ = ha.update(zero)
        assert heatmap.max() < 1.0
        assert heatmap.max() > 0.0

    def test_output_range(self):
        ha = HeatmapAccumulator(decay=0.9, save_interval=1000)
        for _ in range(10):
            density = np.random.rand(20, 20).astype(np.float32)
            heatmap, _ = ha.update(density)
            assert heatmap.min() >= 0.0
            assert heatmap.max() <= 1.0

    def test_colourmap_shape(self):
        ha = HeatmapAccumulator(decay=0.9, save_interval=1000)
        density = np.ones((10, 10), dtype=np.float32) * 0.5
        ha.update(density)
        colour = ha.apply_colourmap(ha._heatmap)
        assert colour.shape == (10, 10, 3)
        assert colour.dtype == np.uint8

    def test_reset(self):
        ha = HeatmapAccumulator(decay=0.9, save_interval=1000)
        density = np.ones((10, 10), dtype=np.float32)
        ha.update(density)
        assert ha._heatmap is not None
        ha.reset()
        assert ha._heatmap is None
        assert ha._frame_count == 0
