import tempfile
import time
from pathlib import Path

import imageio
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from config.settings import Settings


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


def draw_tracks(frame: np.ndarray, people_count: int) -> Image.Image:
    if frame.ndim == 4:
        frame = frame[:, :, :3]

    if frame.dtype != np.uint8:
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    image = Image.fromarray(frame)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    label = f"People: {people_count}"
    draw.text((12, 12), label, fill=(255, 255, 0), font=font)
    return image


def process_video(video_path: str, settings: Settings, max_frames: int = 100):
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

            annotated = draw_tracks(frame, people_count=0)
            yield annotated, 0, frame_number


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
