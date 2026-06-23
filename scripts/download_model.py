import logging
from pathlib import Path

from ultralytics import YOLO

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
DEFAULT_MODEL = "yolo11n.pt"


def download_model(model_name: str = DEFAULT_MODEL) -> Path:
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODELS_DIR / model_name

    if model_path.exists():
        logger.info("Model already exists at %s", model_path)
        return model_path

    logger.info("Downloading model %s ...", model_name)
    model = YOLO(model_name)
    model.save(str(model_path))
    logger.info("Model saved to %s", model_path)
    return model_path


if __name__ == "__main__":
    download_model()
