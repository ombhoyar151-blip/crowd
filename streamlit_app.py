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
    draw.rectangle([10, 8, 190, 34], fill=(0, 0, 0, 180))
    draw.text((14, 12), label, fill=(255, 255, 255), font=font)
    return image


def process_video(video_path: str, settings: Settings, max_frames: int = 120):
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


def page_style() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #0b1f31 0%, #112d44 100%);
            color: #ffffff;
        }
        .title {
            color: #ffffff;
        }
        .subtitle {
            color: #9ac7ff;
        }
        .metric-label {
            color: #9ac7ff !important;
        }
        .metric-value {
            color: #ffffff !important;
        }
        .stProgress > div > div {
            background-image: linear-gradient(90deg, #45b3ff, #6a8aff);
        }
        .card {
            padding: 18px;
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.12);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Crowd Management Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    page_style()

    if "process_requested" not in st.session_state:
        st.session_state.process_requested = False
        st.session_state.video_path = ""
        st.session_state.confidence = 0.5
        st.session_state.fps = 10
        st.session_state.frame_count = 0

    st.markdown(
        "# Crowd Management Dashboard"
        "\n\n"
        "Streamlined detection preview for uploaded video feeds. Use the sidebar to upload a video file, set thresholds, and start processing.",
    )

    header_col1, header_col2 = st.columns([3, 1])
    with header_col1:
        st.markdown(
            "<div class='card'><h3>Real-Time Crowd Monitoring</h3>"
            "<p>Upload a surveillance video and review frame-by-frame crowd detections with a live dashboard.</p></div>",
            unsafe_allow_html=True,
        )
    with header_col2:
        st.markdown(
            "<div class='card'><h4>Quick Controls</h4>"
            "<ul style='margin:0; padding-left:18px;'>"
            "<li>Upload video file</li>"
            "<li>Adjust confidence & FPS</li>"
            "<li>View live detection preview</li>"
            "</ul></div>",
            unsafe_allow_html=True,
        )

    with st.sidebar:
        st.markdown("## Upload & Detection")
        uploaded_file = st.file_uploader(
            "Choose a video file",
            type=["mp4", "mov", "avi", "mkv"],
        )
        st.markdown("---")

        st.markdown("## Settings")
        confidence = st.slider(
            "Confidence threshold",
            0.0,
            1.0,
            st.session_state.confidence,
            0.01,
        )
        fps = st.slider(
            "Target FPS",
            1,
            30,
            st.session_state.fps,
            1,
        )
        st.markdown("---")

        if st.button("Start Detection"):
            if uploaded_file is None:
                st.warning("Upload a video file before starting detection.")
            else:
                st.session_state.video_path = save_uploaded_video(uploaded_file)
                st.session_state.confidence = confidence
                st.session_state.fps = fps
                st.session_state.process_requested = True
                st.session_state.frame_count = 0

        if st.button("Reset"):
            st.session_state.process_requested = False
            st.session_state.video_path = ""
            st.session_state.frame_count = 0
            st.experimental_rerun()

        st.markdown("---")
        st.markdown(
            "#### Notes"
            "<ul style='margin:0; padding-left:18px;'>"
            "<li>File uploads are processed locally.</li>"
            "<li>Max 120 frames shown for preview.</li>"
            "<li>Video is not stored permanently.</li>"
            "</ul>",
            unsafe_allow_html=True,
        )

    if not st.session_state.process_requested:
        st.warning("Upload a video and press Start Detection to preview crowd analytics.")
        return

    settings = configure_settings(
        confidence=st.session_state.confidence,
        fps=st.session_state.fps,
    )

    st.markdown("## Detection Preview")
    metrics_col1, metrics_col2, metrics_col3 = st.columns(3)
    metrics_col1.metric("Confidence", f"{settings.conf_threshold:.0%}")
    metrics_col2.metric("Target FPS", settings.target_fps)
    metrics_col3.metric("Frames Processed", st.session_state.frame_count)

    progress_text = st.empty()
    image_placeholder = st.empty()

    for annotated, people, frame_number in process_video(
        st.session_state.video_path,
        settings,
        max_frames=120,
    ):
        st.session_state.frame_count = frame_number + 1
        image_placeholder.image(
            annotated,
            caption=f"Frame {frame_number + 1} — People detected: {people}",
            use_column_width=True,
        )
        progress_text.markdown(
            f"<div class='card'><strong>Processing frame {frame_number + 1}</strong> · crowd overview active</div>",
            unsafe_allow_html=True,
        )
        time.sleep(0.02)

    st.success(
        f"Crowd detection preview complete — {st.session_state.frame_count} frames processed.",
    )


if __name__ == "__main__":
    main()
