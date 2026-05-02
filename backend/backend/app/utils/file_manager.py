from fastapi import UploadFile
from pathlib import Path
import shutil
from typing import Optional


BASE = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE / "uploads"
OUTPUT_DIR = BASE / "outputs"


def save_upload_file(upload_file: UploadFile, name_prefix: str) -> str:
    ext = Path(upload_file.filename).suffix or ""
    path = UPLOAD_DIR / f"{name_prefix}{ext}"
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    return str(path)


def unique_output_path(base: Path, filename: str) -> str:
    base.mkdir(parents=True, exist_ok=True)
    path = base / filename
    return str(path)
