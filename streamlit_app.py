import os
import queue
import tempfile
import threading
import time
from pathlib import Path

import imageio
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

from config.settings import Settings

FRAME_QUEUE_MAX = 4


def init_session_state() -> None:
    if "running" not in st.session_state:
        st.session_state.running = False
    if "frame_queue" not in st.session_state:
        st.session_state.frame_queue = queue.Queue(maxsize=FRAME_QUEUE_MAX)
    if "stop_event" not in st.session_state:
        st.session_state.stop_event = None
    if "thread" not in st.session_state:
        st.session_state.thread = None
    if "video_path" not in st.session_state:
        st.session_state.video_path = ""
    if "rtsp_url" not in st.session_state:
        st.session_state.rtsp_url = ""
    if "webcam_id" not in st.session_state:
        st.session_state.webcam_id = 0
    if "source" not in st.session_state:
        st.session_state.source = "file"
    if "confidence" not in st.session_state:
        st.session_state.confidence = 0.5
    if "fps" not in st.session_state:
        st.session_state.fps = 10


def save_uploaded_video(uploaded_file: st.uploaded_file_manager.UploadedFile) -> str:
    temp_dir = Path(tempfile.gettempdir())
    target_path = temp_dir / uploaded_file.name
    with open(target_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(target_path)


def configure_settings(
    source: str,
    video_path: str,
    rtsp_url: str,
    webcam_id: int,
    confidence: float,
    fps: int,
) -> Settings:
    settings = Settings()
    settings.video_source = source
    settings.video_path = video_path
    settings.rtsp_url = rtsp_url
    settings.webcam_id = webcam_id
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


def process_video(video_path: str, settings: Settings):
    try:
        reader = imageio.get_reader(video_path, format="ffmpeg")
    except Exception:
        return

    with reader:
        for frame_number, frame in enumerate(reader):
            if st.session_state.stop_event and st.session_state.stop_event.is_set():
                break

            if frame is None:
                continue

            if frame.ndim == 4:
                frame = frame[:, :, :3]

            if frame.dtype != np.uint8:
                frame = np.clip(frame, 0, 255).astype(np.uint8)

            annotated = draw_tracks(frame, people_count=0)
            try:
                if st.session_state.frame_queue.full():
                    _ = st.session_state.frame_queue.get_nowait()
                st.session_state.frame_queue.put(
                    {
                        "frame": annotated,
                        "people": 0,
                        "frame_number": frame_number,
                    },
                    block=False,
                )
            except queue.Full:
                continue

            time.sleep(1.0 / max(settings.target_fps, 1))

    st.session_state.running = False


def stop_processing() -> None:
    if st.session_state.stop_event is not None:
        st.session_state.stop_event.set()
    if st.session_state.thread is not None and st.session_state.thread.is_alive():
        st.session_state.thread.join(timeout=5)
    st.session_state.running = False
    st.session_state.thread = None
    st.session_state.stop_event = None


def start_processing(settings: Settings) -> None:
    if st.session_state.running:
        return

    st.session_state.running = True
    st.session_state.stop_event = threading.Event()
    st.session_state.frame_queue = queue.Queue(maxsize=FRAME_QUEUE_MAX)

    def worker():
        process_video(settings.video_path, settings)

    thread = threading.Thread(target=worker, daemon=True)
    st.session_state.thread = thread
    thread.start()


def main() -> None:
    st.set_page_config(page_title="Crowd Management", layout="wide")
    st.title("Crowd Management — Streamlit Viewer")

    init_session_state()

    with st.sidebar:
        st.subheader("Stream settings")
        source = st.selectbox(
            "Video source",
            ["file", "rtsp", "webcam"],
            index=["file", "rtsp", "webcam"].index(st.session_state.source),
        )
        st.session_state.source = source

        video_path = ""
        rtsp_url = st.session_state.rtsp_url
        webcam_id = st.session_state.webcam_id

        if source == "file":
            uploaded_file = st.file_uploader(
                "Upload video file",
                type=["mp4", "mov", "avi", "mkv"],
            )
            if uploaded_file is not None:
                video_path = save_uploaded_video(uploaded_file)
                st.success("Saved uploaded video for processing")
                st.session_state.video_path = video_path
            elif st.session_state.video_path:
                video_path = st.session_state.video_path

        elif source == "rtsp":
            rtsp_url = st.text_input("RTSP URL", value=rtsp_url)
            st.session_state.rtsp_url = rtsp_url
            st.warning("RTSP playback may not be available in Streamlit Cloud.")

        else:
            webcam_id = st.number_input(
                "Webcam ID",
                min_value=0,
                value=webcam_id,
                step=1,
            )
            st.session_state.webcam_id = webcam_id
            st.warning("Webcam input is not supported in deployed Streamlit apps.")

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
        st.session_state.confidence = confidence
        st.session_state.fps = fps

        if st.button("Start"):
            if source == "file" and not video_path:
                st.warning("Upload a video file before starting.")
            elif source == "rtsp" and not rtsp_url:
                st.warning("Enter an RTSP URL before starting.")
            else:
                settings = configure_settings(
                    source=source,
                    video_path=video_path,
                    rtsp_url=rtsp_url,
                    webcam_id=webcam_id,
                    confidence=confidence,
                    fps=fps,
                )
                start_processing(settings)

        if st.button("Stop"):
            stop_processing()
            st.success("Processing stopped.")

    if st.session_state.running:
        st.subheader("Live detection")
        status_cols = st.columns(3)
        status_cols[0].metric("Running", "Yes")
        status_cols[1].metric("Queue size", st.session_state.frame_queue.qsize())
        status_cols[2].metric(
            "Thread",
            "alive" if st.session_state.thread and st.session_state.thread.is_alive() else "stopped",
        )

        output_placeholder = st.empty()
        while st.session_state.running:
            try:
                item = st.session_state.frame_queue.get(timeout=1.0)
            except queue.Empty:
                time.sleep(0.1)
                continue

            frame = item["frame"]
            people = item["people"]
            frame_number = item["frame_number"]
            output_placeholder.image(
                frame,
                caption=f"Frame {frame_number} — People detected: {people}",
                use_column_width=True,
            )
            time.sleep(0.01)

        st.warning("Processing has stopped.")

    else:
        st.info("Use the sidebar to choose a source and press Start.")


if __name__ == "__main__":
    main()
