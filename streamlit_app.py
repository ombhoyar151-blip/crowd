import tempfile
import time
from pathlib import Path
from typing import Optional

import imageio
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from config.settings import Settings

try:
    from services.vision.detector import Detector
    from models.detection import Detection
    DETECTION_ENABLED = True
    DETECTION_IMPORT_ERROR = None
except Exception as exc:
    Detector = None
    Detection = None
    DETECTION_ENABLED = False
    DETECTION_IMPORT_ERROR = exc


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


def get_model_path(settings: Settings) -> Path:
    root_path = settings.project_root
    primary_path = root_path / settings.model_path
    if primary_path.exists():
        return primary_path

    fallback_path = root_path / settings.model_path.name
    if fallback_path.exists():
        return fallback_path

    raise FileNotFoundError(
        f"YOLO model not found. Checked {primary_path} and {fallback_path}."
    )


def load_detector(settings: Settings) -> Optional[Detector]:
    if not DETECTION_ENABLED:
        return None

    model_path = get_model_path(settings)
    return Detector(
        model_path=model_path,
        conf_threshold=settings.conf_threshold,
        iou_threshold=settings.iou_threshold,
        device=settings.device,
        class_filter=settings.class_filter,
    )


def draw_tracks(frame: np.ndarray, people_count: int) -> Image.Image:
    if frame.ndim == 4:
        frame = frame[:, :, :3]

    if frame.dtype != np.uint8:
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    image = Image.fromarray(frame)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    badge_text = f"People: {people_count}"
    draw.rectangle([10, 8, 240, 42], fill=(18, 92, 187, 230))
    draw.text((14, 12), badge_text, fill=(255, 255, 255), font=font)
    return image


def draw_detections(frame: np.ndarray, detections: list[Detection]) -> Image.Image:
    if frame.ndim == 4:
        frame = frame[:, :, :3]

    if frame.dtype != np.uint8:
        frame = np.clip(frame, 0, 255).astype(np.uint8)

    image = Image.fromarray(frame)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    for detection in detections:
        x1, y1, x2, y2 = map(int, detection.bbox)
        draw.rectangle([x1, y1, x2, y2], outline=(255, 51, 51), width=3)
        label = f"{detection.class_name} {detection.confidence:.2f}"
        draw.rectangle([x1, y1 - 20, x1 + len(label) * 7 + 14, y1], fill=(255, 51, 51))
        draw.text((x1 + 6, y1 - 18), label, fill=(255, 255, 255), font=font)

    people_count = len(detections)
    draw.rectangle([10, 8, 240, 42], fill=(18, 92, 187, 230))
    draw.text((14, 12), f"People: {people_count}", fill=(255, 255, 255), font=font)
    return image


def process_video(
    video_path: str,
    settings: Settings,
    detector: Optional[Detector] = None,
    max_frames: int = 120,
):
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

            if detector is not None:
                detections = detector.detect(
                    frame,
                    frame_number=frame_number,
                )
                annotated = draw_detections(frame, detections)
                people_count = len(detections)
            else:
                annotated = draw_tracks(frame, people_count=0)
                people_count = 0

            yield annotated, people_count, frame_number


