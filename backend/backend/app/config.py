from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
TEMP_DIR = BASE_DIR / "tmp"

DEFAULT_FUSION_WEIGHT_RGB = 0.7
DEFAULT_FUSION_WEIGHT_THERMAL = 0.3

ORB_MAX_FEATURES = 5000
MIN_MATCH_COUNT = 10

VIDEO_FPS = 15
