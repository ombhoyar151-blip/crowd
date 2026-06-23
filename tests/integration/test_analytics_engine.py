import pytest


class TestAnalyticsEngineUnit:
    def test_engine_init(self):
        from config.settings import Settings
        from services.analytics.engine import AnalyticsEngine

        engine = AnalyticsEngine(Settings())
        assert engine.density_estimator is not None
        assert engine.heatmap_accumulator is not None
        assert engine.zone_manager is not None

    def test_engine_set_callback(self):
        from config.settings import Settings
        from services.analytics.engine import AnalyticsEngine

        engine = AnalyticsEngine(Settings())
        calls = []

        def cb(snapshot):
            calls.append(snapshot)

        engine.set_snapshot_callback(cb)
        assert engine._callback is not None


@pytest.mark.skip(reason="Requires model weights and video file")
class TestAnalyticsEngineIntegration:
    async def test_engine_receives_snapshot(self):
        pass

    async def test_snapshot_fields(self):
        pass

    async def test_heatmap_file_saved(self):
        pass

    async def test_zone_count_nonzero(self):
        pass
