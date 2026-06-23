import argparse
import logging
import threading
import time

import cv2

from config.settings import Settings
from services.vision.pipeline import Pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description="Phase 2: Detection + ByteTrack Multi-Object Tracking"
    )
    parser.add_argument("--source", choices=["file", "rtsp", "webcam"], default=None)
    parser.add_argument("--video-path", type=str, default=None)
    parser.add_argument("--rtsp-url", type=str, default=None)
    parser.add_argument("--webcam-id", type=int, default=None)
    parser.add_argument("--conf", type=float, default=None)
    parser.add_argument("--show", action="store_true", default=True)
    parser.add_argument("--save", type=str, default=None, help="Output video path")
    parser.add_argument("--output-fps", type=int, default=15)
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
        logger.info(
            "Frame %d | tracks: %d",
            track_batch.frame_number,
            track_batch.person_count,
        )

        if args.show:
            cv2.imshow("Crowd Tracking", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                stop_event.set()

        if video_writer is not None:
            h, w = annotated_frame.shape[:2]
            if w != settings.frame_width or h != settings.frame_height:
                annotated_frame = cv2.resize(
                    annotated_frame,
                    (settings.frame_width, settings.frame_height),
                )
            video_writer.write(annotated_frame)

    pipeline.set_callback(on_frame)

    try:
        pipeline.run(stop_event=stop_event)
    except KeyboardInterrupt:
        logger.info("Interrupted, shutting down...")
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()
        if video_writer:
            video_writer.release()
            logger.info("Output saved to %s", args.save)


if __name__ == "__main__":
    main()
