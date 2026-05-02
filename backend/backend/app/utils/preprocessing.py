import numpy as np
import cv2
from fastapi import UploadFile
from typing import Tuple


def read_upload_image(file: UploadFile) -> np.ndarray:
    data = file.file.read()
    arr = np.frombuffer(data, dtype='uint8')
    img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)
    if img is None:
        raise ValueError("Cannot read image")
    # convert BGR to RGB if color
    if img.ndim == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img


def ensure_rgb(img: np.ndarray) -> np.ndarray:
    if img.ndim == 2:
        return cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
    return img
