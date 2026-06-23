import numpy as np
import pytest

from models.crowd_snapshot import ZoneStatus
from models.track import TrackedPerson
from services.analytics.zones import ZoneConfig, ZoneManager


@pytest.fixture
def sample_zones():
    return [
        {
            "id": "zone_a",
            "name": "Zone A",
            "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "threshold": 3,
            "color": [0, 255, 0],
        },
        {
            "id": "zone_b",
            "name": "Zone B",
            "polygon": [[200, 200], [400, 200], [400, 400], [200, 400]],
            "threshold": 2,
            "color": [0, 0, 255],
        },
    ]


class TestZoneConfig:
    def test_centroid_inside(self):
        zc = ZoneConfig({
            "id": "test",
            "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "threshold": 5,
        })
        assert zc.contains((50, 50)) is True

    def test_centroid_outside(self):
        zc = ZoneConfig({
            "id": "test",
            "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "threshold": 5,
        })
        assert zc.contains((200, 200)) is False

    def test_boundary_centroid(self):
        zc = ZoneConfig({
            "id": "test",
            "polygon": [[0, 0], [100, 0], [100, 100], [0, 100]],
            "threshold": 5,
        })
        assert zc.contains((0, 50)) is True


class TestZoneManager:
    def test_zone_status_fields(self):
        zs = ZoneStatus(
            zone_id="test", zone_name="Test", count=1, threshold=3, is_violated=False
        )
        assert zs.zone_id == "test"
        assert zs.is_violated is False

    def test_violation_flag(self):
        zs = ZoneStatus(
            zone_id="test", zone_name="Test", count=5, threshold=3, is_violated=True
        )
        assert zs.is_violated is True

    def test_no_violation(self):
        zs = ZoneStatus(
            zone_id="test", zone_name="Test", count=2, threshold=3, is_violated=False
        )
        assert zs.is_violated is False

    def test_evaluate_single_zone(self, tmp_path, sample_zones):
        config_path = tmp_path / "zones.yaml"
        import yaml
        with open(config_path, "w") as f:
            yaml.dump({"zones": [sample_zones[0]]}, f)

        zm = ZoneManager(config_path)
        tracks = [
            TrackedPerson(track_id=1, bbox=(0, 0, 10, 10), centroid=(50, 50), confidence=0.9),
            TrackedPerson(track_id=2, bbox=(0, 0, 10, 10), centroid=(60, 60), confidence=0.8),
        ]
        results = zm.evaluate(tracks)
        assert len(results) == 1
        assert results[0].count == 2
        assert results[0].is_violated is False

    def test_evaluate_multiple_zones(self, tmp_path, sample_zones):
        import yaml
        config_path = tmp_path / "zones.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"zones": sample_zones}, f)

        zm = ZoneManager(config_path)
        tracks = [
            TrackedPerson(track_id=1, bbox=(0, 0, 10, 10), centroid=(50, 50), confidence=0.9),
            TrackedPerson(track_id=2, bbox=(0, 0, 10, 10), centroid=(250, 250), confidence=0.8),
        ]
        results = zm.evaluate(tracks)
        assert len(results) == 2
        assert results[0].count == 1
        assert results[1].count == 1

    def test_empty_tracks(self, tmp_path, sample_zones):
        import yaml
        config_path = tmp_path / "zones.yaml"
        with open(config_path, "w") as f:
            yaml.dump({"zones": [sample_zones[0]]}, f)

        zm = ZoneManager(config_path)
        results = zm.evaluate([])
        assert len(results) == 1
        assert results[0].count == 0
        assert results[0].is_violated is False
