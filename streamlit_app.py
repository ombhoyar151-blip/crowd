import tempfile
import time
from pathlib import Path

import imageio
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from config.settings import Settings
from services.vision.detector import Detector
from services.vision.tracker import Tracker


def save_uploaded_video(uploaded_file: st.uploaded_file_manager.UploadedFile) -> str:
    temp_dir = Path(tempfile.gettempdir())
    target_path = temp_dir / uploaded_file.name
    with open(target_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(target_path)


def configure_settings(confidence: float, fps: int) -> Settings:
    settings = Settings()
    settings.video_source = "file"
    settings.conf_threshold = confidence
    settings.target_fps = fps
    settings.device = "cpu"
    settings.frame_width = 960
    settings.frame_height = 540
    return settings


def draw_tracks(frame: np.ndarray, tracks: list) -> Image.Image:
    if frame.ndim == 4:
        frame = frame[:, :, :3]

    if frame.dtype != np.uint8:
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    image = Image.fromarray(frame)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for track in tracks:
        x1, y1, x2, y2 = [int(v) for v in track.bbox]
        draw.rectangle([x1, y1, x2, y2], outline=(0, 255, 0), width=3)
        label = f"ID:{track.track_id} {track.confidence:.2f}"
        text_width, text_height = draw.textsize(label, font=font)
        draw.rectangle([
            x1,
            y1 - text_height - 6,
            x1 + text_width + 6,
            y1,
        ], fill=(0, 255, 0))
        draw.text((x1 + 3, y1 - text_height - 4), label, fill=(0, 0, 0), font=font)

    count_label = f"People: {len(tracks)}"
    draw.text((12, 12), count_label, fill=(255, 255, 0), font=font)
    return image


def process_video(video_path: str, settings: Settings, max_frames: int = 100):
    detector = Detector(
        model_path=settings.model_path,
        conf_threshold=settings.conf_threshold,
        iou_threshold=settings.iou_threshold,
        device=settings.device,
        class_filter=settings.class_filter,
    )
    tracker = Tracker(
        tracker_name=settings.tracker_name,
        track_buffer=settings.track_buffer,
        match_thresh=settings.match_thresh,
        min_hits=settings.min_hits,
        device=settings.device,
    )

    with imageio.get_reader(video_path, format="ffmpeg") as reader:
        for frame_number, frame in enumerate(reader):
            if frame_number >= max_frames:
                break

            if frame is None:
                continue

            if frame.ndim == 4:
                frame = frame[:, :, :3]

            if frame.dtype != np.uint8:
                frame = np.clip(frame, 0, 255).astype(np.uint8)

            detections = detector.detect(
                frame,
                camera_id=Path(video_path).stem,
                frame_number=frame_number,
            )
            tracks = tracker.update(detections, frame)
            annotated = draw_tracks(frame, tracks)
            yield annotated, len(tracks), frame_number


def main() -> None:
    st.set_page_config(page_title="Crowd Management", layout="wide")
    st.title("Crowd Management — Streamlit Viewer")

    if "process_requested" not in st.session_state:
        st.session_state.process_requested = False
        st.session_state.video_path = ""
        st.session_state.confidence = 0.5
        st.session_state.fps = 10

    with st.sidebar:
        st.subheader("Upload a video")
        uploaded_file = st.file_uploader(
            "Upload video file",
            type=["mp4", "mov", "avi", "mkv"],
        )

        confidence = st.slider("Confidence threshold", 0.0, 1.0, st.session_state.confidence, 0.01)
        fps = st.slider("Target FPS", 1, 30, st.session_state.fps, 1)

        if st.button("Run detection"):
            if uploaded_file is None:
                st.warning("Upload a video file before running detection.")
            else:
                st.session_state.video_path = save_uploaded_video(uploaded_file)
                st.session_state.confidence = confidence
                st.session_state.fps = fps
                st.session_state.process_requested = True

    if not st.session_state.process_requested:
        st.info("Upload a video and press Run detection.")
        return

    settings = configure_settings(
        confidence=st.session_state.confidence,
        fps=st.session_state.fps,
    )

    progress_text = st.empty()
    image_placeholder = st.empty()
    frame_count = 0

    for annotated, people, frame_number in process_video(
        st.session_state.video_path,
        settings,
        max_frames=120,
    ):
        frame_count = frame_number + 1
        image_placeholder.image(
            annotated,
            caption=f"Frame {frame_number} — People detected: {people}",
            use_column_width=True,
        )
        progress_text.text(f"Processed {frame_count} frames")
        time.sleep(0.02)

    st.success(f"Video processing complete. Processed {frame_count} frames.")


if __name__ == "__main__":
    main()
