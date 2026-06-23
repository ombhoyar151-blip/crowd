import cv2
import numpy as np

from models.crowd_snapshot import ZoneStatus
from models.track import TrackBatch


class Annotator:
    def draw(self, frame: np.ndarray, track_batch: TrackBatch) -> np.ndarray:
        annotated = frame.copy()

        for track in track_batch.tracks:
            x1, y1, x2, y2 = [int(v) for v in track.bbox]

            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

            label = f"ID: {track.track_id} {track.confidence:.2f}"
            (label_w, label_h), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2
            )
            cv2.rectangle(
                annotated,
                (x1, y1 - label_h - 6),
                (x1 + label_w, y1),
                (0, 255, 0),
                -1,
            )
            cv2.putText(
                annotated,
                label,
                (x1, y1 - 6),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 0, 0),
                2,
            )

        cv2.putText(
            annotated,
            f"People: {track_batch.person_count}",
            (12, 36),
            cv2.FONT_HERSHEY_SIMPLEX,
            1.0,
            (255, 255, 255),
            2,
        )

        return annotated

    def draw_heatmap_overlay(
        self, frame: np.ndarray, heatmap: np.ndarray
    ) -> np.ndarray:
        h, w = frame.shape[:2]
        heatmap_resized = cv2.resize(heatmap, (w, h))
        heatmap_colour = self._to_colourmap(heatmap_resized)
        return cv2.addWeighted(frame, 0.6, heatmap_colour, 0.4, 0)

    def _to_colourmap(self, heatmap: np.ndarray) -> np.ndarray:
        heat_uint8 = (np.clip(heatmap, 0.0, 1.0) * 255).astype(np.uint8)
        return cv2.applyColorMap(heat_uint8, cv2.COLORMAP_JET)

    def draw_zones(
        self,
        frame: np.ndarray,
        zone_statuses: list[ZoneStatus],
        zone_polygons: list[np.ndarray],
    ) -> np.ndarray:
        annotated = frame.copy()
        overlay = annotated.copy()

        for status, polygon in zip(zone_statuses, zone_polygons):
            color = (0, 0, 255) if status.is_violated else (0, 255, 0)
            cv2.fillPoly(overlay, [polygon], color)
            cv2.polylines(overlay, [polygon], True, color, 2)

            centroid = polygon.mean(axis=0).astype(int)
            label = f"{status.zone_name}: {status.count}/{status.threshold}"
            cv2.putText(
                overlay,
                label,
                (centroid[0] - 40, centroid[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                2,
            )

        return cv2.addWeighted(overlay, 0.3, annotated, 0.7, 0)
