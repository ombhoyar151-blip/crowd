import argparse
import logging
import threading
import base64

import cv2

from config.settings import Settings
from services.analytics.engine import AnalyticsEngine
from services.vision.annotator import Annotator
from services.vision.pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 3: Detection + Tracking + Crowd Analytics"
    )
    parser.add_argument("--source", choices=["file", "rtsp", "webcam"], default=None)
    parser.add_argument("--video-path", type=str, default=None)
    parser.add_argument("--rtsp-url", type=str, default=None)
    parser.add_argument("--webcam-id", type=int, default=None)
    parser.add_argument("--conf", type=float, default=None)
    parser.add_argument("--show", action="store_true", default=False)
    parser.add_argument("--show-heatmap", action="store_true", default=True)
    parser.add_argument("--show-zones", action="store_true", default=True)
    parser.add_argument("--save", type=str, default=None)
    parser.add_argument("--output-fps", type=int, default=15)
    parser.add_argument("--camera-id", type=str, default=None, help="Camera ID to associate snapshots with (for dashboard)")
    args = parser.parse_args()

    settings = Settings()

    if args.source:
        settings.video_source = args.source
    if args.video_path:
        settings.video_path = args.video_path
    if args.rtsp_url:
        settings.rtsp_url = args.rtsp_url
    if args.webcam_id is not None:
        settings.webcam_id = args.webcam_id
    if args.conf is not None:
        settings.conf_threshold = args.conf

    pipeline = Pipeline(settings)
    pipeline.initialize()

    analytics = AnalyticsEngine(settings)
    # Send snapshots to backend so the dashboard can display them live.
    def _post_snapshot(snapshot):
        try:
            # allow overriding camera id from CLI so snapshots map to a DB camera
            cid = getattr(args, "camera_id", None)
            if cid:
                snapshot.camera_id = cid

            import requests

            url = f"http://127.0.0.1:{settings.backend_port}{settings.api_prefix}/ingest"
            requests.post(url, json=snapshot.model_dump())
        except Exception:
            logger.exception("Failed to POST snapshot to backend")

    # We'll POST snapshots (including a small preview) manually after building the display
    annotator = Annotator()

    video_writer = None
    if args.save:
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video_writer = cv2.VideoWriter(
            args.save,
            fourcc,
            args.output_fps,
            (settings.frame_width, settings.frame_height),
        )

    stop_event = threading.Event()

    def on_frame(annotated_frame, track_batch):
        snapshot = analytics.process(annotated_frame, track_batch)

        display = annotated_frame.copy()

        if args.show_heatmap:
            heatmap = analytics.get_heatmap()
            if heatmap is not None:
                display = annotator.draw_heatmap_overlay(display, heatmap)

        if args.show_zones:
            polygons = [z.polygon for z in analytics.zone_manager.zones]
            display = annotator.draw_zones(
                display, snapshot.zone_statuses, polygons
            )

        # Create a small thumbnail preview and attach as base64 data URL to snapshot
        try:
            h, w = display.shape[:2]
            thumb_w = 320
            thumb_h = int((thumb_w * h) / w) if w else h
            thumb = cv2.resize(display, (thumb_w, thumb_h))
            ret, buf = cv2.imencode('.jpg', thumb, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
            if ret:
                b64 = base64.b64encode(buf.tobytes()).decode('ascii')
                snapshot.preview = f"data:image/jpeg;base64,{b64}"
        except Exception:
            logger.exception("Failed to create snapshot preview")

        # POST the snapshot (with preview) to the backend so dashboard clients receive it
        try:
            _post_snapshot(snapshot)
        except Exception:
            logger.exception("Failed to POST snapshot to backend")

        info = f"Density: {snapshot.density_score:.3f}  People: {snapshot.person_count}"
        cv2.putText(
            display,
            info,
            (12, 72),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        logger.info(
            "Frame %d | people=%d density=%.3f zones=%s",
            track_batch.frame_number,
            snapshot.person_count,
            snapshot.density_score,
            [f"{z.zone_id}={z.count}" for z in snapshot.zone_statuses],
        )

        if args.show:
            cv2.imshow("Crowd Analytics", display)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                stop_event.set()

        if video_writer is not None:
            h, w = display.shape[:2]
            if w != settings.frame_width or h != settings.frame_height:
                display = cv2.resize(
                    display, (settings.frame_width, settings.frame_height)
                )
            video_writer.write(display)

    pipeline.set_callback(on_frame)

    try:
        pipeline.run(stop_event=stop_event)
    except KeyboardInterrupt:
        logger.info("Interrupted, shutting down...")
    finally:
        pipeline.stop()
        if args.show:
            try:
                cv2.destroyAllWindows()
            except Exception:
                logger.exception("Failed to destroy OpenCV windows")
        if video_writer:
            video_writer.release()
            logger.info("Output saved to %s", args.save)


if __name__ == "__main__":
    main()
