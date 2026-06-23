import pytest

from services.vision.ingestion import StreamIngestionError, StreamIngestion


class TestStreamIngestion:
    def test_unknown_source_type(self):
        ing = StreamIngestion(source_type="invalid")
        with pytest.raises(StreamIngestionError, match="Unknown source type"):
            ing._open_capture()

    def test_file_not_found(self):
        ing = StreamIngestion(source_type="file", source_path="nonexistent.mp4")
        with pytest.raises(StreamIngestionError, match="Video file not found"):
            ing._open_capture()

    def test_queue_initialized_empty(self):
        ing = StreamIngestion(source_type="file", max_queue_size=10)
        assert ing.queue_size == 0
        assert ing.read() is None
