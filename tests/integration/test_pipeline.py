import pytest


class TestPipelineUnit:
    def test_pipeline_init_without_initialize_raises(self):
        from services.vision.pipeline import Pipeline
        from config.settings import Settings

        p = Pipeline(Settings())
        with pytest.raises(RuntimeError, match="not initialized"):
            p.run()

    def test_pipeline_stop_idempotent(self):
        from services.vision.pipeline import Pipeline
        from config.settings import Settings

        p = Pipeline(Settings())
        p.stop()
        p.stop()


@pytest.mark.skip(reason="Requires model weights and video file")
class TestPipelineIntegration:
    async def test_detection_on_sample_frame(self):
        pass

    async def test_full_pipeline_run(self):
        pass

    async def test_person_count_nonzero(self):
        pass

    async def test_annotated_frame_shape(self):
        pass

    async def test_track_id_type(self):
        pass