def set_page_style() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: linear-gradient(180deg, #061923 0%, #0f2742 100%);
            color: #edf5ff;
        }
        .css-1d391kg {
            background-color: rgba(6, 25, 44, 0.95) !important;
        }
        .css-1d391kg [data-testid="stFileUploaderDropzone"] {
            background: rgba(255, 255, 255, 0.06) !important;
        }
        .css-1v0mbfj.e1fqkh3o3 {
            background: rgba(255, 255, 255, 0.08) !important;
        }
        .st-bc {
            color: #eef6ff !important;
        }
        .stButton>button {
            background: #2d7cff !important;
            color: white !important;
            border: none !important;
        }
        .stButton>button:hover {
            background: #1f5edd !important;
        }
        .metric-label {
            color: #b8d5ff !important;
        }
        .metric-value {
            color: #ffffff !important;
        }
        .reportview-container .main .block-container {
            padding-top: 20px;
            padding-right: 20px;
            padding-left: 20px;
            padding-bottom: 20px;
        }
        .card {
            padding: 20px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.14);
            box-shadow: 0 22px 45px rgba(0, 0, 0, 0.18);
        }
        .section-title {
            color: #ffffff;
            margin-bottom: 6px;
        }
        .section-subtitle {
            color: #a7c7ff;
            margin-top: 0;
        }
        .nav-pill {
            display: inline-block;
            margin-right: 10px;
            padding: 10px 18px;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.08);
            color: #c8daff;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }
        .nav-pill-active {
            background: #2a75ff;
            color: #ffffff;
            border-color: #2a75ff;
        }
        .small-note {
            color: #b8d5ff;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_navbar(selected: str) -> str:
    nav_items = ["Overview", "Live Feed", "Settings"]
    return st.radio(
        "Navigation",
        nav_items,
        index=nav_items.index(selected),
        horizontal=True,
    )


def main() -> None:
    st.set_page_config(
        page_title="Crowd Management Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    set_page_style()

    if "process_requested" not in st.session_state:
        st.session_state.process_requested = False
        st.session_state.video_path = ""
        st.session_state.confidence = 0.5
        st.session_state.fps = 10
        st.session_state.frame_count = 0

    if "nav" not in st.session_state:
        st.session_state.nav = "Overview"

    with st.sidebar:
        st.markdown("# Crowd Control Panel")
        st.markdown("#### Monitor crowd flow and manage detection settings in one place.")
        st.markdown("---")

        uploaded_file = st.file_uploader(
            "Upload surveillance video",
            type=["mp4", "mov", "avi", "mkv"],
        )
        st.markdown("---")

        st.markdown("## Detection Settings")
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
                st.warning("Please upload a video file before starting.")
            else:
                st.session_state.video_path = save_uploaded_video(uploaded_file)
                st.session_state.confidence = confidence
                st.session_state.fps = fps
                st.session_state.process_requested = True
                st.session_state.frame_count = 0
                st.session_state.nav = "Live Feed"

        if st.button("Reset"):
            st.session_state.process_requested = False
            st.session_state.video_path = ""
            st.session_state.frame_count = 0
            st.session_state.nav = "Overview"
            st.experimental_rerun()

        st.markdown("---")
        st.markdown(
            "<div class='card'><strong>Usage Notes</strong>"
            "<p class='small-note'>Upload a clean camera feed and choose a confidence value for reliable detection.</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div class='card'><h1 class='section-title'>Crowd Management Dashboard</h1>"
        "<p class='section-subtitle'>Visualize people detection, monitor density, and preview results in a crowd-control interface.</p></div>",
        unsafe_allow_html=True,
    )

    st.session_state.nav = render_navbar(st.session_state.nav)
    st.markdown("---")

    if st.session_state.nav == "Overview":
        top1, top2, top3, top4 = st.columns(4)
        top1.metric("Upload Status", "Ready")
        top2.metric("Confidence", f"{st.session_state.confidence:.0%}")
        top3.metric("FPS", st.session_state.fps)
        top4.metric("Frames", st.session_state.frame_count)

        st.markdown(
            "<div class='card'><h4>Operational Summary</h4>"
            "<p class='small-note'>Use the sidebar to upload a video and start detection. Live Feed will show annotated frames.</p></div>",
            unsafe_allow_html=True,
        )

        if st.session_state.process_requested:
            st.success("Detection ready. Switch to Live Feed to view the annotated stream.")
        else:
            st.info("No video uploaded yet. Upload a file to begin.")

    elif st.session_state.nav == "Live Feed":
        if not st.session_state.process_requested:
            st.warning("Please start detection from the sidebar to view live feed output.")
        else:
            left, right = st.columns([2, 1])
            with left:
                st.markdown("<div class='card'><h4>Live Detection Preview</h4></div>", unsafe_allow_html=True)
                    stream_placeholder = st.empty()
                status_placeholder = st.empty()

                settings = configure_settings(
                    confidence=st.session_state.confidence,
                    fps=st.session_state.fps,
                )
                detector = None
                if DETECTION_ENABLED:
                    try:
                        detector = load_detector(settings)
                    except Exception as exc:
                        st.error(f"Detection model error: {exc}")
                        return
                else:
                    st.error(
                        "Detection dependencies are not installed. Install ultralytics to enable people detection."
                    )
                    return

                for annotated, people, frame_number in process_video(
                    st.session_state.video_path,
                    settings,
                    detector=detector,
                ):
                    st.session_state.frame_count = frame_number + 1
                    stream_placeholder.image(
                        annotated,
                        caption=f"Frame {frame_number + 1} — People detected: {people}",
                        use_column_width=True,
                    )
                    status_placeholder.markdown(
                        f"<p class='small-note'>Processing frame {frame_number + 1} / 120</p>",
                        unsafe_allow_html=True,
                    )
                    time.sleep(0.02)
                st.success(f"Preview complete — {st.session_state.frame_count} frames processed.")
            with right:
                st.markdown("<div class='card'><h4>Current Settings</h4>"
                            f"<p class='small-note'>Confidence: {st.session_state.confidence:.2f}<br>FPS: {st.session_state.fps}</p></div>",
                            unsafe_allow_html=True)
                st.markdown("<div class='card'><h4>Detection Notes</h4>"
                            "<p class='small-note'>This preview uses a local video file. For a production crowd management system, connect to live camera feeds.</p></div>",
                            unsafe_allow_html=True)

    else:
        st.markdown("<div class='card'><h4>Settings</h4>"
                    "<p class='small-note'>Adjust detection confidence and frame rate in the sidebar.</p></div>",
                    unsafe_allow_html=True)

        st.markdown("<div class='card'><h4>System Info</h4>"
                    "<p class='small-note'>This Streamlit app is a preview interface created for crowd management video review.</p></div>",
                    unsafe_allow_html=True)


if __name__ == "__main__":
    main()
