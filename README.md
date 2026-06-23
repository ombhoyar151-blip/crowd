# Crowd — AI-Powered Real-Time Crowd Management

## Phase 1: Video Ingestion & Person Detection

Ingests video streams (file / RTSP / webcam) and detects people using YOLOv11.

### Quick Start

```bash
pip install -r requirements.txt
python scripts/download_model.py
python scripts/run_pipeline.py --source file --video-path sample.mp4 --show
```

### Configuration

Edit `config/settings.py` or set env vars (see `.env.example`).

### Project Structure

```
config/settings.py          # Pydantic-settings config
config/cameras.yaml         # Camera definitions
models/detection.py         # Shared Pydantic schemas
services/vision/ingestion.py    # Threaded OpenCV reader
services/vision/detector.py     # YOLOv11 wrapper
services/vision/frame_processor.py  # Orchestrator
scripts/download_model.py   # Download YOLOv11 weights
scripts/run_pipeline.py     # CLI entry point
```

### Tests

```bash
pytest tests/ -v
```
