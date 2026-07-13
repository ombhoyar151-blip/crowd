import os
import queue
import tempfile
import threading
import time
from pathlib import Path

import cv2
import numpy as np
import streamlit as st

from config.settings import Settings
from services.vision.pipeline import Pipeline

FRAME_QUEUE_MAX = 1


def init_session_state() -> None:
    if "pipeline" not in st.session_state:
        st.session_state.pipeline = None
    if "frame_queue" not in st.session_state:
        st.session_state.frame_queue = queue.Queue(maxsize=FRAME_QUEUE_MAX)
    if "stop_event" not in st.session_state:
        st.session_state.stop_event = None
    if "thread" not in st.session_state:
        st.session_state.thread = None
    if "running" not in st.session_state:
        st.session_state.running = False
    if "video_path" not in st.session_state:
        st.session_state.video_path = ""


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
    # Use a smaller display size so Streamlit stays responsive.
    settings.frame_width = 960
    settings.frame_height = 540
    return settings


def stop_pipeline() -> None:
    if st.session_state.stop_event is not None:
        st.session_state.stop_event.set()
    if st.session_state.thread is not None and st.session_state.thread.is_alive():
        st.session_state.thread.join(timeout=5)
    st.session_state.pipeline = None
    st.session_state.thread = None
    st.session_state.stop_event = None
    st.session_state.running = False


def pipeline_callback(frame: np.ndarray, track_batch) -> None:
    try:
        if st.session_state.frame_queue.full():
            _ = st.session_state.frame_queue.get_nowait()
    except queue.Empty:
        pass

    st.session_state.frame_queue.put(
        {
            "frame": frame.copy(),
            "people": track_batch.person_count,
            "frame_number": track_batch.frame_number,
        }
    )


def run_pipeline(settings: Settings) -> None:
    pipeline = Pipeline(settings)
    pipeline.initialize()
    pipeline.set_callback(pipeline_callback)
    st.session_state.pipeline = pipeline
    st.session_state.stop_event = threading.Event()
    pipeline.run(stop_event=st.session_state.stop_event)


def main() -> None:
    st.set_page_config(page_title="Crowd Management", layout="wide")
    st.title("Crowd Management — Streamlit Viewer")

    init_session_state()

    with st.sidebar:
        st.subheader("Stream settings")
        source = st.selectbox(
            "Video source",
            ["file", "rtsp", "webcam"],
            index=0,
        )

        video_path = ""
        rtsp_url = ""
        webcam_id = 0

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
            rtsp_url = st.text_input("RTSP URL", value=st.session_state.get("rtsp_url", ""))
            st.session_state.rtsp_url = rtsp_url

        else:
            webcam_id = st.number_input(
                "Webcam ID",
                min_value=0,
                value=st.session_state.get("webcam_id", 0),
                step=1,
            )
            st.session_state.webcam_id = webcam_id

        confidence = st.slider("Confidence threshold", 0.0, 1.0, 0.5, 0.01)
        fps = st.slider("Target FPS", 1, 30, 10)

        if st.button("Start"):
            if source == "file" and not video_path:
                st.warning("Upload a video file before starting.")
            elif source == "rtsp" and not rtsp_url:
                st.warning("Enter an RTSP URL before starting.")
            else:
                st.session_state.running = True
                st.session_state.settings = configure_settings(
                    source=source,
                    video_path=video_path,
                    rtsp_url=rtsp_url,
                    webcam_id=webcam_id,
                    confidence=confidence,
                    fps=fps,
                )

        if st.button("Stop"):
            stop_pipeline()
            st.success("Pipeline stopped")

    if st.session_state.running:
        if st.session_state.pipeline is None or not (
            st.session_state.thread and st.session_state.thread.is_alive()
        ):
            if st.session_state.get("settings") is not None:
                st.session_state.frame_queue = queue.Queue(maxsize=FRAME_QUEUE_MAX)
                thread = threading.Thread(
                    target=run_pipeline,
                    args=(st.session_state.settings,),
                    daemon=True,
                )
                st.session_state.thread = thread
                thread.start()
                time.sleep(1)

        st.subheader("Live detection")
        image_placeholder = st.empty()
        metric_cols = st.columns(3)
        metric_cols[0].metric("Running", "Yes")
        metric_cols[1].metric("Frames queued", st.session_state.frame_queue.qsize())
        metric_cols[2].metric(
            "Pipeline thread",
            "alive" if st.session_state.thread and st.session_state.thread.is_alive() else "stopped",
        )

        while st.session_state.running and st.session_state.thread and st.session_state.thread.is_alive():
            try:
                item = st.session_state.frame_queue.get(timeout=1.0)
            except queue.Empty:
                time.sleep(0.1)
                continue

            frame = item["frame"]
            people = item["people"]
            frame_number = item["frame_number"]

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image_placeholder.image(
                frame_rgb,
                caption=f"Frame {frame_number} — People detected: {people}",
                use_column_width=True,
            )
            time.sleep(0.01)

        if not st.session_state.thread or not st.session_state.thread.is_alive():
            st.warning("Pipeline has stopped. Press Start again to restart.")

    else:
        st.info("Use the sidebar to select a source and start the pipeline.")


if __name__ == "__main__":
    main()
